from fastapi import FastAPI

from app.config.settings import settings
from app.routers import auth

app = FastAPI(title=settings.app_name, debug=settings.debug)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "app": settings.app_name,
        "env": settings.app_env
    }

app.include_router(auth.router)