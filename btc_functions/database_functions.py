import os
import json
import pymysql 
import pandas as pd
from logging import getLogger
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()
logger = getLogger(__name__)

def create_connection():
    try:
        # Charger les informations de connexion depuis les variables d'environnement
        sql_user = os.getenv('DB_USER')
        sql_password = os.getenv('DB_PASSWORD')
        sql_host = os.getenv('DB_HOST')
        sql_port = os.getenv('DB_PORT')
        sql_database = os.getenv('DB_NAME')
        
        # Chaîne de connexion
        connection_string = f"mysql+pymysql://{sql_user}:{sql_password}@{sql_host}:{sql_port}/{sql_database}"
        logger.info(f'Tentative de connexion à {sql_host}:{sql_port} en tant que {sql_user}')
        
        # Création de l'engine avec SQLAlchemy
        engine = create_engine(connection_string)
        # connection = engine.connect()
        
        logger.info("Connexion à MySQL réussie avec SQLAlchemy.")
        return engine
    
    except SQLAlchemyError as e:
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

def insert_data_from_csv(engine, csv_file, table_name):
    try:
        data = pd.read_csv(csv_file)
        
        # Insérer les données en utilisant SQLAlchemy pour la gestion automatique des transactions
        with engine.begin() as connection:
            data.to_sql(table_name, con=connection, if_exists='append', index=False)
            logger.info(f'{len(data)} lignes insérées dans la table {table_name}')
    
    except SQLAlchemyError as e:
        logger.error(f'Erreur lors de l\'insertion des données avec SQLAlchemy : {e}')
    except Exception as e:
        logger.error(f'Erreur lors de l\'insertion des données : {e}')

def close_engine(engine):
    if engine:
        engine.dispose()
        logger.info('Connexion SQL fermée.')