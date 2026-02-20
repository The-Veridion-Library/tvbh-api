from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import jwt
from jwt import PyJWTError

security = HTTPBearer()

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verify a Bearer JWT and return its payload.

    Raises 401 if token missing or invalid. Uses `JWT_SECRET` env var or a placeholder.
    """
    token = credentials.credentials if credentials else None
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Bearer token",
        )

    secret = os.getenv("JWT_SECRET", "CHANGE_ME")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
