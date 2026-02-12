from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from db import get_db
from models import ChatMessage
from utils.ai_response import get_completion
from utils.jwt_handler import verify_token
from schemas.ai_response_schemas import AIRequest, AIResponse, ChatMessageSchema
from typing import List

def get_current_user(token: str):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid session")
    return payload

router = APIRouter()


@router.post("/ask", response_model=AIResponse)
def ask_ai(request: AIRequest, token: str, session_id: int, db: Session = Depends(get_db)):
    """Get response from AI model and save to history."""
    user_data = get_current_user(token)
    user_id = user_data.get("sub")

    # Verify session belongs to user
    from models import ChatSession
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        # 1. Save User Message
        user_msg = ChatMessage(session_id=session_id, user_id=user_id, role="user", content=request.message)
        db.add(user_msg)
        
        # 2. Get AI Response
        ai_text = get_completion(request.message, request.system_prompt)
        
        # 3. Save AI Message
        ai_msg = ChatMessage(session_id=session_id, user_id=user_id, role="assistant", content=ai_text)
        db.add(ai_msg)
        
        # 4. Update session title if it's the first message
        if session.title == "New Chat":
            session.title = request.message[:50] + ("..." if len(request.message) > 50 else "")
        session.updated_at = func.now()
        
        db.commit()
        return AIResponse(response=ai_text)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[ChatMessageSchema])
def get_chat_history(token: str, db: Session = Depends(get_db)):
    """Retrieve chat history for the authenticated user."""
    user_data = get_current_user(token)
    user_id = user_data.get("sub")
    
    messages = db.query(ChatMessage).filter(ChatMessage.user_id == user_id).order_by(ChatMessage.timestamp.asc()).all()
    return messages