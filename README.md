# Crypto Dashboard API

This project is my solution to a task given to me by a potentional employer to prove my skills. This API is used to manage a list of cryptocurrencies, fetch their current prices and metadata via the CoinGecko API, and store this information in a database.

## Features

*   Create, Read, Update, and Delete (CRUD) operations for cryptocurrency records.
*   Automatic symbol validation and fetching of basic data (name, ID) from CoinGecko when adding a cryptocurrency.
*   Storing metadata (current price, image) in the database.
*   Asynchronous task for periodic price updates.

## Requirements

*   Docker
*   Docker Compose

## Running

1.  **Run using Docker Compose:** In your terminal, navigate to the `crypto_api` directory and run:
    ```bash
    docker-compose up -d --build
    ```

2.  **The API will be available at:** `http://localhost:8000`

3.  **Interactive documentation (Swagger UI):** `http://localhost:8000/docs`

## Tests

1.  In your terminal, navigate to the root of this project and run:
    ```bash
    pytest
    ```
