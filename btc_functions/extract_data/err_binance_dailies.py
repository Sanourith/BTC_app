import os
import json
import requests
from datetime import datetime, timedelta
from logging import getLogger, basicConfig
from typing import Optional, Dict, Any

# Logger configuration
logger = getLogger(__name__)

BASE_DIR = os.getenv("BTC_APP_BASE_DIR", "~/BTC_app/data/1_raw")
BINANCE_URL = "https://api.binance.com/api/v3/"


def verif_directory_exists(path: str) -> None:
    """
    Ensures that the directory for the given file path exists, creating it if necessary.

    Args:
        path (str): The path where the file will be saved.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)


def data_to_json(data: Any, filename: str, date: datetime) -> None:
    """
    Saves JSON data to a file in the specified directory.

    Args:
        data (Any): The data to be saved as JSON.
        filename (str): The base filename (without directory or date).
        date (datetime): The date to include in the filename.

    Raises:
        IOError: If there is an issue writing the file.
    """
    if not data:
        logger.warning("No data to save.")
        return

    date_str = date.strftime("%Y%m%d")
    base_name = filename.rstrip(".json")  # Remove .json extension if present
    final_filename = f"{base_name}_{date_str}.json"
    file_path = os.path.join(BASE_DIR, final_filename)

    logger.debug(f"Saving data to: {file_path}")
    ensure_directory_exists(file_path)

    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Data saved successfully: {file_path}")
    except (IOError, OSError) as e:
        logger.error(f"Error saving data to {file_path}: {e}")


def request_data(
    endpoint: str, params: Optional[Dict[str, Any]] = None
) -> Optional[Dict]:
    """
    Sends a GET request to the Binance API.

    Args:
        endpoint (str): The API endpoint to call.
        params (Optional[Dict[str, Any]]): Query parameters for the API request.

    Returns:
        Optional[Dict]: The JSON response if successful, otherwise None.
    """
    url = f"{BINANCE_URL}{endpoint}"
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"HTTP request error: {e}")
        return None


def get_data_from_binance(
    endpoint: str, r_days: int = 1, use_today_for_filename: bool = True
) -> None:
    """
    Retrieves data from the Binance API and saves it to a JSON file.

    Args:
        endpoint (str): The API endpoint to request data from.
        r_days (int): Number of days to go back (default: 1, meaning yesterday).
        use_today_for_filename (bool): If True, use today's date in the filename; otherwise, use yesterday's.

    Raises:
        ValueError: If the provided endpoint is not supported.
    """
    now = datetime.now()
    target_date = now - timedelta(days=r_days)
    logger.debug(f"Fetching data for date: {target_date}")

    start_timestamp = int(
        datetime(
            target_date.year, target_date.month, target_date.day, 0, 0, 0
        ).timestamp()
        * 1000
    )
    end_timestamp = int(
        datetime(
            target_date.year, target_date.month, target_date.day, 23, 59, 59
        ).timestamp()
        * 1000
    )

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
            "params": {"symbol": "BTCUSDT"},
            "file": "prices_BTC_24h",
        },
        "ticker/tradingDay": {
            "params": {"symbol": "BTCUSDT"},
            "file": "prices_BTC_daily",
        },
    }

    if endpoint not in endpoint_mapping:
        logger.error(f"Unsupported endpoint: {endpoint}")
        raise ValueError(
            f"Supported endpoints are: {', '.join(endpoint_mapping.keys())}"
        )

    config = endpoint_mapping[endpoint]
    logger.debug(f"Using configuration: {config}")
    data = fetch_data_from_binance(endpoint, params=config["params"])

    if data:
        file_date = now if use_today_for_filename else target_date
        logger.debug(f"Saving data with date: {file_date}")
        save_data_to_json(data, config["file"], file_date)
