"""Brocooo API — FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.config import settings
from app.database import create_db_and_tables
from app.routers import projects, clips, upload, progress, explore, settings as settings_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown events."""
    create_db_and_tables()
    os.makedirs(settings.storage_dir, exist_ok=True)
    os.makedirs(os.path.join(settings.storage_dir, "uploads"), exist_ok=True)
    os.makedirs(os.path.join(settings.storage_dir, "downloads"), exist_ok=True)
    os.makedirs(os.path.join(settings.storage_dir, "renders"), exist_ok=True)
    os.makedirs(os.path.join(settings.storage_dir, "thumbnails"), exist_ok=True)
    yield


app = FastAPI(
    title="Brocooo API",
    description="Turn any video into viral shorts. Free. Unlimited.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for rendered clips
app.mount(
    "/storage",
    StaticFiles(directory=settings.storage_dir),
    name="storage",
)

# Routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(clips.router, prefix="/api/clips", tags=["clips"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(progress.router, prefix="/api", tags=["progress"])
app.include_router(explore.router, prefix="/api", tags=["explore"])
app.include_router(settings_router.router, prefix="/api/settings", tags=["settings"])


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "brocooo-api"}
