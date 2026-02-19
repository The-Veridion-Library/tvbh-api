# app/crud.py
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import PaperLabel, LabelStatus
import datetime


def get_label_by_paper_id(paper_id: int):
    db = SessionLocal()
    try:
        label = db.query(PaperLabel).filter(PaperLabel.id == paper_id).first()
        return label
    finally:
        db.close()


def create_label(db: Session, book_id: int) -> PaperLabel:
    """Invalidate existing labels for `book_id`, then create and return a new PaperLabel."""
    # Find existing labels for this book that are not already invalidated
    existing = db.query(PaperLabel).filter(
        PaperLabel.book_id == book_id,
        PaperLabel.status != LabelStatus.INVALIDATED,
    ).all()

    now = datetime.datetime.utcnow()
    for lab in existing:
        lab.status = LabelStatus.INVALIDATED
        lab.invalidated_at = now
        db.add(lab)

    # Create the new label
    new_label = PaperLabel(book_id=book_id)
    db.add(new_label)

    # Commit all changes (invalidations + new label) together
    db.commit()

    # Refresh the new label to get generated fields
    db.refresh(new_label)
    return new_label