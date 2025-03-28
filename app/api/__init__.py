from fastapi import APIRouter
from app.api.endpoints import health, cryptocurrencies

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(cryptocurrencies.router, prefix="/cryptocurrencies", tags=["cryptocurrencies"])
