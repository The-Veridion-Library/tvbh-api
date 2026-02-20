from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import SessionLocal

router = APIRouter(prefix="/v1/admin", tags=["Admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Hunt Endpoints ---
@router.get("/hunts")
def list_hunts(db: Session = Depends(get_db)):
    """List all hunts (admin)."""
    # TODO: Implement actual DB logic
    return {"hunts": []}

@router.post("/hunts")
def create_hunt(hunt: dict, db: Session = Depends(get_db)):
    """Create a new hunt (admin)."""
    # TODO: Implement actual DB logic
    return {"message": "Hunt created", "hunt": hunt}

@router.patch("/hunts/{id}")
def edit_hunt(id: int, hunt: dict, db: Session = Depends(get_db)):
    """Edit a hunt (admin)."""
    # TODO: Implement actual DB logic
    return {"message": f"Hunt {id} updated", "hunt": hunt}

@router.delete("/hunts/{id}")
def delete_hunt(id: int, db: Session = Depends(get_db)):
    """Delete a hunt (admin)."""
    # TODO: Implement actual DB logic
    return {"message": f"Hunt {id} deleted"}

# --- Challenge Endpoints ---
@router.get("/challenges")
def list_challenges(db: Session = Depends(get_db)):
    """List all challenges (admin)."""
    # TODO: Implement actual DB logic
    return {"challenges": []}

@router.post("/challenges")
def create_challenge(challenge: dict, db: Session = Depends(get_db)):
    """Create a new challenge (admin)."""
    # TODO: Implement actual DB logic
    return {"message": "Challenge created", "challenge": challenge}

@router.patch("/challenges/{id}")
def edit_challenge(id: int, challenge: dict, db: Session = Depends(get_db)):
    """Edit a challenge (admin)."""
    # TODO: Implement actual DB logic
    return {"message": f"Challenge {id} updated", "challenge": challenge}

@router.delete("/challenges/{id}")
def delete_challenge(id: int, db: Session = Depends(get_db)):
    """Delete a challenge (admin)."""
    # TODO: Implement actual DB logic
    return {"message": f"Challenge {id} deleted"}
