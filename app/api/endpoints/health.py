from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.base import get_db

router = APIRouter()

@router.get("/health", status_code=200)
def health_check(db: Session = Depends(get_db)):
    """
    Jednoduchý health check endpoint pro ověření, že aplikace běží a je připojena k databázi.
    """
    # Test DB connection
    db.execute(text("SELECT 1"))
    
    return {"status": "ok", "database": "connected"}