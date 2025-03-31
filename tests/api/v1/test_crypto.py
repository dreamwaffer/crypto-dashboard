import pytest
from unittest.mock import patch, MagicMock
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import crud_crypto
from app.db import models

API_V1_STR = settings.API_V1_STR
CRYPTO_ENDPOINT = f"{API_V1_STR}/cryptocurrencies"


@pytest.fixture(autouse=True)
def mock_coingecko_search():
    """Mocks coingecko.search_coin to return a predefined result."""
    with patch("app.api.routers.crypto.coingecko.search_coin") as mock_search:
        def side_effect(symbol):
            if symbol.upper() == "BTC":
                return ("bitcoin", "Bitcoin")
            elif symbol.upper() == "ETH":
                return ("ethereum", "Ethereum")
            elif symbol.upper() == "UNKNOWN":
                return None
            else:
                return (f"{symbol.lower()}_id", f"{symbol.capitalize()} Name")

        mock_search.side_effect = side_effect
        yield mock_search


@pytest.fixture(autouse=True)
def mock_coingecko_prices():
    """Mocks coingecko.get_prices to return predefined prices."""
    with patch("app.api.routers.crypto.coingecko.get_prices") as mock_prices:
        mock_prices.return_value = {
            "bitcoin": {"usd": 50000.0},
            "ethereum": {"usd": 4000.0},
        }
        yield mock_prices


@pytest.fixture(autouse=True)
def mock_coingecko_details():
    """Mocks coingecko.get_coin_details to return predefined details."""
    with patch("app.api.routers.crypto.coingecko.get_coin_details") as mock_details:
        mock_details.return_value = {
            "image": {"thumb": "http://example.com/thumb.png", "small": "http://example.com/small.png",
                      "large": "http://example.com/large.png"}
        }
        yield mock_details


@pytest.fixture
def test_crypto_btc(db_session: Session) -> models.Cryptocurrency:
    """Creates a test BTC record in the DB."""
    return crud_crypto.create_crypto(
        db=db_session,
        symbol="BTC",
        name="Bitcoin",
        coingecko_id="bitcoin",
        coin_metadata={"current_price_usd": 50000.0, "image": {"thumb": "...", "small": "...", "large": "..."}},
        note="Test BTC"
    )


@pytest.fixture
def test_crypto_eth(db_session: Session) -> models.Cryptocurrency:
    """Creates a test ETH record in the DB."""
    return crud_crypto.create_crypto(
        db=db_session,
        symbol="ETH",
        name="Ethereum",
        coingecko_id="ethereum",
        coin_metadata={"current_price_usd": 4000.0, "image": {"thumb": "...", "small": "...", "large": "..."}},
        note="Test ETH"
    )


def test_create_cryptocurrency_success(client: TestClient, db_session: Session, mock_coingecko_search: MagicMock,
                                       mock_coingecko_prices: MagicMock, mock_coingecko_details: MagicMock):
    """Test successful creation of a new cryptocurrency (e.g., ETH)."""
    crypto_data = {"symbol": "ETH", "note": "My Ethereum"}
    response = client.post(CRYPTO_ENDPOINT + "/", json=crypto_data)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["symbol"] == "ETH"
    assert data["name"] == "Ethereum"
    assert data["coingecko_id"] == "ethereum"
    assert data["note"] == "My Ethereum"
    assert "current_price_usd" in data["coin_metadata"]
    assert data["coin_metadata"]["current_price_usd"] == 4000.0
    assert "image" in data["coin_metadata"]

    mock_coingecko_search.assert_called_once_with(symbol="ETH")
    mock_coingecko_prices.assert_called_once_with(coingecko_ids=["ethereum"], vs_currency="usd")
    mock_coingecko_details.assert_called_once_with(coingecko_id="ethereum")

    db_obj = crud_crypto.get_crypto_by_symbol(db_session, symbol="ETH")
    assert db_obj is not None
    assert db_obj.symbol == "ETH"
    assert db_obj.name == "Ethereum"


def test_create_cryptocurrency_duplicate_symbol(client: TestClient, test_crypto_btc: models.Cryptocurrency):
    """Test creating a crypto with an already existing symbol."""
    crypto_data = {"symbol": "BTC", "note": "Duplicate BTC"}
    response = client.post(CRYPTO_ENDPOINT + "/", json=crypto_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


def test_create_cryptocurrency_symbol_not_found(client: TestClient, mock_coingecko_search: MagicMock):
    """Test creating a crypto with a symbol not found on CoinGecko."""
    crypto_data = {"symbol": "UNKNOWN", "note": "Unknown coin"}
    response = client.post(CRYPTO_ENDPOINT + "/", json=crypto_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found on CoinGecko" in response.json()["detail"]
    mock_coingecko_search.assert_called_once_with(symbol="UNKNOWN")


def test_read_cryptocurrencies(client: TestClient, test_crypto_btc: models.Cryptocurrency,
                               test_crypto_eth: models.Cryptocurrency):
    """Test retrieving a list of cryptocurrencies."""
    response = client.get(CRYPTO_ENDPOINT + "/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    symbols = [item["symbol"] for item in data]
    assert "BTC" in symbols
    assert "ETH" in symbols


def test_read_cryptocurrencies_pagination(client: TestClient, test_crypto_btc: models.Cryptocurrency,
                                          test_crypto_eth: models.Cryptocurrency):
    """Test pagination for retrieving cryptocurrencies."""

    client.post(CRYPTO_ENDPOINT + "/", json={"symbol": "ADA", "note": "Cardano"})
    client.post(CRYPTO_ENDPOINT + "/", json={"symbol": "DOT", "note": "Polkadot"})

    response = client.get(CRYPTO_ENDPOINT + "/?skip=0&limit=2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

    response = client.get(CRYPTO_ENDPOINT + "/?skip=2&limit=2")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


def test_read_cryptocurrency_success(client: TestClient, test_crypto_btc: models.Cryptocurrency):
    """Test retrieving a specific cryptocurrency by symbol."""
    response = client.get(f"{CRYPTO_ENDPOINT}/{test_crypto_btc.symbol}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == test_crypto_btc.symbol
    assert data["name"] == test_crypto_btc.name
    assert data["id"] == test_crypto_btc.id


def test_read_cryptocurrency_not_found(client: TestClient):
    """Test retrieving a non-existent cryptocurrency."""
    response = client.get(f"{CRYPTO_ENDPOINT}/NONEXISTENT")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]


def test_update_cryptocurrency_success(client: TestClient, test_crypto_btc: models.Cryptocurrency, db_session: Session):
    """Test successfully updating a cryptocurrency's note."""
    update_data = {"note": "Updated BTC note"}
    response = client.put(f"{CRYPTO_ENDPOINT}/{test_crypto_btc.symbol}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == test_crypto_btc.symbol
    assert data["note"] == "Updated BTC note"
    assert data["id"] == test_crypto_btc.id

    db_session.refresh(test_crypto_btc)
    assert test_crypto_btc.note == "Updated BTC note"


def test_update_cryptocurrency_not_found(client: TestClient):
    """Test updating a non-existent cryptocurrency."""
    update_data = {"note": "Note for non-existent"}
    response = client.put(f"{CRYPTO_ENDPOINT}/NONEXISTENT", json=update_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]


def test_delete_cryptocurrency_success(client: TestClient, test_crypto_btc: models.Cryptocurrency, db_session: Session):
    """Test successfully deleting a cryptocurrency."""
    response = client.delete(f"{CRYPTO_ENDPOINT}/{test_crypto_btc.symbol}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == test_crypto_btc.symbol
    assert data["id"] == test_crypto_btc.id

    db_obj = crud_crypto.get_crypto(db_session, crypto_id=test_crypto_btc.id)
    assert db_obj is None


def test_delete_cryptocurrency_not_found(client: TestClient):
    """Test deleting a non-existent cryptocurrency."""
    response = client.delete(f"{CRYPTO_ENDPOINT}/NONEXISTENT")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]
