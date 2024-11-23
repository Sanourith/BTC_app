from logging import getLogger
import pandas as pd
from dotenv import load_dotenv
import btc_functions.database.mysql as db_functions
from btc_functions.logging.logger_config import setup_logger

# import os

logger = getLogger(__name__)


def main(table_name, col1, col2=None) -> pd.DataFrame:
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


if __name__ == "__main__":
    load_dotenv("/home/sanou/BTC_app/env/private.env")
    df_klines = main("klines", "kline_open_time", "kline_close_time")
    df_24 = main("ticket24h", "openTime", "closeTime")

    logger.info(df_klines.head(2))
    logger.info("\n")
    logger.info(df_24.head(2))


# def prepare_ml():
#     sql_table = "klines"
#     df = get_btc_data_from_db(sql_table)

#     # ma target sera une colonne qui indique si
#     df["price_up"] = df[df[]]

#     return X, y


#
#
#
#
# récupère les données from DB

# tri les données et ordonne les résultats
# timestamps => dates
# données chiffres arrondies à round(X, 2)

# Préparation de la donnée à prédire
