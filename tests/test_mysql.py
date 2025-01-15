import pytest
from unittest.mock import patch
from btc_functions.load_database.mysql import create_connection, close_engine


@patch(
    "btc_functions.load_database.mysql.os.getenv",
    side_effect=lambda key: "test_value" if key != "DB_PORT" else "3306",
)
def test_create_connection_success(mock_getenv, mock_engine):
    """Test que la connexion à la base de données est bien créée."""
    engine = create_connection()
    assert engine is not None, "La connexion à la base de données a échoué."


@patch(
    "btc_functions.load_database.mysql.create_engine",
    side_effect=Exception("Erreur de connexion"),
)
def test_create_connection_failure():
    # with patch(
    #     "btc_functions.load_database.mysql.create_engine",
    #     side_effect=Exception("Erreur de connexion"),
    # ):
    engine = create_connection()
    assert engine is None, "La connexion n'a pas échoué comme prévu."


def test_close_engine(mock_engine):
    """Test que la connexion est bien fermée"""
    close_engine(mock_engine)
    mock_engine.dispose.assert_called_once()
