# app/main.py
from fastapi import FastAPI
from app.routes import label
import uvicorn

app = FastAPI(title="TVBH Label API")

# Include the label router
app.include_router(label.router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)