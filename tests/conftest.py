import sys
import os
import pytest
from typing import Generator, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'crypto_api'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.db.base import Base, get_db
from app.main import app as main_app
from app.core.config import settings

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL
settings.DATABASE_URL = SQLALCHEMY_DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    Creates the database tables once per test session.
    """

    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, Any, None]:
    """
    Provides a clean database session for each test function.
    Manages transactions and ensures tables are dropped after each test.
    """

    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)

    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()

        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function", autouse=True)
def override_get_db_dependency(db_session: Session):
    """
    Automatically overrides the get_db dependency for each test function
    to use the isolated, transactional test database session.
    """

    def _override_get_db():
        try:
            yield db_session
        finally:

            pass

    original_override = main_app.dependency_overrides.get(get_db)

    main_app.dependency_overrides[get_db] = _override_get_db
    yield

    if original_override:
        main_app.dependency_overrides[get_db] = original_override
    else:
        main_app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def client() -> TestClient:
    """
    Provides a TestClient instance for making requests to the FastAPI application.
    Relies on the autouse override_get_db_dependency fixture.
    """
    return TestClient(main_app)
