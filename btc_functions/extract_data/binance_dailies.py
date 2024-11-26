import os
import json
import requests
from datetime import datetime, timedelta
from logging import getLogger
from typing import Optional, Dict, Any

logger = getLogger(__name__)

BASE_DIR = os.getenv("BTC_APP_BASE_DIR", "/home/sanou/BTC_app/data/1_raw")
BINANCE_URL = "https://api.binance.com/api/v3/"


def verif_directory_exist(path: str) -> None:
    """Ensure the directory for a given path exists."""
    os.makedirs(os.path.dirname(path), exist_ok=True)


def data_to_json(data: Any, filename: str) -> None:
    """
    Save JSON data to a file in the specified directory.

    Args:
        data (Any): data to save as JSON
        filename (str): file name (without directory)
    """
    if data:
        file_path = os.path.join(BASE_DIR, f"{filename}.json")
        verif_directory_exist(file_path)

        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
            logger.info(f"Data saved to {file_path}.")
        except (IOError, OSError) as e:
            logger.error(f"Error saving data to {file_path}: {e}")
    else:
        logger.warning("No data to save.")


def request_data(
    endpoint: str, params: Optional[Dict[str, Any]] = None
) -> Optional[Dict]:
    """
    Make a GET request to the Binance API.

    Args:
        endpoint (str): API endpoint to call.
        params (Optional[Dict[str, Any]], optional): Query parameters for the API call.
        Defaults to None.

    Returns:
        Optional[Dict]: JSON response or None if the request fails.
    """
    url = BINANCE_URL + endpoint
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"HTTP request error: {e}")
        return None


def get_data_from_binance(endpoint: str) -> None:
    """
    Fetch data from the Binance API and save it to a JSON file.

    Args:
        endpoint (str): API endpoint to fetch data from.
    """
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    start_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    end_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

    start_timestamp = int(start_yesterday.timestamp() * 1000)
    end_timestamp = int(end_yesterday.timestamp() * 1000)

    endpoint_mapping = {
        "klines": {
            "params": {
                "symbol": "BTCUSDT",
                "interval": "5m",
                "startTime": start_timestamp,
                "endTime": end_timestamp,
                "limit": 1000,
            },
            "file": "prices_BTC_KLINES",
        },
        "ticker/24hr": {
            "params": {
                "symbol": "BTCUSDT",
            },
            "file": "prices_BTC_24h",
        },
        "ticker/tradingDay": {
            "params": {
                "symbol": "BTCUSDT",
            },
            "file": "prices_BTC_daily",
        },
    }

    if endpoint not in endpoint_mapping:
        logger.error(f"Unsupported endpoint : {endpoint}")
        raise ValueError(
            f"Supported endpoints are: {', '.join(endpoint_mapping.keys())}"
        )

    config = endpoint_mapping[endpoint]
    data = request_data(endpoint, params=config["params"])
    if data:
        data_to_json(data, config["file"])


# Response_type Klines :
# [
#   [
#     1499040000000,      // Kline open time
#     "0.01634790",       // Open price
#     "0.80000000",       // High price
#     "0.01575800",       // Low price
#     "0.01577100",       // Close price
#     "148976.11427815",  // Volume
#     1499644799999,      // Kline Close time
#     "2434.19055334",    // Quote asset volume
#     308,                // Number of trades
#     "1756.87402397",    // Taker buy base asset volume
#     "28.46694368",      // Taker buy quote asset volume
#     "0"                 // Unused field, ignore.
#   ]
# ]

# Response_type 24h :
# {
#   "symbol": "BNBBTC",
#   "priceChange": "-94.99999800",
#   "priceChangePercent": "-95.960",
#   "weightedAvgPrice": "0.29628482",
#   "prevClosePrice": "0.10002000",
#   "lastPrice": "4.00000200",
#   "lastQty": "200.00000000",
#   "bidPrice": "4.00000000",
#   "bidQty": "100.00000000",
#   "askPrice": "4.00000200",
#   "askQty": "100.00000000",
#   "openPrice": "99.00000000",
#   "highPrice": "100.00000000",
#   "lowPrice": "0.10000000",
#   "volume": "8913.30000000",
#   "quoteVolume": "15.30000000",
#   "openTime": 1499783499040,
#   "closeTime": 1499869899040,
#   "firstId": 28385,   // First tradeId
#   "lastId": 28460,    // Last tradeId
#   "count": 76         // Trade count
# }
