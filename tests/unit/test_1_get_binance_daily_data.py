import pytest
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from btc_functions.extract_data.binance_dailies import (
    verif_directory_exist,
    data_to_json,
    request_data,
    get_data_from_binance,
)


class TestBinanceDataExtraction:
    def test_verif_directory_exist(self, tmp_path):
        """Teste la création de répertoire"""
        test_path = tmp_path / "test_dir" / "test_file.json"
        verif_directory_exist(str(test_path))
        assert test_path.parent.exists()

    def test_data_to_json(self, tmp_path):
        """Teste la sauvegarde JSON"""
        test_data = {"test": "data"}
        with patch(
            "btc_functions.extract_data.binance_dailies.BASE_DIR", str(tmp_path)
        ):
            data_to_json(test_data, "test_file")
            json_files = list(tmp_path.glob("*_*.json"))
            assert len(json_files) == 1

            with open(json_files[0], "r") as f:
                loaded_data = json.load(f)
            assert loaded_data == test_data

    @patch("btc_functions.extract_data.binance_dailies.requests.get")
    def test_request_data_success(self, mock_get):
        """Teste une requête API réussie"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        result = request_data("klines", {"params": "test"})
        assert result == {"key": "value"}

    @patch("btc_functions.extract_data.binance_dailies.request_data")
    @patch("btc_functions.extract_data.binance_dailies.data_to_json")
    def test_get_data_from_binance(self, mock_data_to_json, mock_request_data):
        """Teste l'extraction de données depuis Binance"""
        mock_request_data.return_value = {"test": "data"}
        get_data_from_binance("klines")

        mock_request_data.assert_called_once()
        mock_data_to_json.assert_called_once()

    def test_get_data_from_binance_invalid_endpoint(self):
        """Teste une extaction avec un endpoint invalide"""
        with pytest.raises(ValueError):
            get_data_from_binance("invalid_endpoint")

    @patch("btc_functions.extract_data.binance_dailies.request_data")
    def test_get_data_from_binance_no_data(self, mock_request_data):
        """Teste le cas où aucune donnée n'est retournée"""
        mock_request_data.return_value = None

        with patch(
            "btc_functions.extract_data.binance_dailies.data_to_json"
        ) as mock_data_to_json:
            get_data_from_binance("klines")
            mock_data_to_json.assert_not_called()
