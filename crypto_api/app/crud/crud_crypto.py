from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.db import models
from app.schemas import crypto as crypto_schemas


def get_crypto(db: Session, symbol: str) -> Optional[models.Cryptocurrency]:
    """Gets a single cryptocurrency by its symbol (case-insensitive search)."""
    return db.query(models.Cryptocurrency).filter(models.Cryptocurrency.symbol.ilike(symbol)).first()


def get_cryptos(db: Session, skip: int = 0, limit: int = 100) -> List[models.Cryptocurrency]:
    """Gets a list of cryptocurrencies with pagination."""
    return db.query(models.Cryptocurrency).offset(skip).limit(limit).all()


def get_all_crypto_coingecko_ids(db: Session) -> List[str]:
    """Gets a list of all non-null coingecko_ids stored in the database."""
    results = db.query(models.Cryptocurrency.coingecko_id).filter(models.Cryptocurrency.coingecko_id.isnot(None)).all()
    return [result[0] for result in results]


def create_crypto(db: Session, symbol: str, name: str, coingecko_id: str, coin_metadata: Dict[str, Any],
                  note: Optional[str] = None) -> models.Cryptocurrency:
    """Creates a new cryptocurrency record."""
    db_crypto = models.Cryptocurrency(
        symbol=symbol.upper(),
        name=name,
        coingecko_id=coingecko_id,
        coin_metadata=coin_metadata,
        note=note,
        last_updated_coingecko=datetime.now()
    )
    db.add(db_crypto)
    db.commit()
    db.refresh(db_crypto)
    return db_crypto


def update_crypto(db: Session, db_obj: models.Cryptocurrency,
                  crypto_in: crypto_schemas.CryptoUpdate) -> models.Cryptocurrency:
    """Updates the note for an existing cryptocurrency record."""
    update_data = crypto_in.model_dump(exclude_unset=True)

    if "note" in update_data:
        db_obj.note = update_data["note"]
        db_obj.last_updated_coingecko = datetime.now()

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def update_crypto_metadata_batch(db: Session, updates: Dict[str, Dict[str, Any]]) -> int:
    """
    Updates coin_metadata for multiple cryptocurrencies based on coingecko_id.
    'updates' dict format: {coingecko_id: {'current_price_usd': ..., 'image': ...}}
    Returns the number of updated records.
    """
    if not updates:
        return 0

    coingecko_ids = list(updates.keys())
    db_cryptos = db.query(models.Cryptocurrency).filter(models.Cryptocurrency.coingecko_id.in_(coingecko_ids)).all()

    updated_count = 0
    for db_crypto in db_cryptos:
        if db_crypto.coingecko_id in updates:
            new_metadata = updates[db_crypto.coingecko_id]
            current_metadata = db_crypto.coin_metadata if db_crypto.coin_metadata else {}
            current_metadata.update(new_metadata)

            db_crypto.coin_metadata = current_metadata
            flag_modified(db_crypto, "coin_metadata")
            db_crypto.last_updated_coingecko = datetime.now()
            db.add(db_crypto)
            updated_count += 1

    if updated_count > 0:
        db.commit()
    return updated_count


def delete_crypto(db: Session, symbol: str) -> Optional[models.Cryptocurrency]:
    """Deletes a cryptocurrency record by its ID."""
    db_obj = db.query(models.Cryptocurrency).filter(models.Cryptocurrency.symbol == symbol).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
