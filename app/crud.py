# app/crud.py
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import PaperLabel, LabelStatus
import datetime
from app.models import APIKey
from passlib.context import CryptContext
import hmac


# Password / key hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


def create_api_key(db: Session, user_id: int, raw_key: str) -> APIKey:
    """Hash `raw_key` and store an APIKey record tied to `user_id`. Returns the created APIKey instance."""
    hashed = pwd_context.hash(raw_key)
    api = APIKey(user_id=user_id, key_hash=hashed)
    db.add(api)
    db.commit()
    db.refresh(api)
    return api


def verify_api_key(db: Session, raw_key: str) -> APIKey:
    """Return the APIKey record if `raw_key` matches any stored hash, otherwise None."""
    # Fetch all keys and verify with bcrypt verify to avoid needing to store raw
    keys = db.query(APIKey).all()
    for k in keys:
        try:
            if pwd_context.verify(raw_key, k.key_hash):
                return k
        except Exception:
            # ignore malformed hash
            continue
    return None