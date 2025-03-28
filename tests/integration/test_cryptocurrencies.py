import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

from app.main import app
from app.db.base import Base, get_db
from app.db.models.cryptocurrency import Cryptocurrency
from tests.common.test_data import SAMPLE_CRYPTOCURRENCIES, NEW_CRYPTOCURRENCY, UPDATE_CRYPTOCURRENCY

# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Fixture for setting up the test database
@pytest.fixture(scope="function")
def db() -> Generator:
    # Create database and tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Clean up the database after each test
        Base.metadata.drop_all(bind=engine)


# Fixture for the API client
@pytest.fixture(scope="function")
def client(db) -> Generator:
    # Define a dependency for the database that uses the test db instead of production
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    # Replace the dependency
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a test client
    with TestClient(app) as c:
        yield c
    
    # Clean up
    app.dependency_overrides.clear()


# Test for creating a cryptocurrency
def test_create_cryptocurrency(client: TestClient, db):
    # Create a cryptocurrency through the API
    response = client.post("/api/v1/cryptocurrencies/", json=NEW_CRYPTOCURRENCY)
    
    # Verify that the creation was successful
    assert response.status_code == 201
    data = response.json()
    assert data["symbol"] == NEW_CRYPTOCURRENCY["symbol"]
    assert data["name"] == NEW_CRYPTOCURRENCY["name"]
    assert data["notes"] == NEW_CRYPTOCURRENCY["notes"]
    assert "id" in data
    assert "coingecko_id" in data


# Test for reading a cryptocurrency
def test_get_cryptocurrency(client: TestClient, db):
    # First, create a cryptocurrency directly in the DB
    crypto = Cryptocurrency(
        symbol=SAMPLE_CRYPTOCURRENCIES[0]["symbol"],
        name=SAMPLE_CRYPTOCURRENCIES[0]["name"],
        coingecko_id=SAMPLE_CRYPTOCURRENCIES[0]["coingecko_id"],
        notes=SAMPLE_CRYPTOCURRENCIES[0]["notes"]
    )
    db.add(crypto)
    db.commit()
    db.refresh(crypto)
    
    # Read the cryptocurrency through the API by symbol
    response = client.get(f"/api/v1/cryptocurrencies/{SAMPLE_CRYPTOCURRENCIES[0]['symbol']}")
    
    # Verify that the read was successful
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == SAMPLE_CRYPTOCURRENCIES[0]["symbol"]
    assert data["name"] == SAMPLE_CRYPTOCURRENCIES[0]["name"]
    assert data["notes"] == SAMPLE_CRYPTOCURRENCIES[0]["notes"]


# Test for updating a cryptocurrency
def test_update_cryptocurrency(client: TestClient, db):
    # First, create a cryptocurrency directly in the DB
    crypto = Cryptocurrency(
        symbol=SAMPLE_CRYPTOCURRENCIES[0]["symbol"],
        name=SAMPLE_CRYPTOCURRENCIES[0]["name"],
        coingecko_id=SAMPLE_CRYPTOCURRENCIES[0]["coingecko_id"],
        notes=SAMPLE_CRYPTOCURRENCIES[0]["notes"]
    )
    db.add(crypto)
    db.commit()
    db.refresh(crypto)
    
    # Update the cryptocurrency through the API
    response = client.put(
        f"/api/v1/cryptocurrencies/{SAMPLE_CRYPTOCURRENCIES[0]['symbol']}", 
        json=UPDATE_CRYPTOCURRENCY
    )
    
    # Verify that the update was successful
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == SAMPLE_CRYPTOCURRENCIES[0]["symbol"]
    assert data["name"] == SAMPLE_CRYPTOCURRENCIES[0]["name"]  # Name should not change
    assert data["notes"] == UPDATE_CRYPTOCURRENCY["notes"]
    
    # Verify that the changes are saved in the DB
    db_crypto = db.query(Cryptocurrency).filter(
        Cryptocurrency.symbol == SAMPLE_CRYPTOCURRENCIES[0]["symbol"]
    ).first()
    assert db_crypto.name == SAMPLE_CRYPTOCURRENCIES[0]["name"]  # Name should not change
    assert db_crypto.notes == UPDATE_CRYPTOCURRENCY["notes"]


# Test for deleting a cryptocurrency
def test_delete_cryptocurrency(client: TestClient, db):
    # First, create a cryptocurrency directly in the DB
    crypto = Cryptocurrency(
        symbol=SAMPLE_CRYPTOCURRENCIES[3]["symbol"],
        name=SAMPLE_CRYPTOCURRENCIES[3]["name"],
        coingecko_id=SAMPLE_CRYPTOCURRENCIES[3]["coingecko_id"],
        notes=SAMPLE_CRYPTOCURRENCIES[3]["notes"]
    )
    db.add(crypto)
    db.commit()
    db.refresh(crypto)
    
    # Delete the cryptocurrency through the API
    response = client.delete(f"/api/v1/cryptocurrencies/{SAMPLE_CRYPTOCURRENCIES[3]['symbol']}")
    
    # Verify that the deletion was successful
    assert response.status_code == 204
    
    # Verify that the cryptocurrency was actually deleted from the DB
    db_crypto = db.query(Cryptocurrency).filter(
        Cryptocurrency.symbol == SAMPLE_CRYPTOCURRENCIES[3]["symbol"]
    ).first()
    assert db_crypto is None


# Test for getting a list of cryptocurrencies
def test_list_cryptocurrencies(client: TestClient, db):
    # Create several cryptocurrencies directly in the DB
    cryptos = []
    for crypto_data in SAMPLE_CRYPTOCURRENCIES[:3]:  # Use the first 3 cryptocurrencies
        crypto = Cryptocurrency(
            symbol=crypto_data["symbol"],
            name=crypto_data["name"],
            coingecko_id=crypto_data["coingecko_id"],
            notes=crypto_data["notes"]
        )
        cryptos.append(crypto)
    
    db.add_all(cryptos)
    db.commit()
    
    # Get the list of cryptocurrencies through the API
    response = client.get("/api/v1/cryptocurrencies/")
    
    # Verify that getting the list was successful
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] == 3
    assert len(data["items"]) == 3
    
    # Verify that the list contains the expected cryptocurrencies
    symbols = [item["symbol"] for item in data["items"]]
    for crypto_data in SAMPLE_CRYPTOCURRENCIES[:3]:
        assert crypto_data["symbol"] in symbols


# Test for a non-existent cryptocurrency
def test_get_nonexistent_cryptocurrency(client: TestClient, db):
    # Attempt to read a non-existent cryptocurrency
    response = client.get("/api/v1/cryptocurrencies/NONEXISTENT")
    
    # Verify that the API returns 404
    assert response.status_code == 404 