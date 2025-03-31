from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class CryptoBase(BaseModel):
    symbol: str = Field(..., description="Cryptocurrency symbol (e.g., BTC, ETH)")


class CryptoCreate(CryptoBase):
    note: Optional[str] = None


class CryptoUpdate(BaseModel):
    note: Optional[str] = None


class Crypto(CryptoBase):
    id: int
    name: Optional[str] = None
    coingecko_id: Optional[str] = None
    last_updated_coingecko: Optional[datetime] = None
    coin_metadata: Optional[Dict[str, Any]] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True
