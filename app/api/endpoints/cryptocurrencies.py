from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.db import crud
from app.db.base import get_db
from app.schemas import (
    CryptocurrencyCreate,
    CryptocurrencyUpdate,
    CryptocurrencyResponse,
    CryptocurrencyList
)

router = APIRouter()


@router.get("/", response_model=CryptocurrencyList)
def list_cryptocurrencies(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """
    Get list of cryptocurrencies with pagination
    """
    cryptocurrencies = crud.get_cryptocurrencies(db, skip=skip, limit=limit)
    total = len(cryptocurrencies)  # In a production app, you would get total count from DB
    return {"items": cryptocurrencies, "total": total}


@router.get("/{symbol}", response_model=CryptocurrencyResponse)
def get_cryptocurrency_by_symbol(
        symbol: str = Path(..., title="The symbol of the cryptocurrency to get"),
        db: Session = Depends(get_db)
):
    """
    Get a cryptocurrency by symbol
    """
    # Convert symbol to uppercase to ensure consistent lookup
    symbol = symbol.upper()
    crypto = crud.get_cryptocurrency_by_symbol(db, symbol)
    if crypto is None:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    return crypto


@router.put("/{symbol}", response_model=CryptocurrencyResponse)
def update_cryptocurrency_by_symbol(
        crypto_data: CryptocurrencyUpdate,
        symbol: str = Path(..., title="The symbol of the cryptocurrency to update"),
        db: Session = Depends(get_db)
):
    """
    Update a cryptocurrency by symbol
    """
    # Convert symbol to uppercase to ensure consistent lookup
    symbol = symbol.upper()
    crypto = crud.update_cryptocurrency_by_symbol(db, symbol, crypto_data.model_dump(exclude_unset=True))
    if crypto is None:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    return crypto


@router.delete("/{symbol}", status_code=204)
def delete_cryptocurrency_by_symbol(
        symbol: str = Path(..., title="The symbol of the cryptocurrency to delete"),
        db: Session = Depends(get_db)
):
    """
    Delete a cryptocurrency by symbol
    """
    # Convert symbol to uppercase to ensure consistent lookup
    symbol = symbol.upper()
    success = crud.delete_cryptocurrency_by_symbol(db, symbol)
    if not success:
        raise HTTPException(status_code=404, detail="Cryptocurrency not found")
    return None


@router.post("/", response_model=CryptocurrencyResponse, status_code=201)
def create_cryptocurrency(
        crypto: CryptocurrencyCreate,
        db: Session = Depends(get_db)
):
    """
    Create a new cryptocurrency
    """
    # Normally here we would call a service to verify with Coingecko API
    # For this example, we're creating a simplified version
    crypto_data = {
        "symbol": crypto.symbol,
        "name": crypto.name or crypto.symbol,  # Use symbol as name if name not provided
        "coingecko_id": crypto.symbol.lower(),  # Simplified - in reality, we'd get this from CoinGecko
        "notes": crypto.notes
    }

    return crud.create_cryptocurrency(db, crypto_data)
