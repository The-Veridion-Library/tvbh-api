# app/crud.py
from app.db import SessionLocal
from app.models import PaperLabel

async def get_label_by_paper_id(paper_id: str):
    db = SessionLocal()
    label = db.query(PaperLabel).filter(PaperLabel.id == paper_id).first()
    db.close()
    return label