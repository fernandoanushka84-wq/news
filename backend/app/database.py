import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import pymysql

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "thailand_tourism_news")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)

# Engine without database name (for creating DB)
SERVER_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}"

engine = None
SessionLocal = None
Base = declarative_base()


def ensure_database_exists():
    """Create MySQL database if it does not exist. Runs automatically on startup."""
    try:
        temp_engine = create_engine(SERVER_URL, pool_pre_ping=True)
        with temp_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
        temp_engine.dispose()
        print(f"[DB] Database '{MYSQL_DATABASE}' is ready.")
    except Exception as e:
        print(f"[DB] Warning: Could not ensure database exists: {e}")
        print("[DB] Make sure MySQL is running and credentials in .env are correct.")


def get_engine():
    global engine, SessionLocal
    if engine is None:
        ensure_database_exists()
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine


def init_db():
    """Create all tables if they do not exist. Called automatically on backend startup."""
    eng = get_engine()
    # Import models so they are registered with Base
    from app.models import NewsArticle  # noqa: F401
    Base.metadata.create_all(bind=eng)
    print("[DB] Tables created / verified successfully.")


def get_db():
    if SessionLocal is None:
        get_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
