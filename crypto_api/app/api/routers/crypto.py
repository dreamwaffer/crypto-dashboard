import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Any
from app.db import models
from app.schemas import crypto as crypto_schemas
from app.crud import crud_crypto
from app.services import coingecko
from app.db.base import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=crypto_schemas.Crypto, status_code=status.HTTP_201_CREATED)
def create_cryptocurrency(
        *,
        db: Session = Depends(get_db),
        crypto_in: crypto_schemas.CryptoCreate
) -> Any:
    """
    Create new cryptocurrency record.
    Verifies symbol with CoinGecko, fetches initial metadata (price, image) (synchronous).
    """
    symbol_upper = crypto_in.symbol.upper()

    db_crypto = crud_crypto.get_crypto(db, symbol=symbol_upper)
    if db_crypto:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cryptocurrency with symbol '{symbol_upper}' already exists.",
        )

    search_result = coingecko.search_coin(symbol=symbol_upper)
    if not search_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symbol '{symbol_upper}' not found on CoinGecko.",
        )

    coingecko_id, name = search_result

    existing_by_cg_id = db.query(models.Cryptocurrency).filter(
        models.Cryptocurrency.coingecko_id == coingecko_id).first()
    if existing_by_cg_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cryptocurrency with CoinGecko ID '{coingecko_id}' (symbol: {existing_by_cg_id.symbol}) already exists.",
        )

    coin_metadata = {}
    prices = coingecko.get_prices(coingecko_ids=[coingecko_id], vs_currency="usd")

    if coingecko_id in prices and "usd" in prices[coingecko_id]:
        coin_metadata["current_price_usd"] = prices[coingecko_id]["usd"]

    details = coingecko.get_coin_details(coingecko_id=coingecko_id)
    if details and details.get("image"):
        coin_metadata["image"] = details["image"]

    created_crypto = crud_crypto.create_crypto(
        db=db,
        symbol=symbol_upper,
        name=name,
        coingecko_id=coingecko_id,
        coin_metadata=coin_metadata,
        note=crypto_in.note
    )
    return created_crypto


@router.get("/", response_model=List[crypto_schemas.Crypto])
def read_cryptocurrencies(
        db: Session = Depends(get_db),
        skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
        limit: int = Query(100, ge=1, le=200, description="Maximum number of records to return")
) -> Any:
    """
    Retrieve a list of cryptocurrencies with pagination.
    """
    cryptos = crud_crypto.get_cryptos(db, skip=skip, limit=limit)
    return cryptos


@router.get("/{symbol}", response_model=crypto_schemas.Crypto)
def read_cryptocurrency(
        *,
        db: Session = Depends(get_db),
        symbol: str
) -> Any:
    """
    Get a specific cryptocurrency by its symbol.
    """

    db_crypto = crud_crypto.get_crypto(db, symbol=symbol)
    if not db_crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol '{symbol}' not found",
        )
    return db_crypto


@router.put("/{symbol}", response_model=crypto_schemas.Crypto)
def update_cryptocurrency(
        *,
        db: Session = Depends(get_db),
        symbol: str,
        crypto_in: crypto_schemas.CryptoUpdate
) -> Any:
    """
    Update a cryptocurrency by its symbol (only supports updating note).
    """

    db_crypto = crud_crypto.get_crypto(db, symbol=symbol)
    if not db_crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol '{symbol}' not found",
        )

    updated_crypto = crud_crypto.update_crypto(db=db, db_obj=db_crypto, crypto_in=crypto_in)
    return updated_crypto


@router.delete("/{symbol}", response_model=crypto_schemas.Crypto)
def delete_cryptocurrency(
        *,
        db: Session = Depends(get_db),
        symbol: str
) -> Any:
    """
    Delete a cryptocurrency by its symbol.
    """

    db_crypto = crud_crypto.get_crypto(db, symbol=symbol)
    if not db_crypto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with symbol '{symbol}' not found",
        )

    deleted_crypto = crud_crypto.delete_crypto(db=db, symbol=db_crypto.symbol)

    return deleted_crypto
