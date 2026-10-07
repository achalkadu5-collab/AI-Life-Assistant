from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def home():
    return {
        "message": "Welcome to AI-Life-Assistant"
    }

@router.get("/about")
def about():
    return {
        "project":
"AI-Life-Assistant",
        "version": "1.0",
        "developer": "Achal"        
    }


