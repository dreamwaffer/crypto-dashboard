from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


# Base schema with common attributes
class CryptocurrencyBase(BaseModel):
    """Base schema for cryptocurrency with common attributes"""
    symbol: str = Field(..., min_length=1, max_length=20, description="Symbol of cryptocurrency (e.g. BTC)")
    name: Optional[str] = Field(None, max_length=100, description="Name of cryptocurrency (e.g. Bitcoin)")
    notes: Optional[str] = Field(None, description="Optional notes about the cryptocurrency")


# Schema for creating a new cryptocurrency - only requires symbol
class CryptocurrencyCreate(CryptocurrencyBase):
    """Schema for creating a new cryptocurrency"""
    symbol: str = Field(..., min_length=1, max_length=20, description="Symbol of cryptocurrency (e.g. BTC)")


    @field_validator('symbol')
    def symbol_must_be_uppercase(cls, v):
        """Validate that symbol is uppercase"""
        if v != v.upper():
            return v.upper()
        return v


# Schema for updating an existing cryptocurrency
class CryptocurrencyUpdate(BaseModel):
    """Schema for updating an existing cryptocurrency"""
    notes: Optional[str] = Field(None, description="Optional notes about the cryptocurrency")


# Schema for cryptocurrency DB representation
class CryptocurrencyInDB(CryptocurrencyBase):
    """Schema representing a cryptocurrency in the database"""
    id: int
    coingecko_id: str
    current_price: Optional[float] = None
    market_cap: Optional[float] = None
    total_volume: Optional[float] = None
    price_change_24h: Optional[float] = None
    last_updated: datetime
    image_url: Optional[str] = None

    class Config:
        orm_mode = True


# Schema for cryptocurrency response
class CryptocurrencyResponse(CryptocurrencyInDB):
    """Schema for cryptocurrency response"""
    pass


# Schema for listing multiple cryptocurrencies
class CryptocurrencyList(BaseModel):
    """Schema for a list of cryptocurrencies"""
    items: list[CryptocurrencyResponse]
    total: int
    
    class Config:
        orm_mode = True 