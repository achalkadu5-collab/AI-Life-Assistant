import sqlite3

# ==========================================
# Database Configuration
# ==========================================

DATABASE_NAME = "ai_life_assistant.db"


# ==========================================
# Get Database Connection
# ==========================================

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    return connection


# ==========================================
# Create Database Tables
# ==========================================

def create_table():

    connection = get_connection()
    cursor = connection.cursor()

    # ======================================
    # Memories Table
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            memory TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ======================================
    # Conversations Table
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # ======================================
    # Users Table
    # ======================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# ==========================================
# Save Conversation Message
# ==========================================

def save_message(user_id, role, message):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversations
        (user_id, role, message)
        VALUES (?, ?, ?)
        """,
        (user_id, role, message)
    )

    connection.commit()
    connection.close()


# ==========================================
# Get Conversation History
# ==========================================

def get_conversation_history(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT role, message
        FROM conversations
        WHERE user_id = ?
        ORDER BY id ASC
        """,
        (user_id,)
    )

    conversations = cursor.fetchall()

    connection.close()

    return conversations


# ==========================================
# Create New User
# ==========================================

def create_user(username, email, password_hash):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO users
        (username, email, password_hash)
        VALUES (?, ?, ?)
        """,
        (username, email, password_hash)
    )

    connection.commit()

    user_id = cursor.lastrowid

    connection.close()

    return user_id


# ==========================================
# Get User By Email
# ==========================================

def get_user_by_email(email):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, username, email, password_hash
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    return user


# ==========================================
# Initialize Database
# ==========================================

create_table()