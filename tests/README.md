# Testing Framework for Crypto API

This folder contains tests for Crypto API, divided by test type into individual subfolders.

## Test Structure

```
tests/
├── common/              # Shared components and data for tests
│   ├── __init__.py
│   └── test_data.py     # Test data
├── unit/                # Unit tests (testing individual components in isolation)
│   ├── __init__.py
│   ├── test_crud.py     # Tests for CRUD operations using mocks
│   ├── test_api_endpoints.py  # Tests for API endpoints using mocks
│   └── test_schemas.py  # Tests for schema validation
├── integration/         # Integration tests (testing interaction between components)
│   ├── __init__.py
│   └── test_cryptocurrencies.py  # End-to-end tests of API with DB
├── conftest.py          # Global pytest configuration
└── README.md            # This file
```

## Test Types

### Unit Tests

Unit tests test individual system components in isolation. They use mock objects to replace dependencies. Their goal is to verify that each component works correctly on its own.

- `test_crud.py` - Tests CRUD database operations using mock objects
- `test_api_endpoints.py` - Tests API endpoints with mocked CRUD operations
- `test_schemas.py` - Tests Pydantic schema validation

### Integration Tests

Integration tests test interactions between system components. They use a real database (SQLite in memory) but have no external dependencies. Their goal is to verify that components work together correctly.

- `test_cryptocurrencies.py` - Tests end-to-end flow of API endpoints with database

## Running Tests

### Running All Tests

```bash
python -m pytest
```

### Running Only Unit Tests

```bash
python -m pytest tests/unit/
```

### Running Only Integration Tests

```bash
python -m pytest tests/integration/
```

### Running with Code Coverage

```bash
python -m pytest --cov=app
```

## Test Data

Test data is defined in `tests/common/test_data.py` and used across all tests to ensure consistency. 