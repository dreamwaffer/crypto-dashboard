from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.sql import func

from app.db.base import Base

class Cryptocurrency(Base):
    """
    SQLAlchemy model for cryptocurrency table
    """
    __tablename__ = "cryptocurrencies"

    id = Column(Integer, primary_key=True, index=True)
    coingecko_id = Column(String(100), unique=True, index=True, nullable=False)
    symbol = Column(String(20), index=True, nullable=False)
    name = Column(String(100), nullable=False)
    current_price = Column(Float)
    market_cap = Column(Float)
    total_volume = Column(Float)
    price_change_24h = Column(Float)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    image_url = Column(String(255))
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Cryptocurrency(symbol={self.symbol}, name={self.name})>" 