from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, selectinload

from app.db import SessionLocal
from app.models import PaperLabel  # make sure this imports your SQLAlchemy models
from app.pdf_utils import generate_label_pdf  # your PDF generation function

router = APIRouter()

# Replace this with your actual base URL
BASE_URL = "http://127.0.0.1:8000"

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/label/pdf/{paper_id}")
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