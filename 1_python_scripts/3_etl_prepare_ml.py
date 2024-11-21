from logging import getLogger
from datetime import datetime
import pandas as pd
from btc_functions.logging.logger_config import setup_logger
# import os
from dotenv import load_dotenv
import btc_functions.database.mysql as db_functions

logger = getLogger(__name__)


# def round_numbers(file):
#     return file


def reverse_timestamp(df: pd.DataFrame, col1: str, col2: str = None) -> pd.DataFrame:
    """Attention, la fonction traite max 2 colonnes

    Args:
        df (pd.DataFrame): df
        col1 (str): nom de la col à transformer
        col2 (str, optional): nom de la col2 à transformer. Defaults to None.

    Returns:
        pd.DataFrame: df
    """
    cols = [col1] if col2 is None else [col1, col2]
    df[cols] = df[cols].applymap(lambda x: datetime.fromtimestamp(x / 1000))
    return df
    # df["kline_open_time"] = df["kline_open_time"].apply(
    #     lambda x: datetime.fromtimestamp(x / 1000)
    # )
    # df["kline_close_time"] = df["kline_close_time"].apply(
    #     lambda x: datetime.fromtimestamp(x / 1000)
    # )
    # return df


def get_btc_data_from_db(table_name):
    setup_logger()

    load_dotenv("/home/sanou/BTC_app/env/private.env")

    try:
        engine = db_functions.create_connection()
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, engine)
        logger.info(f"Requête {query} récupérée en DataFrame. ETL en cours...")

        col1 = "kline_open_time"
        col2 = "kline_close_time"
        df = reverse_timestamp(df, col1, col2)

    # TODO : arrondir les nombres ? -non
    # TODO : ajouter des colonnes indicateurs

    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données. {e}")
    return df


def prepare_ml():
    sql_table = "klines"
    df = get_btc_data_from_db(sql_table)

    # ma target sera une colonne qui indique si 
    df["price_up"] = df[df[]]
    return X, y


#
#
#
#
# récupère les données from DB

# tri les données et ordonne les résultats
# timestamps => dates
# données chiffres arrondies à round(X, 2)

# Préparation de la donnée à prédire
