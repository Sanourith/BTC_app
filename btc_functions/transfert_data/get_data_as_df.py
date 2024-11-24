import pandas as pd
import logging
from ..logging.logger_config import setup_logger
from ..load_database import mysql as db_functions

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
