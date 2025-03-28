import pytest
import os


# Setting up the test environment
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Sets up the test environment before running all tests
    """
    # Set environment to test
    os.environ["ENVIRONMENT"] = "test"

    # We can perform additional initializations for the test here
    yield

    # Cleanup after tests
    test_db_path = "test.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
