from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime


class NewsOut(BaseModel):
    id: int
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: str
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    category: Optional[str] = None
    is_tourism: bool = True
    confidence: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    total: int
    items: List[NewsOut]


class CategoryCount(BaseModel):
    category: str
    count: int


class SourceCount(BaseModel):
    source: str
    count: int


class HealthResponse(BaseModel):
    status: str
    database: str
    ollama: str
    message: str
