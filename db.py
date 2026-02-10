from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
load_dotenv()

Base=declarative_base()

DATABASE_URL=os.getenv("DATABASE_URL")
if DATABASE_URL is None:
    DATABASE_URL = "sqlite:///./test.db"
    print("WARNING: DATABASE_URL not set in environment, using default SQLite database.")
elif DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

print("DATABASE_URL",DATABASE_URL)
engine=create_engine(DATABASE_URL)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        