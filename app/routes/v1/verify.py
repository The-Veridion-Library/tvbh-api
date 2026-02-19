from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.db import SessionLocal
from app.models import PaperLabel, LabelStatus
from app.schemas import PaperLabelOut

router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/v1/verify/{label_id}")
def verify_label(label_id: int, db: Session = Depends(get_db)):
    """
    Verify a PaperLabel by ID. Returns error if not found or not PLACED, else success.
    """
    label = db.query(PaperLabel)\
        .options(selectinload(PaperLabel.book))\
        .filter(PaperLabel.id == label_id)\
        .first()

    if not label:
        return {"success": False, "reason": "Label not found"}, 404

    if label.status != LabelStatus.PLACED:
        return {
            "success": False,
            "reason": f"Label status is '{label.status.value}', not PLACED"
        }, 400

    return {"success": True, "message": "Label is valid and PLACED."}
