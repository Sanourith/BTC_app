import pytest
import os
import json
import tempfile
import pandas as pd
from btc_functions.load_database.mysql import (
    setup_directories,
    convert_json_to_csv,
    get_table_name,
)


class TestDatabaseFunctions:
    def test_setup_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = os.path.join(tmpdir, "new_directory")
            setup_directories(test_dir)
            assert os.path.exists(test_dir), "Le répertoire n'a pas été créé"

    def test_convert_json_to_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            # Préparer un fichier JSON de test
            json_file = os.path.join(tmpdir, "test_data.json")
            csv_file = os.path.join(tmpdir, "test_data.csv")

            test_data = [
                [
                    1737241200000,
                    "104291.30000000",
                    "104475.00000000",
                    "104291.30000000",
                    "104443.56000000",
                    "83.55140000",
                    1737241499999,
                    "8722250.89667130",
                    12863,
                    "43.81979000",
                    "4574770.78810830",
                    "0",
                ]
            ]

            with open(json_file, "w") as f:
                json.dump(test_data, f)

            convert_json_to_csv(json_file, csv_file)

            assert os.path.exists(csv_file), "Le fichier CSV n'a pas été créé"

            df = pd.read_csv(csv_file)
            assert len(df) == 1, "Le nombre de lignes est incorrect"

    def test_get_table_name(self):
        test_cases = [
            ("prices_BTC_klines_2023-01-01.csv", "klines"),
            ("prices_BTC_24h_2023-01-01.csv", "ticker24h"),
            ("prices_BTC_daily_2023-01-01.csv", "daily"),
            ("unknown_file.csv", "unknownfile"),
        ]

        for input_file, expected_table in test_cases:
            assert (
                get_table_name(input_file) == expected_table
            ), f"Erreur pour {input_file}"

    # def test_error_handling(self):
    #     with tempfile.TemporaryDirectory() as tmpdir:
    #         # Test avec un fichier JSON vide
    #         empty_json = os.path.join(tmpdir, "empty.json")
    #         with open(empty_json, "w") as f:
    #             f.write("[]")

    #         with pytest.raises(ValueError):
    #             convert_json_to_csv(empty_json, os.path.join(tmpdir, "output.csv"))
