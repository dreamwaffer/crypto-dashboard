from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func

from .base import Base


class Cryptocurrency(Base):
    __tablename__ = "cryptocurrencies"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    coingecko_id = Column(String, unique=True, index=True, nullable=True)
    last_updated_coingecko = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    coin_metadata = Column(JSON, nullable=True)
    note = Column(String, nullable=True)
