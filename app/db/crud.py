from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.db.models.cryptocurrency import Cryptocurrency

# Create operations
def create_cryptocurrency(db: Session, crypto_data: Dict[str, Any]) -> Cryptocurrency:
    """
    Create a new cryptocurrency record in the database
    """
    db_crypto = Cryptocurrency(**crypto_data)
    db.add(db_crypto)
    db.commit()
    db.refresh(db_crypto)
    return db_crypto

# Read operations
def get_cryptocurrency(db: Session, crypto_id: int) -> Optional[Cryptocurrency]:
    """
    Get a cryptocurrency by its ID
    """
    return db.query(Cryptocurrency).filter(Cryptocurrency.id == crypto_id).first()

def get_cryptocurrencies(db: Session, skip: int = 0, limit: int = 100) -> List[Cryptocurrency]:
    """
    Get a list of cryptocurrencies with pagination
    """
    return db.query(Cryptocurrency).offset(skip).limit(limit).all()

# Update operations
def update_cryptocurrency(db: Session, crypto_id: int, crypto_data: Dict[str, Any]) -> Optional[Cryptocurrency]:
    """
    Update a cryptocurrency by its ID
    """
    db_crypto = get_cryptocurrency(db, crypto_id)
    if db_crypto:
        for key, value in crypto_data.items():
            setattr(db_crypto, key, value)
        db.commit()
        db.refresh(db_crypto)
    return db_crypto

# Delete operations
def delete_cryptocurrency(db: Session, crypto_id: int) -> bool:
    """
    Delete a cryptocurrency by its ID
    """
    db_crypto = get_cryptocurrency(db, crypto_id)
    if db_crypto:
        db.delete(db_crypto)
        db.commit()
        return True
    return False 