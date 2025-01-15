import pytest
from unittest.mock import patch
from sqlalchemy.engine.base import Engine


@pytest.fixture
def mock_engine():
    """Fixture qui retourne un moteur SQLAlchemy factice"""
    with patch(
        "btc_functions.load_database.mysql.create_connection"
    ) as mock_create_engine:
        yield mock_create_engine.return_value
