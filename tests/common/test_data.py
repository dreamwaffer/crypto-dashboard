"""
Test data for unit tests
"""

# Test data for cryptocurrencies
SAMPLE_CRYPTOCURRENCIES = [
    {
        "symbol": "BTC",
        "name": "Bitcoin",
        "coingecko_id": "bitcoin",
        "notes": "First cryptocurrency"
    },
    {
        "symbol": "ETH",
        "name": "Ethereum",
        "coingecko_id": "ethereum",
        "notes": "Smart contract platform"
    },
    {
        "symbol": "XRP",
        "name": "Ripple",
        "coingecko_id": "ripple",
        "notes": "Payment network"
    },
    {
        "symbol": "DOGE",
        "name": "Dogecoin",
        "coingecko_id": "dogecoin",
        "notes": "Meme cryptocurrency"
    }
]

# Data for creating a new cryptocurrency
NEW_CRYPTOCURRENCY = {
    "symbol": "ADA",
    "name": "Cardano",
    "notes": "Proof-of-Stake blockchain platform"
}

# Data for updating a cryptocurrency
UPDATE_CRYPTOCURRENCY = {
    "notes": "Updated description"
} 