from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from repositories.search_repo import SearchRepo
from schemas.search_schema import SearchCreate, SearchHistorySchema
from utils.jwt_handler import verify_token
from fastapi.security import OAuth2PasswordBearer
from typing import List

router = APIRouter(prefix="/search", tags=["search"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user_id(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return int(payload.get("sub"))

@router.post("/", response_model=SearchHistorySchema)
def add_search(search: SearchCreate, db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    search_repo = SearchRepo(db)
    return search_repo.add_search_history(user_id=user_id, query=search.query)

@router.get("/history", response_model=List[SearchHistorySchema])
def get_history(db: Session = Depends(get_db), user_id: int = Depends(get_current_user_id)):
    search_repo = SearchRepo(db)
    return search_repo.get_user_history(user_id=user_id)
