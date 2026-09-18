from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Index
from datetime import datetime
from app.database import Base


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    source = Column(String(200), nullable=True, index=True)
    published_at = Column(DateTime, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    is_tourism = Column(Boolean, default=True, index=True)
    confidence = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_category_created", "category", "created_at"),
        Index("idx_source_created", "source", "created_at"),
    )
