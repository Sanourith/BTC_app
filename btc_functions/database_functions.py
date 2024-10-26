import os
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
        data = pd.read_json(json_file)
        data.to_csv(csv_file, index=False)
        logger.info(f'Conversion réussie : {json_file} -> {csv_file}')
    except Exception as e:
        logger.error(f'Erreur lors de la conversion :{e}')

def insert_data_from_csv(connection, csv_file, table_name):
    try:
        data = pd.read_csv(csv_file)
        cursor = connection.cursor()

        cols = ",".join(str(i) for i in data.columns.tolist())

        for i, row in data.iterrows():
            sql = f"INSERT INTO {table_name} ({cols}) VALUES ({'%s, ' * (len(row) - 1)}%s)"
            cursor.execute(sql, tuple(row))
        
        connection.commit()

        logger.info(f'{len(data)} lignes insérées dans la table {table_name}')
        
    except Exception as e:
        logger.info(f'Erreur lors de l\'insertion des données : {e}')
        connection.rollback()

def close_connection(connection):
    if connection:
        connection.close()
        logger.info('Connexion SQL fermée.')