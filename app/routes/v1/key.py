from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.db import SessionLocal
from app import crud
from app.auth import verify_auth

router = APIRouter(tags=["API Keys"], prefix="/v1/key")


class CreateKeyIn(BaseModel):
    user_id: int


@router.post("/create")
def create_key(payload: CreateKeyIn, auth=Depends(verify_auth)):
    """Generate a new API key for `user_id`, return the plaintext key once and store only the hash."""
    # Require JWT auth for creating API keys (prevent API key from creating other keys)
    if auth.get("type") != "jwt":
        raise HTTPException(status_code=403, detail="API key creation requires JWT authentication")

    raw_key = __generate_raw_key()

    db = SessionLocal()
    try:
        api = crud.create_api_key(db, payload.user_id, raw_key)
    finally:
        db.close()

    return {"api_key": raw_key, "id": api.id, "user_id": api.user_id}


def __generate_raw_key() -> str:
    import secrets
    # produce a URL-safe string; length ~43 chars for 32 bytes
    return secrets.token_urlsafe(32)
