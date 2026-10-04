"""
Database configuration and session management supporting PostgreSQL (Neon) and SQLite fallback.
"""

import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from backend.models import Base

logger = logging.getLogger("campus_resolve.db")

# Load environment variables from backend/.env or root .env
DB_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(DB_DIR)

if os.path.exists(os.path.join(DB_DIR, ".env")):
    load_dotenv(os.path.join(DB_DIR, ".env"))
elif os.path.exists(os.path.join(PROJECT_ROOT, ".env")):
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

raw_db_url = os.getenv("DATABASE_URL")
engine = None
DATABASE_URL = None

if raw_db_url and raw_db_url.strip():
    candidate_url = raw_db_url.strip()
    # Normalize postgresql:// to postgresql+psycopg2:// for SQLAlchemy compatibility
    if candidate_url.startswith("postgresql://"):
        candidate_url = candidate_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    
    try:
        test_engine = create_engine(
            candidate_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 15}
        )
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine = test_engine
        DATABASE_URL = candidate_url
        print("[DATABASE] Successfully connected to PostgreSQL (Neon cloud database)!")
    except Exception as e:
        print(f"[DATABASE] Notice: Remote PostgreSQL connection encountered: {e}. Falling back to high-speed local SQLite.")

if engine is None:
    if os.getenv("VERCEL"):
        DB_FILE = "/tmp/campus_resolve.db"
    else:
        DB_FILE = os.path.join(DB_DIR, "campus_resolve.db")
    DATABASE_URL = f"sqlite:///{DB_FILE}"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    print(f"[DATABASE] Connected to SQLite database at {DB_FILE}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI Dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
