from pydantic import BaseModel
from datetime import datetime
from typing import List

class SearchCreate(BaseModel):
    query: str

class SearchHistorySchema(BaseModel):
    id: int
    query: str
    timestamp: datetime

    class Config:
        from_attributes = True
