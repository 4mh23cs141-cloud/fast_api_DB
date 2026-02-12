from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from db import get_db
from models import ChatSession, ChatMessage
from utils.jwt_handler import verify_token
from schemas.session_schema import SessionCreate, SessionSchema
from schemas.ai_response_schemas import ChatMessageSchema
from typing import List

router = APIRouter()

def get_current_user(token: str):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid session")
    return payload

@router.get("/sessions", response_model=List[SessionSchema])
def get_sessions(token: str, db: Session = Depends(get_db)):
    """Get all chat sessions for the authenticated user."""
    user_data = get_current_user(token)
    user_id = user_data.get("sub")
    
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user_id).order_by(ChatSession.updated_at.desc()).all()
    return sessions

@router.post("/sessions", response_model=SessionSchema)
def create_session(session: SessionCreate, token: str, db: Session = Depends(get_db)):
    """Create a new chat session."""
    user_data = get_current_user(token)
    user_id = user_data.get("sub")
    
    new_session = ChatSession(user_id=user_id, title=session.title)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageSchema])
def get_session_messages(session_id: int, token: str, db: Session = Depends(get_db)):
    """Get all messages for a specific session."""
    user_data = get_current_user(token)
    user_id = user_data.get("sub")
    
    # Verify session belongs to user
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.timestamp.asc()).all()
    return messages

@router.delete("/sessions/{session_id}")
def delete_session(session_id: int, token: str, db: Session = Depends(get_db)):
    """Delete a chat session."""
    user_data = get_current_user(token)
    user_id = user_data.get("sub")
    
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete associated messages
    db.query(ChatMessage).filter(ChatMessage.session_id == session_id).delete()
    db.delete(session)
    db.commit()
    return {"message": "Session deleted successfully"}
