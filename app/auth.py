from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
import os
import jwt
from jwt import PyJWTError
from app.db import SessionLocal
from app import crud
import logging

logger = logging.getLogger("uvicorn.error")

# Expose these security dependencies so FastAPI/OpenAPI shows the schemes
security = HTTPBearer(auto_error=False, scheme_name="JWT Secret")
api_key_scheme = APIKeyHeader(name="X-API-Key", auto_error=False, scheme_name="API Key")
# Dev testing header - set `DEV_AUTH_TOKEN` in your .env to enable
dev_api_scheme = APIKeyHeader(name="X-DEV-AUTH", auto_error=False, scheme_name="Dev Auth")


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
    request: Request,
    bearer: HTTPAuthorizationCredentials = Depends(security),
    x_api_key: str = Depends(api_key_scheme),
    x_dev_token: str = Depends(dev_api_scheme),
):
    """Dependency that accepts either a Bearer JWT or an X-API-Key header.

    Because this function depends on FastAPI security dependencies (`HTTPBearer` and `APIKeyHeader`),
    the OpenAPI schema will include those security schemes and the docs will show the Authorize button.
    """
    # First: Dev token (for local/dev testing)
    # Enable by setting DEV_AUTH_TOKEN in your .env to a chosen secret.
    dev_secret = os.getenv("DEV_AUTH_TOKEN")
    debug = os.getenv("DEV_AUTH_DEBUG")
    if debug and dev_secret:
        logger.info("verify_auth: DEV_AUTH_TOKEN present; request headers: %s", dict(request.headers))
    if dev_secret:
        # Accept dev token via X-DEV-AUTH header
        if x_dev_token:
            if x_dev_token == dev_secret:
                return {"type": "dev", "token": x_dev_token}
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid dev token")

        # Accept dev token via Bearer field in the Swagger Authorize UI
        if bearer and bearer.credentials and bearer.credentials == dev_secret:
            return {"type": "dev", "token": bearer.credentials}

        # Accept dev token via X-API-Key header as well
        if x_api_key and x_api_key == dev_secret:
            return {"type": "dev", "token": x_api_key}
        # Fallback: read raw headers directly from request (handles proxies/clients)
        # Normalize header names to lowercase
        hdr_dev = request.headers.get("x-dev-auth")
        if hdr_dev and hdr_dev == dev_secret:
            if debug:
                logger.info("verify_auth: matched X-DEV-AUTH header")
            return {"type": "dev", "token": hdr_dev}

        hdr_api = request.headers.get("x-api-key")
        if hdr_api and hdr_api == dev_secret:
            if debug:
                logger.info("verify_auth: matched x-api-key header as dev token")
            return {"type": "dev", "token": hdr_api}

        auth_hdr = request.headers.get("authorization")
        if auth_hdr:
            parts = auth_hdr.split()
            if len(parts) == 2 and parts[0].lower() == "bearer" and parts[1] == dev_secret:
                if debug:
                    logger.info("verify_auth: matched Authorization Bearer as dev token")
                return {"type": "dev", "token": parts[1]}
        # Also accept dev token via query parameters for direct browser access
        q_dev = request.query_params.get("dev_token")
        if q_dev and q_dev == dev_secret:
            if debug:
                logger.info("verify_auth: matched dev_token query param")
            return {"type": "dev", "token": q_dev}

        q_api = request.query_params.get("api_key")
        if q_api and q_api == dev_secret:
            if debug:
                logger.info("verify_auth: matched api_key query param as dev token")
            return {"type": "dev", "token": q_api}

    # Second: Bearer JWT (handled by HTTPBearer)
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
