from datetime import datetime, timedelta
from btc_functions.extract_data.binance_daylies import get_data_from_binance
from btc_functions.logging.logger_config import setup_logger
import logging
import os
import glob

logger = logging.getLogger(__name__)


def rename_json_files_with_date():
    """
    Recherche et renomme les fichiers JSON sans date pour y ajouter la date d'hier.
    """
    yesterday = datetime.now() - timedelta(days=1)
    date_str = yesterday.strftime("%Y%m%d")

    # Dossier de base où sont stockés les fichiers
    base_dir = os.path.expanduser(os.getenv("BTC_APP_BASE_DIR", "~/BTC_app/data/1_raw"))

    # Patterns à rechercher
    patterns = [
        "prices_BTC_KLINES.json",
        "prices_BTC_24h.json",
        "prices_BTC_daily.json",
    ]

    for pattern in patterns:
        # Cherche les fichiers correspondant au pattern
        path_pattern = os.path.join(base_dir, pattern)
        matching_files = glob.glob(path_pattern)

        for file_path in matching_files:
            # Extraire le nom de base (sans extension)
            file_dir = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            base_name = file_name.replace(".json", "")

            # Créer le nouveau nom avec la date
            new_file_name = f"{base_name}_{date_str}.json"
            new_file_path = os.path.join(file_dir, new_file_name)

            # Renommer le fichier
            try:
                os.rename(file_path, new_file_path)
                logger.info(f"Renamed {file_path} to {new_file_path}")
            except Exception as e:
                logger.error(f"Error renaming {file_path}: {e}")


def main():
    setup_logger()
    endpoints = ["klines", "ticker/24hr", "ticker/tradingDay"]

    for endpoint in endpoints:
        # Sauvegarde les fichiers sans date dans le nom
        get_data_from_binance(endpoint, use_today_for_filename=True)
        logger.info(f"Data successfully fetched and saved for endpoint: {endpoint}")

    # Après avoir récupéré toutes les données, renommer les fichiers pour ajouter la date
    rename_json_files_with_date()
    logger.info("File renaming completed")


if __name__ == "__main__":
    main()
