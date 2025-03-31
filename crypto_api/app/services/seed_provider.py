import logging
from app.services import coingecko
from app.db.base import SessionLocal
from app.crud import crud_crypto
from app.db import models

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(name)s: %(message)s')
logger = logging.getLogger(__name__)

def seed_db():
    """Seeds the database with initial data if it's empty."""
    db = SessionLocal()
    try:
        count = db.query(models.Cryptocurrency).count()
        if count == 0:
            logger.info("Database is empty, seeding initial data...")
            initial_symbols = ["BTC", "ETH"]
            for symbol in initial_symbols:
                try:
                    logger.info(f"Attempting to seed {symbol}...")

                    existing = crud_crypto.get_crypto(db, symbol=symbol)
                    if existing:
                        logger.info(f"{symbol} already exists, skipping seed.")
                        continue

                    search_result = coingecko.search_coin(symbol=symbol)
                    if search_result:
                        coingecko_id, name = search_result
                        coin_metadata = {}
                        prices = coingecko.get_prices(coingecko_ids=[coingecko_id], vs_currency="usd")
                        if coingecko_id in prices and "usd" in prices[coingecko_id]:
                            coin_metadata["current_price_usd"] = prices[coingecko_id]["usd"]
                        details = coingecko.get_coin_details(coingecko_id=coingecko_id)
                        if details and details.get("image"):
                            coin_metadata["image"] = details["image"]

                        crud_crypto.create_crypto(
                            db=db,
                            symbol=symbol,
                            name=name,
                            coingecko_id=coingecko_id,
                            coin_metadata=coin_metadata,
                            note=f"Initial seed for {symbol}"
                        )
                        logger.info(f"Successfully seeded {symbol}")
                    else:
                        logger.warning(f"Could not find {symbol} on CoinGecko during seeding.")
                except Exception as seed_error:
                    logger.error(f"Error seeding {symbol}: {seed_error}", exc_info=True)
                    db.rollback()
            logger.info("Initial data seeding complete.")
        else:
            logger.info(f"Database contains {count} records, skipping seeding.")
    finally:
        db.close()