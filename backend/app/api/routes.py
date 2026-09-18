from fastapi import APIRouter, Depends, Query, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List

from app.database import get_db
from app.models import NewsArticle
from app.schemas import NewsOut, NewsListResponse, HealthResponse
from models.classifier import CATEGORIES, check_ollama_status
from scrapers.scraper import run_full_scrape

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    db_status = "ok"
    try:
        db.execute(func.select(1))
    except Exception:
        db_status = "error"

    ollama_status = check_ollama_status()

    return HealthResponse(
        status="ok" if db_status == "ok" else "degraded",
        database=db_status,
        ollama=ollama_status,
        message="Thailand Tourism News Analyzer API is running"
    )


@router.get("/news", response_model=NewsListResponse)
def list_news(
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(NewsArticle).filter(NewsArticle.is_tourism == True)

    if category:
        query = query.filter(NewsArticle.category == category)
    if source:
        query = query.filter(NewsArticle.source == source)

    total = query.count()
    articles = query.order_by(NewsArticle.created_at.desc()).offset(offset).limit(limit).all()

    return NewsListResponse(total=total, items=articles)


@router.get("/news/{news_id}", response_model=NewsOut)
def get_news(news_id: int, db: Session = Depends(get_db)):
    article = db.query(NewsArticle).filter(NewsArticle.id == news_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="News not found")
    return article


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    results = (
        db.query(NewsArticle.category, func.count(NewsArticle.id))
        .filter(NewsArticle.is_tourism == True)
        .group_by(NewsArticle.category)
        .all()
    )
    return [{"category": cat or "Unknown", "count": count} for cat, count in results]


@router.get("/sources")
def list_sources(db: Session = Depends(get_db)):
    results = (
        db.query(NewsArticle.source, func.count(NewsArticle.id))
        .filter(NewsArticle.is_tourism == True)
        .group_by(NewsArticle.source)
        .all()
    )
    return [{"source": src or "Unknown", "count": count} for src, count in results]


@router.get("/meta/categories")
def get_all_categories():
    return {"categories": CATEGORIES}


@router.post("/scrape")
def trigger_scrape(background_tasks: BackgroundTasks):
    """Trigger a full scrape in background. Uses Ollama for classification."""
    background_tasks.add_task(run_full_scrape)
    return {"message": "Scrape started in background. Check logs for progress."}
