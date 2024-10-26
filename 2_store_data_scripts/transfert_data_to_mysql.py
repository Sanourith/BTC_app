from logging import getLogger
from btc_functions.logger_config import setup_logger
import os
import glob
import shutil
from dotenv import load_dotenv
import btc_functions.database_functions as db_functions

logger = getLogger(__name__)

def main():
    setup_logger()
    json_dir = "/home/sanou/BTC/data/1_raw"
    csv_dir = "/home/sanou/BTC/data/1_raw"
    interim_dir = "/home/sanou/BTC/data/2_interim"
    # Charger les variables d'environnement
    load_dotenv('/home/sanou/BTC/env/private.env')
    # Créer la connexion à la base de données
    connection = db_functions.create_connection()
    if connection:
        try:
            # Conversion des fichiers .json en .csv
            db_functions.convert_all_json_to_csv(json_dir, csv_dir)
            logger.info('Conversion des fichiers .json terminée avec succès')
            # Insertion des données CSV dans la base de données
            for csv_file in glob.glob(os.path.join(csv_dir, "prices_BTC_KLINES*.csv")):
                db_functions.insert_data_from_csv(connection, csv_file, "klines")
                logger.info(f'Données {csv_file} enregistrées dans la base de données.')
                if not os.path.exists(interim_dir):
                    os.makedirs(interim_dir)
                # Déplacement des fichiers insérés en base de données dans 2_interim
                destination = os.path.join(interim_dir, os.path.basename(csv_file))
                shutil.move(csv_file, destination)
                logger.info(f'Fichier {csv_file} déplacé vers {destination}.')
        except Exception as e:
            logger.error(f"Erreur lors de l'insertion des données : {e}")
        finally:
            db_functions.close_connection(connection)
    else:
        logger.error('Erreur de connexion à la base de données')

if __name__ == "__main__":
    main()
