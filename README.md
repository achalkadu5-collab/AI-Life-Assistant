# AI Life Assistant

## Project Overview

AI Life Assistant is an AI-powered personal assistant that helps users
interact with an AI, store personal memories, manage conversation history,
and access their information securely.

The application uses JWT authentication so that each user can securely
access only their own chats and memories.

## Features

- User Registration
- User Login
- JWT Authentication
- AI Chat using Google Gemini API
- Chat History
- Automatic Memory Saving
- Add Memory
- Edit Memory
- Delete Memory
- Search Memory
- User Profile
- Dashboard
- Protected API Routes
- Secure User-specific Data Access

## Technologies Used

### Backend
- Python
- FastAPI
- SQLite
- Google Gemini API
- JWT Authentication
- Passlib / bcrypt

### Frontend
- HTML
- CSS
- JavaScript

### Development Tools
- Visual Studio Code
- Swagger UI
- Git
- GitHub

## Project Structure

```text
AI-Life-assistant/
│
├── backend/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   └── memory.py
│   │
│   ├── models/
│   │   └── chat.py
│   │
│   ├── database.py
│   ├── dependencies.py
│   ├── jwt_utils.py
│   └── main.py
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   └── register.html
│
├── ai_life_assistant.db
├── README.md
└── requirements.txt