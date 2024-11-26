from logging import getLogger
from btc_functions.logging.logger_config import setup_logger
import os
import sys
import glob
import shutil
from dotenv import load_dotenv
import BTC_app.btc_functions.load_database.mysql as db_functions

logger = getLogger(__name__)


def move_to_failed(file_path, failed_dir):
    """Déplace le fichier et son .json associé vers le répertoire failed.

    Args:
        file_path (.csv): fichier .csv en cours de traitement
        failed_dir (dir): dossier failed
    """
    json_file_path = os.path.splitext(file_path)[0] + "json"
    failed_destination_json = os.path.join(failed_dir, os.path.basename(json_file_path))
    failed_destination_csv = os.path.join(failed_dir, os.path.basename(file_path))

    # json_file_path = os.path.splitext(file_path)[0] + "json"
    if os.path.exists(json_file_path):
        shutil.move(json_file_path, failed_destination_json)
        logger.warning(
            f"Fichier {json_file_path} déplacé vers {failed_destination_json}"
        )
    shutil.move(file_path, failed_destination_csv)
    logger.warning(
        f"Fichier {file_path} déplacé vers {failed_destination_csv} pour analyse"
    )


def main():
    setup_logger()

    json_dir = "/home/sanou/BTC_app/data/1_raw"
    csv_dir = "/home/sanou/BTC_app/data/1_raw"
    interim_dir = "/home/sanou/BTC_app/data/2_interim"
    failed_dir = "/home/sanou/BTC_app/data/5_failed"

    os.makedirs(interim_dir, exist_ok=True)
    os.makedirs(failed_dir, exist_ok=True)

    load_dotenv("/home/sanou/BTC_app/env/private.env")

    engine = db_functions.create_connection()

    if not engine:
        logger.error("Database connection failed. Exiting script.")
        sys.exit(1)

    db_functions.convert_all_json_to_csv(json_dir, csv_dir)
    logger.info("Conversion des fichiers .json terminée avec succès")

    for file_path in glob.glob(os.path.join(csv_dir, "*.csv")):
        try:
            if "kline" in file_path.lower():
                table_name = "klines"
            elif "btc_24h" in file_path.lower():
                table_name = "ticker24h"
            elif "daily" in file_path.lower():
                table_name = "daily"
            else:
                table_name = "unknownfile"

            if table_name == "unknownfile":
                logger.warning(
                    f"Fichier ignoré : {file_path} (doc non -klines, daily ou 24h)"
                )
                # move_to_failed(file_path, failed_dir)
                continue

            db_functions.insert_data_from_csv(engine, file_path, table_name)
            logger.info("Données enregistrées dans la base de données btc_db.")

            destination = os.path.join(interim_dir, os.path.basename(file_path))
            shutil.move(file_path, destination)
            logger.info(f"Fichier {file_path} déplacé vers {destination}")

        except Exception as e:
            logger.error(
                f"Erreur lors du traitement de {file_path} : {e}", exc_info=True
            )
            # move_to_failed(file_path, failed_dir)

    for file_path in glob.glob(os.path.join(csv_dir, "*.json")):
        destination = os.path.join(interim_dir, os.path.basename(file_path))
        shutil.move(file_path, destination)
        logger.info(f"Fichier JSON {file_path} déplacé vers {destination}")

    logger.info("Traitement terminé pour tous les fichiers.")

    db_functions.close_engine(engine)


if __name__ == "__main__":
    main()
