from datetime import datetime, timedelta
from pathlib import Path
import logging
import glob
import os

from btc_functions.extract_data.binance_dailies import get_data_from_binance
from btc_functions.logging.logger_config import setup_logger

logger = logging.getLogger(__name__)


def rename_json_files_with_date():
    """
    Searches for JSON files without a date in the filename and renames them by appending yesterday's date.
    """
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y%m%d")

    base_dir = Path(os.getenv("BTC_APP_BASE_DIR", "~/BTC_app/data/1_raw")).expanduser()

    patterns = [
        "prices_BTC_KLINES.json",
        "prices_BTC_24h.json",
        "prices_BTC_daily.json",
    ]

    for pattern in patterns:
        path_pattern = str(base_dir / pattern)
        matching_files = glob.glob(path_pattern)

        for file_path in matching_files:
            file_path = Path(file_path)
            new_file_name = f"{file_path.stem}_{date_str}.json"
            new_file_path = file_path.parent / new_file_name

            try:
                file_path.rename(new_file_path)
                logger.info(f"Renamed {file_path} to {new_file_path}")
            except Exception as e:
                logger.error(f"Error renaming {file_path}: {e}")


def main():
    """
    Main execution function:
    - Sets up logging
    - Fetches data from Binance API
    - Renames JSON files by appending the date
    """
    setup_logger()
    endpoints = ["klines", "ticker/24hr", "ticker/tradingDay"]

    for endpoint in endpoints:
        get_data_from_binance(endpoint)
        logger.info(f"Data successfully fetched and saved for endpoint: {endpoint}")

    rename_json_files_with_date()
    logger.info("File renaming completed")


if __name__ == "__main__":
    main()
