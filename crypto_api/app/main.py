from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routers import crypto as crypto_router
from app.services import coingecko
from app.db.base import Base, engine, SessionLocal
from app.crud import crud_crypto
from app.db import models


def create_db_and_tables():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created or already exist.")
    except Exception as e:
        print(f"Error creating database tables: {e}")


def seed_db():
    """Seeds the database with initial data if it's empty."""
    db = SessionLocal()
    try:
        count = db.query(models.Cryptocurrency).count()
        if count == 0:
            print("Database is empty, seeding initial data...")
            initial_symbols = ["BTC", "ETH"]
            for symbol in initial_symbols:
                try:
                    print(f"Attempting to seed {symbol}...")

                    existing = crud_crypto.get_crypto_by_symbol(db, symbol=symbol)
                    if existing:
                        print(f"{symbol} already exists, skipping seed.")
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
                        print(f"Successfully seeded {symbol}")
                    else:
                        print(f"Could not find {symbol} on CoinGecko during seeding.")
                except Exception as seed_error:
                    print(f"Error seeding {symbol}: {seed_error}")
                    db.rollback()
            print("Initial data seeding complete.")
        else:
            print(f"Database contains {count} records, skipping seeding.")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    create_db_and_tables()
    seed_db()

    yield

    print("Application shutdown...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crypto_router.router, prefix=settings.API_V1_STR + "/cryptocurrencies", tags=["cryptocurrencies"])


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
