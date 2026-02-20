from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload

from app.db import SessionLocal
from app.models import PaperLabel, Book  # make sure this imports your SQLAlchemy models
from app.pdf_utils import generate_label_pdf  # your PDF generation function
from app import crud
from app.schemas import PaperLabelOut

router = APIRouter(tags=["Labels"], prefix="/v1/label")

# Replace this with your actual base URL
BASE_URL = "http://127.0.0.1:8000"

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/pdf/{paper_id}")
def download_label_pdf(paper_id: int, db: Session = Depends(get_db)):
    """
    Generate and return the PDF for a specific PaperLabel.
    Eager-loads the book relationship to avoid DetachedInstanceError.
    """
    # Eager-load the book relationship
    label = db.query(PaperLabel)\
        .options(selectinload(PaperLabel.book))\
        .filter(PaperLabel.id == paper_id)\
        .first()

    if not label:
        raise HTTPException(status_code=404, detail="Label not found")

    # Generate PDF while session is still active
    pdf_buffer = generate_label_pdf(label.book, paper_id, BASE_URL)

    # Return as streaming response so browser can open/download
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="label_{paper_id}.pdf"'}
    )


@router.post("/mint/{book_id}", response_model=PaperLabelOut)
def mint_label(book_id: int, db: Session = Depends(get_db)):
    """
    Create a new PaperLabel for the provided `book_id` (path parameter) and return it.
    Example: POST /label/mint/123
    """
    # Ensure the referenced book exists
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Create the label
    label = crud.create_label(db, book_id)

    # Eager-load the book relationship so response_model can include it
    label = db.query(PaperLabel).options(selectinload(PaperLabel.book)).filter(PaperLabel.id == label.id).first()

    return label