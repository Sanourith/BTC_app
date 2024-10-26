import os
import json
import pymysql 
import pandas as pd
from logging import getLogger

logger = getLogger(__name__)

def create_connection():
    try:
        host=os.getenv('DB_HOST')
        user=os.getenv('DB_USER')
        password=os.getenv('DB_PASSWORD')
        database=os.getenv('DB_NAME')
        port=int(os.getenv('DB_PORT'))

        logger.info(f'Tentative de connexion à {host}:{port} en tant que/qu\' {user}')
        
        connection = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            port=int(os.getenv('DB_PORT')),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        logger.info(f'Connexion à MySQL réussie.')
        return connection
    
    except Exception as e:
        logger.error(f'Erreur lors de la connexion à MySQL : {e}')
        return None 

def convert_json_to_csv(json_file, csv_file):
    try:
        with open(json_file, 'r') as file:
            data = json.load(file)
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            columns = [
                "kline_open_time", "open_price", "high_price", "low_price", 
                "close_price", "volume", "kline_close_time", "quote_asset_volume", 
                "number_of_trades", "taker_buy_base_asset_volume", 
                "taker_buy_quote_asset_volume", "ignore"
            ]
            df = pd.DataFrame(data, columns=columns)
            df.drop(columns=["ignore"], inplace=True)  # Supprimer la colonne inutile
        else:
            raise ValueError("Format JSON non pris en charge.")

        df.to_csv(csv_file, index=False)
        logger.info(f'Conversion réussie : {json_file} -> {csv_file}')
    except Exception as e:
        logger.error(f'Erreur lors de la conversion :{e}')

def convert_all_json_to_csv(json_dir, csv_dir):
    os.makedirs(csv_dir, exist_ok=True)

    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            json_file = os.path.join(json_dir, filename)
            csv_file = os.path.join(csv_dir, filename.replace(".json", ".csv"))

            convert_json_to_csv(json_file, csv_file)
            logger.info(f'Fichier {filename} converti avec succès en csv.')

def insert_data_from_csv(connection, csv_file, table_name):
    try:
        data = pd.read_csv(csv_file)
        cursor = connection.cursor()

        # Vérifier que les colonnes du CSV correspondent à celles de la table
        cols = ",".join(str(i) for i in data.columns.tolist())
        placeholders = ', '.join(['%s'] * len(data.columns))

        for i, row in data.iterrows():
            sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(row))

        connection.commit()
        logger.info(f'{len(data)} lignes insérées dans la table {table_name}')

    except pymysql.MySQLError as e:
        logger.error(f'Erreur lors de l\'insertion des données : {e}')
        connection.rollback()
    except Exception as e:
        logger.error(f'Erreur lors de l\'insertion des données : {e}')
        connection.rollback()
    finally:
        cursor.close()

def close_connection(connection):
    if connection:
        connection.close()
        logger.info('Connexion SQL fermée.')