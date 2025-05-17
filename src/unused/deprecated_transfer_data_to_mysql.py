from logging import getLogger
from btc_functions.logging.logger_config import setup_logger
import os
import glob
import shutil
from dotenv import load_dotenv
import BTC_app.btc_functions.load_database.deprecated_mysql as db_functions

logger = getLogger(__name__)


def main():
    # Configurer le logger
    setup_logger()

    json_dir = "~/BTC_app/data/1_raw"
    csv_dir = "~/BTC_app/data/1_raw"
    interim_dir = "~/BTC_app/data/2_interim"

    os.makedirs(csv_dir, exist_ok=True)
    os.makedirs(interim_dir, exist_ok=True)

    # Charger les variables d'environnement
    load_dotenv("~/BTC_app/env/private.env")

    # Créer l'engine de connexion à la base de données
    engine = db_functions.create_connection()

    if engine:
        try:
            # Conversion des fichiers .json en .csv
            db_functions.convert_all_json_to_csv(json_dir, csv_dir)
            logger.info("Conversion des fichiers .json terminée avec succès")

            # Déplacement des fichiers json pour éviter un double traitement
            for json_file in glob.glob(
                os.path.join(json_dir, "prices_BTC_KLINES*.json")
            ):
                destination = os.path.join(interim_dir, os.path.basename(json_file))
                shutil.move(json_file, destination)
                logger.info(f"Fichier {json_file} déplacé vers {destination}.")

            # Insertion des données CSV dans la base de données
            for csv_file in glob.glob(os.path.join(csv_dir, "prices_BTC_KLINES*.csv")):
                db_functions.insert_data_from_csv(engine, csv_file, "klines")
                logger.info(f"Données {csv_file} enregistrées dans la base de données.")

                # Déplacement des fichiers insérés en base de données dans 2_interim
                destination = os.path.join(interim_dir, os.path.basename(csv_file))
                shutil.move(csv_file, destination)
                logger.info(f"Fichier {csv_file} déplacé vers {destination}.")

        except Exception as e:
            logger.error(f"Erreur lors du traitement des fichiers : {e}")

        finally:
            # Fermer l'engine SQLAlchemy
            db_functions.close_engine(engine)
    else:
        logger.error("Erreur de connexion à la base de données")


if __name__ == "__main__":
    main()
