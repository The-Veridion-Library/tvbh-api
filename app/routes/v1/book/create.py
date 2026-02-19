from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import Book
from app.schemas import BookCreate, BookOut

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/v1/book/create", response_model=BookOut)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """
    Create a new Book entry.
    """
    db_book = Book(title=book.title, author=book.author, isbn=book.isbn)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book
