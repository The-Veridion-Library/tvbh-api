# app/main.py
from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html

# Load environment variables from a .env file (if present)
load_dotenv()
from app.routes.v1 import label, verify, admin as admin_routes
from app.db import init_db
import uvicorn
from app.routes.v1.book import create as book_create
from app.routes.v1.key import router as key_router
from app.auth import verify_auth

app = FastAPI(title="TVBH - API - Version 1.0", version="1.0", dependencies=[Depends(verify_auth)])

# Include routers
app.include_router(admin_routes.router)
app.include_router(label.router)
app.include_router(verify.router)
app.include_router(book_create.router)
app.include_router(key_router)

# Mount a static directory for custom docs assets (create `static/custom.css`)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Serve a slightly customized Swagger UI using a local custom CSS file.

    - `static/custom.css` is used to override the default Swagger UI styling.
    - The Swagger JS/CSS bundle is left as the default CDN provided by FastAPI.
    """
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Docs",
        swagger_favicon_url="/static/favicon.ico",
        swagger_css_url="/static/custom.css",
        swagger_ui_parameters={
            "docExpansion": "none",
            "defaultModelsExpandDepth": -1,
        },
    )


@app.on_event("startup")
def on_startup():
    """Create DB tables if they don't exist."""
    init_db()


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)