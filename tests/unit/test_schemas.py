import pytest
from datetime import datetime
from pydantic import ValidationError

from app.schemas.cryptocurrency import (
    CryptocurrencyCreate, 
    CryptocurrencyUpdate,
    CryptocurrencyInDB,
    CryptocurrencyResponse
)


def test_cryptocurrency_create_schema():
    # Test valid data
    crypto = CryptocurrencyCreate(symbol="BTC")
    assert crypto.symbol == "BTC"
    assert crypto.name is None
    assert crypto.notes is None

    # Test lowercase symbol gets converted to uppercase
    crypto = CryptocurrencyCreate(symbol="eth")
    assert crypto.symbol == "ETH"

    # Test invalid data - empty symbol
    with pytest.raises(ValidationError):
        CryptocurrencyCreate(symbol="")


def test_cryptocurrency_update_schema():
    # Test valid data
    crypto = CryptocurrencyUpdate(notes="My notes")
    assert crypto.notes == "My notes"

    # Test empty update
    crypto = CryptocurrencyUpdate()
    assert crypto.notes is None


def test_cryptocurrency_indb_schema():
    # Test valid data
    now = datetime.now()
    crypto_data = {
        "id": 1,
        "coingecko_id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "current_price": 50000.0,
        "market_cap": 1000000000.0,
        "total_volume": 50000000.0,
        "price_change_24h": 2.5,
        "last_updated": now,
        "image_url": "https://example.com/bitcoin.png",
        "notes": "My notes"
    }
    
    crypto = CryptocurrencyInDB(**crypto_data)
    assert crypto.id == 1
    assert crypto.symbol == "BTC"
    assert crypto.name == "Bitcoin"
    assert crypto.current_price == 50000.0


def test_cryptocurrency_response_schema():
    # Test valid data
    now = datetime.now()
    crypto_data = {
        "id": 1,
        "coingecko_id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "current_price": 50000.0,
        "market_cap": 1000000000.0,
        "total_volume": 50000000.0,
        "price_change_24h": 2.5,
        "last_updated": now,
        "image_url": "https://example.com/bitcoin.png",
        "notes": "My notes"
    }
    
    crypto = CryptocurrencyResponse(**crypto_data)
    assert crypto.dict()["id"] == 1
    assert crypto.dict()["symbol"] == "BTC" 