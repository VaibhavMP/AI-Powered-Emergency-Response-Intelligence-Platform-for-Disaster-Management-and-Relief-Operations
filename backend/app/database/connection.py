from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

db_url = settings.database_url
connect_args = {}
if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(db_url, pool_pre_ping=True, connect_args=connect_args)
    # Validate connection quickly
    with engine.connect() as conn:
        pass
    logger.info(f"Connected to database at {db_url}")
except Exception as e:
    logger.warning(f"Could not connect to database '{db_url}' ({e}). Falling back to local SQLite.")
    db_url = "sqlite:///./disaster_response.db"
    engine = create_engine(db_url, pool_pre_ping=True, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
