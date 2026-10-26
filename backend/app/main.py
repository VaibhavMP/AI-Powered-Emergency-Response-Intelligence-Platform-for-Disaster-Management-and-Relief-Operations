from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.database.connection import engine, Base, SessionLocal
from app.database.seed import seed_database_if_empty
from app.api.router import api_router
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
        db = SessionLocal()
        try:
            seed_database_if_empty(db)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database initialization error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Disaster Response Platform API")
    init_db()
    yield
    logger.info("Shutting down Disaster Response Platform API")


app = FastAPI(
    title="Disaster Response Intelligence Platform",
    description="AI-Powered Emergency Response Intelligence Platform for Disaster Management and Relief Operations",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "disaster-response-api"}


@app.get("/")
async def root():
    return {
        "message": "Disaster Response Intelligence Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Ensure tables are initialized when imported
init_db()
