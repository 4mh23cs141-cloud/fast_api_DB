from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import User
from utils.jwt_handler import verify_token
from pydantic import BaseModel

router = APIRouter()

class ProfileSchema(BaseModel):
    name: str
    email: str
    joined_date: str

    class Config:
        from_attributes = True

def get_current_user(token: str):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid session")
    return payload

@router.get("/profile", response_model=ProfileSchema)
def get_profile(token: str, db: Session = Depends(get_db)):
    """Get user profile data."""
    user_data = get_current_user(token)
    user_id = user_data.get("sub")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "name": user.name or "User",
        "email": user.email,
        "joined_date": "February 2026"  # You can add a created_at field to User model later
    }
