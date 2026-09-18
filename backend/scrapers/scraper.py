import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
import time
from typing import List, Dict, Optional

from scrapers.sources import NEWS_SOURCES, TOURISM_KEYWORDS
from models.classifier import classify_article
from app.database import get_engine, get_session, init_db
from app.models import NewsArticle

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def contains_tourism_keyword(text: str) -> bool:
    if not text:
        return False
    lower = text.lower()
    return any(kw in lower for kw in TOURISM_KEYWORDS)


def parse_date(date_str: str) -> Optional[datetime]:
    if not date_str:
        return None
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except Exception:
        pass
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%d %H:%M:%S",
        "%a, %d %b %Y %H:%M:%S %z",
        "%d %b %Y",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str[:26], fmt)
        except Exception:
            continue
    return None


def fetch_rss(source: dict) -> List[Dict]:
    articles = []
    rss_url = source.get("rss_url")
    if not rss_url:
        return articles

    try:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:30]:
            title = entry.get("title", "").strip()
            summary = entry.get("summary", "") or entry.get("description", "")
            link = entry.get("link", "")
            published = entry.get("published") or entry.get("updated")

            if not title or not link:
                continue

            if not contains_tourism_keyword(title + " " + summary):
                continue

            articles.append({
                "title": title,
                "summary": BeautifulSoup(summary, "lxml").get_text()[:500] if summary else "",
                "url": link,
                "source": source["name"],
                "published_at": parse_date(published),
                "content": ""
            })
    except Exception as e:
        print(f"Error fetching RSS from {source['name']}: {e}")

    return articles


def scrape_category_page(url: str, source_name: str) -> List[Dict]:
    articles = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        for item in soup.select("article, .post, .news-item, .entry, .card")[:20]:
            title_tag = item.select_one("h2 a, h3 a, .title a, a.headline")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            if link and not link.startswith("http"):
                link = urljoin(url, link)

            summary_tag = item.select_one("p, .summary, .excerpt, .description")
            summary = summary_tag.get_text(strip=True)[:500] if summary_tag else ""

            if not title or not link:
                continue
            if not contains_tourism_keyword(title + " " + summary):
                continue

            articles.append({
                "title": title,
                "summary": summary,
                "url": link,
                "source": source_name,
                "published_at": None,
                "content": ""
            })
    except Exception as e:
        print(f"Error scraping {url}: {e}")

    return articles


def save_article(db, article_data: dict, classification: dict) -> bool:
    if not classification.get("is_tourism", False):
        return False
    if classification.get("confidence", 0) < 0.55:
        return False

    existing = db.query(NewsArticle).filter(NewsArticle.url == article_data["url"]).first()
    if existing:
        return False

    news = NewsArticle(
        title=article_data["title"],
        summary=article_data.get("summary", ""),
        content=article_data.get("content", ""),
        url=article_data["url"],
        source=article_data["source"],
        published_at=article_data.get("published_at"),
        category=classification.get("category", "Other"),
        is_tourism=True,
        confidence=str(classification.get("confidence", 0))
    )
    db.add(news)
    db.commit()
    return True


def run_full_scrape():
    """
    Main scraping pipeline.
    Safe to call from FastAPI background tasks.
    Always creates a fresh DB session via get_session().
    """
    print("[SCRAPE] Starting full scrape...")
    init_db()
    get_engine()  # ensure engine + SessionLocal exist

    db = get_session()  # <-- fixed: never use SessionLocal() directly
    total_saved = 0

    try:
        for source in NEWS_SOURCES:
            print(f"[SCRAPE] Processing source: {source['name']}")
            articles = []

            if source.get("rss_url"):
                articles.extend(fetch_rss(source))

            for cat_url in source.get("category_urls", []):
                articles.extend(scrape_category_page(cat_url, source["name"]))

            seen = set()
            unique_articles = []
            for a in articles:
                if a["url"] not in seen:
                    seen.add(a["url"])
                    unique_articles.append(a)

            print(f"[SCRAPE]   Found {len(unique_articles)} candidate articles")

            for article in unique_articles:
                try:
                    classification = classify_article(
                        article["title"],
                        article.get("summary", "")
                    )
                    if save_article(db, article, classification):
                        total_saved += 1
                        print(f"[SCRAPE]   Saved: {article['title'][:60]}... [{classification.get('category')}]")
                except Exception as e:
                    print(f"[SCRAPE]   Error classifying/saving article: {e}")

                time.sleep(0.3)

        print(f"[SCRAPE] Finished. Total new tourism articles saved: {total_saved}")
        return total_saved
    except Exception as e:
        print(f"[SCRAPE] Fatal error: {e}")
        raise
    finally:
        db.close()
        print("[SCRAPE] DB session closed.")
