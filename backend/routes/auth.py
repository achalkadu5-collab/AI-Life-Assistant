from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext

from backend.database import create_user, get_user_by_email
from backend.jwt_utils import create_access_token


# ==========================================
# Authentication Router
# ==========================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# ==========================================
# Password Hashing
# ==========================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# ==========================================
# Register Request Model
# ==========================================

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str


# ==========================================
# Login Request Model
# ==========================================

class LoginRequest(BaseModel):
    email: str
    password: str


# ==========================================
# Register API
# ==========================================

@router.post("/register")
def register(request: RegisterRequest):

    try:

        print("REGISTER STARTED")

        # Check existing user
        existing_user = get_user_by_email(request.email)

        print("CHECK USER:", existing_user)

        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered."
            )

        # Hash password
        password_hash = pwd_context.hash(request.password)

        print("PASSWORD HASHED")

        # Create user
        user_id = create_user(
            request.username,
            request.email,
            password_hash
        )

        print("USER CREATED:", user_id)

        return {
            "message": "User registered successfully.",
            "user_id": user_id,
            "username": request.username
        }

    except HTTPException:
        raise

    except Exception as e:

        print("REGISTER ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=f"REGISTER ERROR: {repr(e)}"
        )


# ==========================================
# Login API
# ==========================================

@router.post("/login")
def login(request: LoginRequest):
    try:
        print("LOGIN STARTED")

        user = get_user_by_email(request.email)

        print("LOGIN USER:", user)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password."
            )

        password_correct = pwd_context.verify(
            request.password,
            user[3]
        )

        if not password_correct:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password."
            )

        access_token = create_access_token(
            {
                "user_id": user[0],
                "username": user[1],
                "email": user[2]
            }
        )

        print("LOGIN SUCCESS")

        return {
            "message": "Login successful.",
            "access_token": access_token,
            "user_id": user[0],
            "username": user[1],
            "email": user[2]
        }

    except HTTPException:
        raise

    except Exception as e:
        print(
            "LOGIN ERROR:",
            repr(e)
        )

        raise HTTPException(
            status_code=500,
            detail=f"LOGIN ERROR: {repr(e)}"
        )