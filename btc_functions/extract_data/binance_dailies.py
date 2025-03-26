import os
import json
import requests
from datetime import datetime, timedelta
from logging import getLogger
from typing import Optional, Dict, Any

logger = getLogger(__name__)

BASE_DIR = os.getenv("BTC_APP_BASE_DIR", "/home/sanou/work/BTC_app/data/1_raw")
BINANCE_URL = "https://api.binance.com/api/v3/"


def verif_directory_exists(path: str) -> None:
    """Ensure the directory for a given path exists"""
    os.makedirs(os.path.dirname(path), exist_ok=True)


def data_to_json(data: Any, filename: str, date: datetime) -> None:
    """
    Save JSON data to a file in the specified directory.

    Args:
        data (Any): data to save as JSON
        filename (str): file name (without directory)
        date (datetime): date to use in the filename
    """
    if data:
        date_str = date.strftime("%Y%m%d")

        # Supprimer l'extension .json si elle existe déjà
        if filename.lower().endswith(".json"):
            base_name = filename[:-5]
        else:
            base_name = filename

        # Construire le chemin complet avec la date
        final_filename = f"{base_name}_{date_str}.json"
        file_path = os.path.join(BASE_DIR, final_filename)

        logger.debug(f"Attempting to save file with path: {file_path}")
        logger.debug(f"BASE_DIR is: {BASE_DIR}")
        logger.debug(f"Final filename is: {final_filename}")

        verif_directory_exists(file_path)

        try:
            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)
                logger.info(f"Data saved to {file_path}")
        except (IOError, OSError) as e:
            logger.error(f"Error saving data to {file_path}: {e}")
    else:
        logger.warning("No data to save")
    return


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
        logger.error(f"Http request error : {e}")
        return None


def get_data_from_binance(
    endpoint: str, r_days: int = 1, use_today_for_filename: bool = True
) -> None:
    """
    Fetch data from the Binance API and save it to a JSON file.

    Args:
        endpoint (str): API endpoint to fetch data from.
        r_days (int): number of days to go back (default: 1 for yesterday)
        use_today_for_filename (bool): if True, use today's date for the filename
    """
    now = datetime.now()
    yesterday = now - timedelta(days=r_days)
    logger.debug(f"Yesterday's date is :{yesterday}")

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
            f"Supported endpoints are : {', '.join(endpoint_mapping.keys())}"
        )

    config = endpoint_mapping[endpoint]
    logger.debug(f"Using configuration : {config}")
    data = request_data(endpoint, params=config["params"])

    if data:
        # Utilisez now ou yesterday selon le paramètre
        file_date = now if use_today_for_filename else yesterday
        logger.debug(f"Using date {file_date} for filename")
        data_to_json(data, config["file"], file_date)
        return
