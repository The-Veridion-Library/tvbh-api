# app/main.py
from fastapi import FastAPI
from app.routes.v1 import label, verify
from app.db import init_db
import uvicorn
from app.routes.v1.book import create as book_create

app = FastAPI(title="The Veridion Book Hunt - API")

# Include routers
app.include_router(label.router)
app.include_router(verify.router)
app.include_router(book_create.router)


@app.on_event("startup")
def on_startup():
    """Create DB tables if they don't exist."""
    init_db()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)