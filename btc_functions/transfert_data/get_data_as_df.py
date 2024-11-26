import pandas as pd
import logging
from ..logging.logger_config import setup_logger
from ..load_database import deprecated_mysql as db_functions

logger = logging.getLogger(__name__)


def get_df_change_timestamp(table_name, col1, col2=None) -> pd.DataFrame:
    """Récupère une table SQL, applique reverse_timestamp sur les cols BIGINT spécifiées
       et retourne le DataFrame.

    Args:
        engine (connection): engine pymysql
        table_name (sql_table): nom de la table cible (type BIGINT / timestamp)
        col1 (table_column): table à transcrire
        col2 (table_column2, optional): 2e colonne à transcrire. Defaults to None.
    """
    setup_logger()
    engine = db_functions.create_connection()
    query = f"SELECT * FROM {table_name}"

    df = pd.read_sql_query(query, engine)
    df = db_functions.reverse_timestamp(df, col1, col2)

    logger.info(f"Table {table_name} traitée avec succès.")
    return df


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
    df[cols] = df[cols].map(lambda x: datetime.fromtimestamp(x / 1000))
    return df
