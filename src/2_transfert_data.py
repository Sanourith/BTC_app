from logging import getLogger
from btc_functions.logging.logger_config import setup_logger
import os
import sys
import glob
from dotenv import load_dotenv
import btc_functions.load_database.mysql as db_functions
from pathlib import Path

logger = getLogger(__name__)


def main():
    setup_logger()

    # Définir les répertoires
    directories = {
        "json_dir": "~/BTC_app/data/1_raw",
        "csv_dir": "~/BTC_app/data/1_raw",
        "interim_dir": "~/BTC_app/data/2_interim",
        "failed_dir": "~/BTC_app/data/5_failed",
    }

    # Créer les répertoires nécessaires
    for name, dir_path in directories.items():
        directories[name] = db_functions.setup_directories(dir_path)

    # Établir la connexion à la base de données
    engine = db_functions.create_connection()
    if not engine:
        logger.error("Database connection failed. Exiting script.")
        sys.exit(1)

    try:
        # Convertir tous les fichiers JSON en CSV
        db_functions.convert_all_json_to_csv(
            directories["json_dir"], directories["csv_dir"]
        )

        # Traiter tous les fichiers CSV
        csv_pattern = os.path.join(os.path.expanduser(directories["csv_dir"]), "*.csv")
        csv_files = glob.glob(csv_pattern)

        if not csv_files:
            logger.warning("No CSV files found to process.")
        else:
            logger.info(f"Found {len(csv_files)} CSV files to process.")

        processed_files = 0
        failed_files = 0

        for file_path in csv_files:
            table_name = db_functions.get_table_name(file_path)
            if table_name == "unknownfile":
                logger.info(f"Skipping unknown file type: {file_path}")
                continue

            try:
                # Insérer les données dans la base de données
                if db_functions.insert_data_from_csv(engine, file_path, table_name):
                    # Déplacer le fichier vers interim après traitement réussi
                    if db_functions.move_to_interim(
                        file_path, directories["interim_dir"]
                    ):
                        processed_files += 1
                    else:
                        failed_files += 1
                else:
                    failed_files += 1
                    # Option, déplacer les fichiers échoués vers un dossier spécifique
                    db_functions.move_to_interim(file_path, directories["failed_dir"])

            except Exception as e:
                failed_files += 1
                logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
                # Déplacer vers le dossier des fichiers échoués
                db_functions.move_to_interim(file_path, directories["failed_dir"])

        # Déplacer tous les fichiers JSON originaux vers interim
        json_pattern = os.path.join(
            os.path.expanduser(directories["json_dir"]), "*.json"
        )
        for file_path in glob.glob(json_pattern):
            db_functions.move_to_interim(file_path, directories["interim_dir"])

        logger.info(
            f"File processing completed: {processed_files} successful, {failed_files} failed."
        )

    finally:
        # Fermer la connexion à la base de données
        db_functions.close_engine(engine)


if __name__ == "__main__":
    # Charger les variables d'environnement
    load_dotenv(os.path.expanduser("~/BTC_app/env/private.env"))
    main()
