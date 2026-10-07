from fastapi import APIRouter, HTTPException, Depends
from backend.dependencies import get_current_user

from backend.models.chat import ChatRequest, ChatResponse

from backend.database import (
    save_message,
    get_conversation_history,
    get_connection
)

import os
import time
from dotenv import load_dotenv
from google import genai


# Load .env file
load_dotenv()


# Create router
router = APIRouter()


# Gemini client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# =========================================================
# CHAT ENDPOINT
# =========================================================

@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):

    try:

        print("CHAT STARTED")

        # Get actual user ID
        user_id = str(current_user["user_id"])

        print("USER ID:", user_id)

        # -------------------------------------------------
        # Save user message
        # -------------------------------------------------

        save_message(
            user_id,
            "User",
            request.message
        )

        print("USER MESSAGE SAVED")

        # -------------------------------------------------
        # Automatic Memory Detection
        # -------------------------------------------------

        message_lower = request.message.lower().strip()

        memory_keywords = [
            "remember that",
            "remember this",
            "remember my",
            "don't forget that",
            "dont forget that",
            "please remember"
        ]

        should_save_memory = False

        for keyword in memory_keywords:

            if keyword in message_lower:
                should_save_memory = True
                break

        if should_save_memory:

            memory_text = request.message.strip()

            # Remove common memory phrases
            prefixes = [
                "remember that",
                "remember this",
                "remember my",
                "don't forget that",
                "dont forget that",
                "please remember"
            ]

            for prefix in prefixes:

                if memory_text.lower().startswith(prefix):

                    memory_text = memory_text[len(prefix):].strip()
                    break

            # Save memory only if text exists
            if memory_text:

                connection = get_connection()
                cursor = connection.cursor()

                cursor.execute(
                    """
                    INSERT INTO memories (user_id, memory)
                    VALUES (?, ?)
                    """,
                    (
                        user_id,
                        memory_text
                    )
                )

                connection.commit()

                memory_id = cursor.lastrowid

                connection.close()

                print(
                    "MEMORY SAVED AUTOMATICALLY:",
                    memory_id,
                    memory_text
                )

        # -------------------------------------------------
        # Get conversation history
        # -------------------------------------------------

        history = get_conversation_history(user_id)

        print("HISTORY:", history)

        # -------------------------------------------------
        # Get saved memories
        # -------------------------------------------------

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT memory
            FROM memories
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,)
        )

        memory_rows = cursor.fetchall()

        connection.close()

        memories = []

        for row in memory_rows:
            memories.append(row[0])

        print("MEMORIES:", memories)

        # -------------------------------------------------
        # Convert history into text
        # -------------------------------------------------

        conversation = ""

        for role, message in history:

            conversation += f"{role}: {message}\n"

        # -------------------------------------------------
        # Create prompt for Gemini
        # -------------------------------------------------

        prompt = f"""
You are AI Life Assistant.

You are a helpful, friendly and intelligent personal AI assistant.

Use the conversation history and saved memories below to understand
the user's context.

Conversation History:
{conversation}

Saved Memories:
{memories}

Latest User Message:
{request.message}

Important instructions:

1. Use saved memories when they are relevant.
2. Do not mention the database or memory system to the user.
3. Answer naturally and personally.
4. If the user asked you to remember something, confirm that you remember it.
5. Do not invent memories that are not provided.

Give a helpful and relevant answer.
"""

        print("SENDING REQUEST TO GEMINI")

        # -------------------------------------------------
        # Gemini response with fallback models
        # -------------------------------------------------

        models = [
            "gemini-3.6-flash",
            "gemini-3.5-flash",
            "gemini-3.5-flash-lite"
        ]

        response = None
        last_error = None

        for model_name in models:

            try:

                print("TRYING MODEL:", model_name)

                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )

                print(
                    "SUCCESS WITH MODEL:",
                    model_name
                )

                break

            except Exception as e:

                last_error = e

                print(
                    "MODEL ERROR:",
                    model_name,
                    repr(e)
                )

                time.sleep(1)

        # -------------------------------------------------
        # Check if all models failed
        # -------------------------------------------------

        if response is None:

            print(
                "ALL GEMINI MODELS FAILED:",
                repr(last_error)
            )

            raise HTTPException(
                status_code=503,
                detail="Gemini AI is temporarily unavailable. Please try again later."
            )

        # -------------------------------------------------
        # Get AI reply
        # -------------------------------------------------

        reply = response.text

        print("AI RESPONSE:", reply)

        # -------------------------------------------------
        # Save AI response
        # -------------------------------------------------

        save_message(
            user_id,
            "AI",
            reply
        )

        print("AI RESPONSE SAVED")

        # -------------------------------------------------
        # Return response
        # -------------------------------------------------

        return ChatResponse(
            reply=reply
        )

    except HTTPException:

        raise

    except Exception as e:

        print(
            "CHAT ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while processing your request."
        )


# =========================================================
# CHAT HISTORY ENDPOINT
# =========================================================

@router.get("/chat/history")
def chat_history( current_user: dict = Depends(get_current_user)):

    try:

        print(
            "HISTORY REQUEST FOR:",
            str(current_user["user_id"]),
        )

        # Get conversation history
        conversations = get_conversation_history(str(current_user["user_id"]))

        # Format history
        history = []

        for role, message in conversations:

            history.append({
                "role": role,
                "message": message
            })

        return {
            "user_id": str(current_user["user_id"]),
            "history": history
        }

    except Exception as e:

        print(
            "HISTORY ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while loading chat history."
        )