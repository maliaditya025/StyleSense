"""
StyleSense Backend — FastAPI Application Entry Point.

This is the main application file that:
- Initializes the FastAPI app with metadata
- Configures CORS middleware
- Includes all API routers
- Serves uploaded images as static files
- Creates database tables on startup
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.database import init_db


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle — runs on startup and shutdown."""
    # Create uploads directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Initialize database tables
    init_db()
    print("✅ Database initialized")
    print("✅ Upload directory ready")
    print(f"📂 Uploads: {os.path.abspath(settings.UPLOAD_DIR)}")

    yield  # App runs here

    print("👋 Shutting down StyleSense backend")


# ─── Create FastAPI App ───────────────────────────────────────────

app = FastAPI(
    title="StyleSense API",
    description="AI-powered outfit recommendation engine",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS Middleware ──────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files (uploaded images) ──────────────────────────────

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ─── Include API Routers ─────────────────────────────────────────

from app.routers import auth, profile, clothes, outfits

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(clothes.router)
app.include_router(outfits.router)


# ─── Health Check ─────────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": "StyleSense API",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
