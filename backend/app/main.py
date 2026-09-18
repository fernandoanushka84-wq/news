"""
FastAPI Backend - Thailand Tourism News Analyzer
Database (MySQL) is created and tables are migrated automatically on startup.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.database import init_db, ensure_database_exists, get_engine
from app.api.routes import router
from models.classifier import check_ollama_status

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
AUTO_SCRAPE = os.getenv("AUTO_SCRAPE_ON_STARTUP", "false").lower() == "true"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ===== STARTUP: Auto run all DB scripts =====
    print("=" * 50)
    print("[STARTUP] Thailand Tourism News Analyzer Backend")
    print("=" * 50)

    print("[STARTUP] 1. Ensuring MySQL database exists...")
    ensure_database_exists()

    print("[STARTUP] 2. Creating / migrating tables...")
    init_db()

    print("[STARTUP] 3. Checking Ollama connection...")
    ollama_status = check_ollama_status()
    print(f"[STARTUP]    Ollama status: {ollama_status}")

    if AUTO_SCRAPE:
        print("[STARTUP] 4. Auto-scrape enabled. Starting background scrape...")
        from scrapers.scraper import run_full_scrape
        import threading
        t = threading.Thread(target=run_full_scrape, daemon=True)
        t.start()
    else:
        print("[STARTUP] 4. Auto-scrape is disabled (set AUTO_SCRAPE_ON_STARTUP=true to enable)")

    print("[STARTUP] Backend is ready.")
    print("=" * 50)

    yield

    # ===== SHUTDOWN =====
    print("[SHUTDOWN] Backend stopped.")


app = FastAPI(
    title="Thailand Tourism News Analyzer",
    description="Extract and classify Thailand tourism news using local Ollama models. MySQL + FastAPI + React.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "message": "Thailand Tourism News Analyzer API v2",
        "docs": "/docs",
        "health": "/api/health",
        "frontend": "Run React app on port 5173"
    }
