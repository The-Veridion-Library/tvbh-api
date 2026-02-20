from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
import os
import jwt
from jwt import PyJWTError
from app.db import SessionLocal
from app import crud

# Expose these security dependencies so FastAPI/OpenAPI shows the schemes
security = HTTPBearer(auto_error=False, scheme_name="JWT Secret")
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False, scheme_name="API Key")


def verify_jwt_token_from_header(token: str) -> dict:
    """Decode JWT token string and return payload or raise 401."""
    secret = os.getenv("JWT_SECRET", "CHANGE_ME")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def verify_auth(
    bearer: HTTPAuthorizationCredentials = Depends(security),
    x_api_key: str = Depends(api_key_scheme),
):
    """Dependency that accepts either a Bearer JWT or an X-API-Key header.

    Because this function depends on FastAPI security dependencies (`HTTPBearer` and `APIKeyHeader`),
    the OpenAPI schema will include those security schemes and the docs will show the Authorize button.
    """
    # First: Bearer JWT (handled by HTTPBearer)
    if bearer and bearer.scheme and bearer.credentials:
        payload = verify_jwt_token_from_header(bearer.credentials)
        return {"type": "jwt", "payload": payload}

    # Second: X-API-Key header
    if x_api_key:
        db = SessionLocal()
        try:
            record = crud.verify_api_key(db, x_api_key)
            if not record:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
            return {"type": "api_key", "record": {"id": record.id, "user_id": record.user_id}}
        finally:
            db.close()

    # No valid auth provided
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authentication")
