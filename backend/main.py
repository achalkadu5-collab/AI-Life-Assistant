from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends

from backend.dependencies import get_current_user

from backend.database import create_table
from backend.routes.chat import router as chat_router
from backend.routes.auth import router as auth_router
from backend.routes.memory import router as memory_router

app = FastAPI(
    title="AI Life Assistant API",
    description="AI-powered personal life assistant",
    version="1.0.0"
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Create Database Tables
# =========================

create_table()


# =========================
# Include Routers
# =========================

app.include_router(chat_router)
app.include_router(auth_router)
app.include_router(memory_router)

# =========================
# Home
# =========================

@app.get("/")
def home():

    return {
        "message": "AI Life Assistant API is running"
    }


# =========================
# About
# =========================

@app.get("/about")
def about():

    return {
        "project": "AI Life Assistant",
        "version": "1.0"
    }

@app.get("/protected")
def protected_route(
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "You accessed a protected route.",
        "user": current_user
    }