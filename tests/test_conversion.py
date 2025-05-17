import pytest
import os
import json
import pandas as pd
from btc_functions.load_database.mysql import convert_json_to_csv


@pytest.fixture
def json_file(tmp_path):
    """Fixture qui crée un fichier JSON temporaire"""
    data = [
        {
            "kline_open_time": 123456,
            "open_price": 1.1,
            "high_price": 1.2,
            "low_price": 1.0,
            "close_price": 1.15,
            "volume": 100,
            "kline_close_time": 123457,
            "quote_asset_volume": 50,
            "number_of_trades": 10,
            "taker_buy_base_asset_volume": 30,
            "taker_buy_quote_asset_volume": 20,
            "ignore": 0,
        }
    ]
    file_path = tmp_path / "test.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return str(file_path)


def test_convert_json_to_csv_valid(json_file, tmp_path):
    """Test de la conversion d'un fichier JSON valide en CSV"""
    csv_file = tmp_path / "test.csv"
    convert_json_to_csv(json_file, csv_file)

    assert os.path.exists(csv_file), "Le fichier CSV n'a pas été créé."

    df = pd.read_csv(csv_file)
    assert len(df) == 1, "Le fichier CSV ne contient pas le bon nombre de lignes."
    assert (
        "open_price" in df.columns
    ), "La colonne 'open_price' est absente dans le CSV."


def test_convert_data_to_csv_empty(tmp_path):
    """Test de la conversion d'un fichier JSON vide"""
    empty_json_file = tmp_path / "empty.json"
    with open(empty_json_file, "w") as f:
        json.dump([], f)

    csv_file = tmp_path / "output.csv"
    with pytest.raises(ValueError, match="Unsupported JSON format"):
        convert_json_to_csv(empty_json_file, csv_file)
