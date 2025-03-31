# Crypto Dashboard API

Toto API slouží ke správě seznamu kryptoměn, získávání jejich aktuálních cen a metadat pomocí CoinGecko API a ukládání těchto informací do databáze.

## Funkce

*   Přidávání, čtení, aktualizace a mazání (CRUD) záznamů o kryptoměnách.
*   Automatické ověření symbolu a získání základních dat (název, ID) z CoinGecko při přidání.
*   Ukládání metadat (aktuální cena, obrázek) do databáze.
*   Asynchronní úloha pro pravidelnou aktualizaci cen.

## Požadavky

*   Docker
*   Docker Compose

## Spuštění
1.  **Spusťte pomocí Docker Compose:** V terminálu přejděte do adresáře `crypto_api` a spusťte:
    ```bash
    docker-compose up -d --build
    ```
    *   `-d` spustí kontejnery na pozadí.
    *   `--build` zajistí sestavení image, pokud ještě neexistuje nebo pokud se změnily závislosti.

   2.  **API bude dostupné na:** `http://localhost:8000`
   3.  **Interaktivní dokumentace (Swagger UI):** `http://localhost:8000/docs`