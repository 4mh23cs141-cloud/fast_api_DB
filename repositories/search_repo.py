from sqlalchemy.orm import Session
from models import SearchHistory

class SearchRepo:
    def __init__(self, db: Session):
        self.db = db

    def add_search_history(self, user_id: int, query: str):
        db_history = SearchHistory(user_id=user_id, query=query)
        self.db.add(db_history)
        self.db.commit()
        self.db.refresh(db_history)
        return db_history

    def get_user_history(self, user_id: int, limit: int = 10):
        return self.db.query(SearchHistory).filter(SearchHistory.user_id == user_id).order_by(SearchHistory.timestamp.desc()).limit(limit).all()
