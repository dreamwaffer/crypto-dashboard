import pytest
from unittest.mock import patch, MagicMock, ANY
from fastapi.testclient import TestClient
from fastapi import status
from datetime import datetime

from app.main import app
from tests.common.test_data import SAMPLE_CRYPTOCURRENCIES, NEW_CRYPTOCURRENCY, UPDATE_CRYPTOCURRENCY


@pytest.fixture
def client():
    """Fixture for FastAPI test client"""
    return TestClient(app)


class TestCryptocurrencyEndpoints:
    """
    Unit tests for cryptocurrency API endpoints
    Using mock objects instead of a real database
    """
    
    @patch("app.api.endpoints.cryptocurrencies.crud.get_cryptocurrency_by_symbol")
    def test_get_cryptocurrency(self, mock_get_crypto, client):
        # Prepare cryptocurrency mock object
        mock_crypto = MagicMock()
        mock_crypto.id = 1
        mock_crypto.symbol = SAMPLE_CRYPTOCURRENCIES[0]["symbol"]
        mock_crypto.name = SAMPLE_CRYPTOCURRENCIES[0]["name"]
        mock_crypto.coingecko_id = SAMPLE_CRYPTOCURRENCIES[0]["coingecko_id"]
        mock_crypto.notes = SAMPLE_CRYPTOCURRENCIES[0]["notes"]
        mock_crypto.image_url = "https://example.com/btc.png"
        mock_crypto.current_price = 50000.0
        mock_crypto.market_cap = 1000000000.0
        mock_crypto.total_volume = 50000000.0
        mock_crypto.price_change_24h = 2.5
        mock_crypto.last_updated = datetime.now()
        
        # Set return value for mocked function
        mock_get_crypto.return_value = mock_crypto
        
        # Call API endpoint
        response = client.get(f"/api/v1/cryptocurrencies/{SAMPLE_CRYPTOCURRENCIES[0]['symbol']}")
        
        # Verify result
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["symbol"] == SAMPLE_CRYPTOCURRENCIES[0]["symbol"]
        assert data["name"] == SAMPLE_CRYPTOCURRENCIES[0]["name"]
        
        # Verify that the function was called with correct parameters
        mock_get_crypto.assert_called_once()
    
    @patch("app.api.endpoints.cryptocurrencies.crud.get_cryptocurrency_by_symbol")
    def test_get_cryptocurrency_not_found(self, mock_get_crypto, client):
        # Set return value for mocked function
        mock_get_crypto.return_value = None
        
        # Call API endpoint
        response = client.get("/api/v1/cryptocurrencies/NONEXISTENT")
        
        # Verify result
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify that the function was called with correct parameters
        mock_get_crypto.assert_called_once()
    
    @patch("app.api.endpoints.cryptocurrencies.crud.create_cryptocurrency")
    def test_create_cryptocurrency(self, mock_create_crypto, client):
        # Prepare cryptocurrency mock object
        mock_crypto = MagicMock()
        mock_crypto.id = 1
        mock_crypto.symbol = NEW_CRYPTOCURRENCY["symbol"]
        mock_crypto.name = NEW_CRYPTOCURRENCY["name"]
        mock_crypto.coingecko_id = NEW_CRYPTOCURRENCY["symbol"].lower()
        mock_crypto.notes = NEW_CRYPTOCURRENCY["notes"]
        mock_crypto.image_url = "https://example.com/ada.png"
        mock_crypto.current_price = 1.5
        mock_crypto.market_cap = 50000000.0
        mock_crypto.total_volume = 10000000.0
        mock_crypto.price_change_24h = 1.2
        mock_crypto.last_updated = datetime.now()
        
        # Set return value for mocked function
        mock_create_crypto.return_value = mock_crypto
        
        # Call API endpoint
        response = client.post("/api/v1/cryptocurrencies/", json=NEW_CRYPTOCURRENCY)
        
        # Verify result
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["symbol"] == NEW_CRYPTOCURRENCY["symbol"]
        assert data["name"] == NEW_CRYPTOCURRENCY["name"]
        
        # Verify that the function was called with correct parameters
        mock_create_crypto.assert_called_once()
    
    @patch("app.api.endpoints.cryptocurrencies.crud.update_cryptocurrency_by_symbol")
    def test_update_cryptocurrency(self, mock_update_crypto, client):
        # Prepare cryptocurrency mock object
        mock_crypto = MagicMock()
        mock_crypto.id = 1
        mock_crypto.symbol = SAMPLE_CRYPTOCURRENCIES[0]["symbol"]
        mock_crypto.name = SAMPLE_CRYPTOCURRENCIES[0]["name"]  # Name should not change
        mock_crypto.notes = UPDATE_CRYPTOCURRENCY["notes"]
        mock_crypto.coingecko_id = SAMPLE_CRYPTOCURRENCIES[0]["coingecko_id"]
        mock_crypto.image_url = "https://example.com/btc.png"
        mock_crypto.current_price = 50000.0
        mock_crypto.market_cap = 1000000000.0
        mock_crypto.total_volume = 50000000.0
        mock_crypto.price_change_24h = 2.5
        mock_crypto.last_updated = datetime.now()
        
        # Set return value for mocked function
        mock_update_crypto.return_value = mock_crypto
        
        # Call API endpoint
        response = client.put(
            f"/api/v1/cryptocurrencies/{SAMPLE_CRYPTOCURRENCIES[0]['symbol']}",
            json=UPDATE_CRYPTOCURRENCY
        )
        
        # Verify result
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["symbol"] == SAMPLE_CRYPTOCURRENCIES[0]["symbol"]
        assert data["name"] == SAMPLE_CRYPTOCURRENCIES[0]["name"]  # Name should not change
        assert data["notes"] == UPDATE_CRYPTOCURRENCY["notes"]
        
        # Verify that the function was called with correct parameters
        mock_update_crypto.assert_called_once()
    
    @patch("app.api.endpoints.cryptocurrencies.crud.update_cryptocurrency_by_symbol")
    def test_update_cryptocurrency_not_found(self, mock_update_crypto, client):
        # Set return value for mocked function
        mock_update_crypto.return_value = None
        
        # Call API endpoint
        response = client.put(
            "/api/v1/cryptocurrencies/NONEXISTENT",
            json=UPDATE_CRYPTOCURRENCY
        )
        
        # Verify result
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify that the function was called with correct parameters
        mock_update_crypto.assert_called_once()
    
    @patch("app.api.endpoints.cryptocurrencies.crud.delete_cryptocurrency_by_symbol")
    def test_delete_cryptocurrency(self, mock_delete_crypto, client):
        # Set return value for mocked function
        mock_delete_crypto.return_value = True
        
        # Call API endpoint
        response = client.delete(f"/api/v1/cryptocurrencies/{SAMPLE_CRYPTOCURRENCIES[3]['symbol']}")
        
        # Verify result
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify that the function was called with correct parameters
        mock_delete_crypto.assert_called_once_with(ANY, SAMPLE_CRYPTOCURRENCIES[3]['symbol'].upper())
    
    @patch("app.api.endpoints.cryptocurrencies.crud.delete_cryptocurrency_by_symbol")
    def test_delete_cryptocurrency_not_found(self, mock_delete_crypto, client):
        # Set return value for mocked function
        mock_delete_crypto.return_value = False
        
        # Call API endpoint
        response = client.delete("/api/v1/cryptocurrencies/NONEXISTENT")
        
        # Verify result
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify that the function was called with correct parameters
        mock_delete_crypto.assert_called_once_with(ANY, "NONEXISTENT")
    
    @patch("app.api.endpoints.cryptocurrencies.crud.get_cryptocurrencies")
    def test_list_cryptocurrencies(self, mock_get_cryptos, client):
        # Prepare cryptocurrency mock objects
        mock_cryptos = []
        for i, crypto_data in enumerate(SAMPLE_CRYPTOCURRENCIES[:3]):
            mock_crypto = MagicMock()
            mock_crypto.id = i + 1
            mock_crypto.symbol = crypto_data["symbol"]
            mock_crypto.name = crypto_data["name"]
            mock_crypto.coingecko_id = crypto_data["coingecko_id"]
            mock_crypto.notes = crypto_data["notes"]
            mock_crypto.image_url = f"https://example.com/{crypto_data['symbol'].lower()}.png"
            mock_crypto.current_price = 50000.0 / (i + 1)
            mock_crypto.market_cap = 1000000000.0 / (i + 1)
            mock_crypto.total_volume = 50000000.0 / (i + 1)
            mock_crypto.price_change_24h = 2.5 - i
            mock_crypto.last_updated = datetime.now()
            mock_cryptos.append(mock_crypto)
        
        # Set return value for mocked function
        mock_get_cryptos.return_value = mock_cryptos
        
        # Call API endpoint
        response = client.get("/api/v1/cryptocurrencies/")
        
        # Verify result
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 3
        assert len(data["items"]) == 3
        
        # Verify that the function was called with correct parameters
        mock_get_cryptos.assert_called_once() 