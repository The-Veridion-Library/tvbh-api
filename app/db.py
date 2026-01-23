from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

DATABASE_URL = os.environ.get("DATABASE_URL")  # e.g., postgres://user:pass@host/dbname

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from .models import Base
    Base.metadata.create_all(bind=engine)
