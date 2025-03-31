import httpx
from typing import Optional, Dict, Any, List, Tuple

from app.core.config import settings

sync_client = httpx.Client(base_url=settings.COINGECKO_API_BASE_URL, timeout=10.0)


def search_coin(symbol: str) -> Optional[Tuple[str, str]]:
    """
    Searches for a coin on CoinGecko using the /search endpoint (synchronous).
    Returns a tuple (coingecko_id, name) if found and matches the symbol closely, otherwise None.
    """
    try:

        response = sync_client.get("/search", params={"query": symbol})
        response.raise_for_status()
        data = response.json()

        if data and "coins" in data and data["coins"]:

            for coin in data["coins"]:

                if coin.get("symbol", "").lower() == symbol.lower():

                    coingecko_id = coin.get("api_symbol", coin.get("id"))
                    if coingecko_id and coin.get("name"):
                        return coingecko_id, coin["name"]

    except httpx.HTTPStatusError as e:
        print(f"HTTP error searching for coin {symbol}: {e.response.status_code} - {e.response.text}")

    except httpx.RequestError as e:
        print(f"Request error searching for coin {symbol}: {e}")
    except Exception as e:
        print(f"Unexpected error searching for coin {symbol}: {e}")

    return None


def get_coin_details(coingecko_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches detailed information for a coin using its coingecko_id (/coins/{id}) (synchronous).
    Returns a dictionary with details (like image URL) or None if error.
    """
    if not coingecko_id:
        return None
    try:

        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "false",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "false"
        }

        response = sync_client.get(f"/coins/{coingecko_id}", params=params)
        response.raise_for_status()
        data = response.json()

        return {
            "image": data.get("image", {}).get("large")
        }
    except httpx.HTTPStatusError as e:
        print(f"HTTP error getting details for {coingecko_id}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Request error getting details for {coingecko_id}: {e}")
    except Exception as e:
        print(f"Unexpected error getting details for {coingecko_id}: {e}")
    return None


def get_prices(coingecko_ids: List[str], vs_currency: str = "usd") -> Dict[str, Dict[str, float]]:
    """
    Fetches current prices for a list of coingecko_ids using /simple/price (synchronous).
    Returns a dictionary mapping coingecko_id to its price dict, e.g.,
    {'bitcoin': {'usd': 60000.0}, 'ethereum': {'usd': 4000.0}}
    Returns an empty dict if error or no IDs provided.
    """
    if not coingecko_ids:
        return {}

    try:
        ids_param = ",".join(coingecko_ids)
        params = {
            "ids": ids_param,
            "vs_currencies": vs_currency
        }

        response = sync_client.get("/simple/price", params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except httpx.HTTPStatusError as e:
        print(f"HTTP error getting prices for {coingecko_ids}: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        print(f"Request error getting prices for {coingecko_ids}: {e}")
    except Exception as e:
        print(f"Unexpected error getting prices for {coingecko_ids}: {e}")
    return {}
