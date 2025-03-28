from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from app.core.settings import settings

# Create SQLAlchemy engine
engine = create_engine(str(settings.DATABASE_URI))

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()

# Dependency for getting DB session
def get_db() -> Session:
    """
    Dependency function that provides a SQLAlchemy session
    to database operations for FastAPI endpoints.
    Yields a session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 