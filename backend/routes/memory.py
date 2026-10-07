from fastapi import APIRouter, HTTPException, Depends
from backend.dependencies import get_current_user
from pydantic import BaseModel

from backend.database import get_connection


# ==========================================
# Memory Router
# ==========================================

router = APIRouter(
    prefix="/memory",
    tags=["Memory"]
)


# ==========================================
# Memory Request Model
# ==========================================

class MemoryRequest(BaseModel):
    user_id: str
    memory: str


# ==========================================
# Save Memory
# ==========================================

@router.post("/save")
def save_memory(
    request: MemoryRequest,
    current_user: dict = Depends(get_current_user)
):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO memories (user_id, memory)
            VALUES (?, ?)
            """,
            (
            str(current_user["user_id"]),
                request.memory
            )
        )

        connection.commit()

        memory_id = cursor.lastrowid

        connection.close()

        return {
            "message": "Memory saved successfully.",
            "memory_id": memory_id,
            "user_id": str(current_user["user_id"]),
            "memory": request.memory
        }

    except Exception as e:

        print("SAVE MEMORY ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while saving memory."
        )


# ==========================================
# Get User Memories
# ==========================================

@router.get("/list")
def list_memories(
    current_user: dict = Depends(get_current_user)
):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, memory, created_at
            FROM memories
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (str(current_user["user_id"]),)
        )

        memories = cursor.fetchall()

        connection.close()

        result = []

        for memory in memories:

            result.append({
                "id": memory[0],
                "memory": memory[1],
                "created_at": memory[2]
            })

        return {
            "user_id": str(current_user["user_id"]),
            "memories": result
        }

    except Exception as e:

        print("GET MEMORY ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while loading memories."
        )


# ==========================================
# Delete Memory
# ==========================================

@router.delete("/delete/{memory_id}")
def delete_memory(
    memory_id: int,
    current_user: dict = Depends(get_current_user)
):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        user_id = str(current_user["user_id"])

        # Check if memory belongs to current user
        cursor.execute(
            """
            SELECT id
            FROM memories
            WHERE id = ? AND user_id = ?
            """,
            (memory_id, user_id)
        )

        memory = cursor.fetchone()

        if not memory:
            conn.close()
            raise HTTPException(
                status_code=404,
                detail="Memory not found."
            )

        # Delete memory
        cursor.execute(
            """
            DELETE FROM memories
            WHERE id = ? AND user_id = ?
            """,
            (memory_id, user_id)
        )

        conn.commit()
        conn.close()

        return {
            "message": "Memory deleted successfully.",
            "memory_id": memory_id,
            "user_id": user_id
        }

    except HTTPException:
        raise

    except Exception as e:
        print(
            "DELETE MEMORY ERROR:",
            repr(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"DELETE MEMORY ERROR: {repr(e)}"
        )

# =========================================================
# EDIT MEMORY
# =========================================================

@router.put("/edit/{memory_id}")
def edit_memory(
    memory_id: int,
    memory: str,
    current_user: dict = Depends(get_current_user)
):

    try:

        connection = get_connection()
        cursor = connection.cursor()

        # Check memory belongs to this user
        cursor.execute(
            """
            SELECT id
            FROM memories
            WHERE id = ? AND user_id = ?
            """,
            (memory_id, str(current_user["user_id"]))
        )

        existing_memory = cursor.fetchone()

        if existing_memory is None:

            connection.close()

            raise HTTPException(
                status_code=404,
                detail="Memory not found or does not belong to this user."
            )

        # Update memory
        cursor.execute(
            """
            UPDATE memories
            SET memory = ?
            WHERE id = ? AND user_id = ?
            """,
            (
                memory,
                memory_id,
                str(current_user["user_id"])
            )
        )

        connection.commit()
        connection.close()

        return {
            "message": "Memory updated successfully.",
            "memory_id": memory_id,
            "user_id": str(current_user["user_id"]),
            "memory": memory
        }

    except HTTPException:

        raise

    except Exception as e:

        print(
            "EDIT MEMORY ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while editing memory."
        )
# =========================================================
# SEARCH MEMORY
# =========================================================

@router.get("/search")
def search_memory(
    user_id: str,
    keyword: str,
    current_user: dict = Depends(get_current_user)
):
    try:
        if str(current_user["user_id"]) != str(user_id):
            raise HTTPException(
                status_code=403,
                detail="You can only access your own memories."
            )
        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, memory, created_at
            FROM memories
            WHERE user_id = ?
            AND memory LIKE ?
            ORDER BY id DESC
            """,
            (
                str(current_user["user_id"]),
                f"%{keyword}%"
            )
        )

        memories = cursor.fetchall()

        connection.close()

        result = []

        for memory in memories:

            result.append({
                "id": memory[0],
                "memory": memory[1],
                "created_at": memory[2]
            })

        return {
            "user_id": str(current_user["user_id"]),
            "keyword": keyword,
            "memories": result
        }

    except Exception as e:

        print(
            "SEARCH MEMORY ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail="Something went wrong while searching memories."
        )