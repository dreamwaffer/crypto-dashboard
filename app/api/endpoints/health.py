from fastapi import APIRouter

router = APIRouter()

@router.get("/health", status_code=200)
def health_check():
    """
    Jednoduchý health check endpoint pro ověření, že aplikace běží.
    """
    return {"status": "ok"} 