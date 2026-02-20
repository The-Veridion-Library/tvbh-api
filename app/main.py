# app/main.py
from fastapi import FastAPI, Depends
from dotenv import load_dotenv

# Load environment variables from a .env file (if present)
load_dotenv()
from app.routes.v1 import label, verify, admin as admin_routes
from app.db import init_db
import uvicorn
from app.routes.v1.book import create as book_create
from app.auth import verify_jwt_token

app = FastAPI(title="TVBH - API - Version 1.0", version="1.0", dependencies=[Depends(verify_jwt_token)])

# Include routers
app.include_router(admin_routes.router)
app.include_router(label.router)
app.include_router(verify.router)
app.include_router(book_create.router)


@app.on_event("startup")
def on_startup():
    """Create DB tables if they don't exist."""
    init_db()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)