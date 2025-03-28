import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from app.db import crud
from app.db.models.cryptocurrency import Cryptocurrency
from tests.common.test_data import SAMPLE_CRYPTOCURRENCIES, NEW_CRYPTOCURRENCY, UPDATE_CRYPTOCURRENCY


class TestCrudOperations:
    """
    Unit tests for CRUD operations
    Using mock objects instead of a real database
    """
    
    def test_get_cryptocurrency_by_symbol(self):
        # Prepare mock for session and query
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_first = MagicMock()
        
        # Set expected behavior and return values
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = Cryptocurrency(
            id=1,
            symbol=SAMPLE_CRYPTOCURRENCIES[0]["symbol"],
            name=SAMPLE_CRYPTOCURRENCIES[0]["name"],
            coingecko_id=SAMPLE_CRYPTOCURRENCIES[0]["coingecko_id"],
            notes=SAMPLE_CRYPTOCURRENCIES[0]["notes"]
        )
        
        # Call the tested function
        result = crud.get_cryptocurrency_by_symbol(mock_db, SAMPLE_CRYPTOCURRENCIES[0]["symbol"])
        
        # Verify that the function uses the session correctly
        mock_db.query.assert_called_once_with(Cryptocurrency)
        mock_query.filter.assert_called_once()
        
        # Verify the result
        assert result is not None
        assert result.symbol == SAMPLE_CRYPTOCURRENCIES[0]["symbol"]
        assert result.name == SAMPLE_CRYPTOCURRENCIES[0]["name"]
    
    def test_get_cryptocurrency_by_symbol_not_found(self):
        # Prepare mock for session and query
        mock_db = MagicMock(spec=Session)
        mock_query = MagicMock()
        mock_filter = MagicMock()
        
        # Set expected behavior and return values for cryptocurrency not found
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        # Call the tested function
        result = crud.get_cryptocurrency_by_symbol(mock_db, "NONEXISTENT")
        
        # Verify that the function uses the session correctly
        mock_db.query.assert_called_once_with(Cryptocurrency)
        mock_query.filter.assert_called_once()
        
        # Verify the result
        assert result is None
    
    def test_create_cryptocurrency(self):
        # Prepare mock for session
        mock_db = MagicMock(spec=Session)
        
        # Data for creating a cryptocurrency
        crypto_data = {
            "symbol": NEW_CRYPTOCURRENCY["symbol"],
            "name": NEW_CRYPTOCURRENCY["name"],
            "coingecko_id": NEW_CRYPTOCURRENCY["symbol"].lower(),
            "notes": NEW_CRYPTOCURRENCY["notes"]
        }
        
        # Call the tested function
        result = crud.create_cryptocurrency(mock_db, crypto_data)
        
        # Verify that the function uses the session correctly
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        
        # Verify the result
        assert result is not None
        assert result.symbol == NEW_CRYPTOCURRENCY["symbol"]
        assert result.name == NEW_CRYPTOCURRENCY["name"]
    
    def test_update_cryptocurrency_by_symbol(self):
        # Prepare mock objects
        mock_db = MagicMock(spec=Session)
        mock_crypto = MagicMock(spec=Cryptocurrency)
        mock_crypto.symbol = SAMPLE_CRYPTOCURRENCIES[0]["symbol"]
        mock_crypto.name = SAMPLE_CRYPTOCURRENCIES[0]["name"]  # Name should not change
        
        # Set return value for get_cryptocurrency_by_symbol
        with patch('app.db.crud.get_cryptocurrency_by_symbol', return_value=mock_crypto):
            # Data for update
            update_data = {
                "notes": UPDATE_CRYPTOCURRENCY["notes"]
            }
            
            # Call the tested function
            result = crud.update_cryptocurrency_by_symbol(mock_db, SAMPLE_CRYPTOCURRENCIES[0]["symbol"], update_data)
            
            # Verify that the function uses the session correctly
            mock_db.commit.assert_called_once()
            mock_db.refresh.assert_called_once()
            
            # Verify that values were set
            assert result is not None
            assert result.symbol == SAMPLE_CRYPTOCURRENCIES[0]["symbol"]
    
    def test_update_cryptocurrency_by_symbol_not_found(self):
        # Prepare mock objects
        mock_db = MagicMock(spec=Session)
        
        # Set return value for get_cryptocurrency_by_symbol
        with patch('app.db.crud.get_cryptocurrency_by_symbol', return_value=None):
            # Data for update
            update_data = {
                "notes": UPDATE_CRYPTOCURRENCY["notes"]
            }
            
            # Call the tested function
            result = crud.update_cryptocurrency_by_symbol(mock_db, "NONEXISTENT", update_data)
            
            # Verify that the session was not used
            mock_db.commit.assert_not_called()
            mock_db.refresh.assert_not_called()
            
            # Verify the result
            assert result is None
    
    def test_delete_cryptocurrency_by_symbol(self):
        # Prepare mock objects
        mock_db = MagicMock(spec=Session)
        mock_crypto = MagicMock(spec=Cryptocurrency)
        
        # Set return value for get_cryptocurrency_by_symbol
        with patch('app.db.crud.get_cryptocurrency_by_symbol', return_value=mock_crypto):
            # Call the tested function
            result = crud.delete_cryptocurrency_by_symbol(mock_db, SAMPLE_CRYPTOCURRENCIES[3]["symbol"])
            
            # Verify that the function uses the session correctly
            mock_db.delete.assert_called_once_with(mock_crypto)
            mock_db.commit.assert_called_once()
            
            # Verify the result
            assert result is True
    
    def test_delete_cryptocurrency_by_symbol_not_found(self):
        # Prepare mock objects
        mock_db = MagicMock(spec=Session)
        
        # Set return value for get_cryptocurrency_by_symbol
        with patch('app.db.crud.get_cryptocurrency_by_symbol', return_value=None):
            # Call the tested function
            result = crud.delete_cryptocurrency_by_symbol(mock_db, "NONEXISTENT")
            
            # Verify that the session was not used
            mock_db.delete.assert_not_called()
            mock_db.commit.assert_not_called()
            
            # Verify the result
            assert result is False 