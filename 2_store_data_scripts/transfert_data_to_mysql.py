from logging import getLogger
import os
import glob
from dotenv import load_dotenv
import btc_functions.database_functions as db_functions

logger = getLogger(__name__)

def main():
    json_dir = "/home/sanou/BTC/data/1_raw"
    csv_dir = "/home/sanou/BTC/data/2_interim"
    load_dotenv('/home/sanou/BTC/env/private.env')
    connection = db_functions.create_connection()

    if connection:
        # fichiers klines
        logger.info(f'Connexion établie. ZzZ')
        for json_file in glob.glob(os.path.join(json_dir, "prices_BTC_KLINES*.json")):
            csv_file = os.path.join(csv_dir, os.path.basename(json_file).replace('.json', '.csv'))
            db_functions.convert_json_to_csv(json_file, csv_file)
            logger.info(f'Document {json_file} converti avec succès.')
            db_functions.insert_data_from_csv(connection, csv_file, "prices_BTC_KLINES")
            logger.info(f'Données {csv_file} enregistrées dans la base de données.')
        # fichiers 24hr
        for json_file in glob.glob(os.path.join(json_dir, "prices_BTC_24*.json")):
            csv_file = os.path.join(csv_dir, os.path.basename(json_file).replace('.json', '.csv'))
            db_functions.convert_json_to_csv(json_file, csv_file)
            logger.info(f'Document {json_file} converti avec succès.')
            db_functions.insert_data_from_csv(connection, csv_file, "prices_BTC_24h")
            logger.info(f'Données {csv_file} enregistrées dans la base de données.')
        db_functions.close_connection(connection)

if __name__ == "__main__":
    main()
