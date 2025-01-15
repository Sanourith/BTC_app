import pytest
import os
import json
import glob
import btc_functions.load_database.mysql as db_functions


@pytest.fixture
def setup_dir(tmp_path):
    """Fixture qui crée des répertoires temporaires pour les tests"""
    json_dir = tmp_path / "json_dir"
    csv_dir = tmp_path / "csv_dir"
    interim_dir = tmp_path / "interim_dir"
    json_dir.mkdir()
    csv_dir.mkdir()
    interim_dir.mkdir()
    return str(json_dir), str(csv_dir), str(interim_dir)


def test_full_integration(mock_engine, setup_dir):
    """Test d'intégration complet : conversion, insertion et déplacement des fichiers"""
    json_dir, csv_dir, interim_dir = setup_dir

    # fichier JSON test
    json_file_path = os.path.join(json_dir, "test.json")
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
    with open(json_file_path, "w") as f:
        json.dump(data, f)

    # Conversion JSON > CSV
    db_functions.convert_all_json_to_csv(json_dir, csv_dir)
    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    assert len(csv_files) == 1, "Le fichier CSV n'a pas été créé correctement."

    # Insertion dans la DB (mock)
    db_functions.insert_data_from_csv(mock_engine, csv_files[0], "test_table")

    # Déplacement des fichiers
    db_functions.move_to_interim(csv_files[0], interim_dir)
    assert os.path.exists(
        os.path.join(interim_dir, "test.csv")
    ), "Le fichier n'a pas été déplacé correctement"
