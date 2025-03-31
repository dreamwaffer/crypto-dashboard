import logging
from typing import Dict, Any

from app.worker.celery_app import celery_app
from app.db.base import SessionLocal
from app.crud import crud_crypto
from app.services import coingecko

logger = logging.getLogger(__name__)


@celery_app.task(acks_late=True)
def update_all_crypto_prices():
    """
    Celery task to fetch current prices for all tracked cryptocurrencies
    from CoinGecko and update them in the database.
    """
    logger.info("Starting periodic task: update_all_crypto_prices")
    db = SessionLocal()
    updated_count = 0
    try:

        coingecko_ids = crud_crypto.get_all_crypto_coingecko_ids(db)
        if not coingecko_ids:
            logger.info("No cryptocurrencies with coingecko_ids found in DB. Skipping price update.")
            return {"message": "No coins to update."}

        logger.info(f"Found {len(coingecko_ids)} coingecko_ids to update prices for.")

        prices_data = coingecko.get_prices(coingecko_ids=coingecko_ids, vs_currency="usd")
        logger.debug(f"Received prices data: {prices_data}") # Changed print to debug

        if not prices_data:
            logger.warning("Received no price data from CoinGecko.")
            return {"message": "Failed to fetch price data from CoinGecko."}

        updates_for_db: Dict[str, Dict[str, Any]] = {}
        for cg_id, price_info in prices_data.items():
            if "usd" in price_info:
                updates_for_db[cg_id] = {"current_price_usd": price_info["usd"]}
            else:
                logger.warning(f"USD price not found for coingecko_id: {cg_id}")

        if not updates_for_db:
            logger.info("No prices found in the expected format from CoinGecko response.")
            return {"message": "No valid price data to update."}

        logger.info(f"Attempting to update coin_metadata for {len(updates_for_db)} cryptocurrencies.")
        updated_count = crud_crypto.update_crypto_metadata_batch(db=db, updates=updates_for_db)
        logger.info(f"Successfully updated coin_metadata for {updated_count} cryptocurrencies.")

    except Exception as e:
        logger.error(f"Error during update_all_crypto_prices task: {e}", exc_info=True)

        raise
    finally:
        db.close()

    return {"message": f"Price update task completed. Updated {updated_count} records."}
