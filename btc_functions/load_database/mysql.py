import os
import json
import shutil
import pandas as pd
from logging import getLogger
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# from dotenv import load_dotenv
# from datetime import datetime
logger = getLogger()
# load_dotenv("/home/sanou/BTC_app/env/private.env")


def create_connection():
    """
    Establishes a connection to the MySQL database using SQLAlchemy and variables.

    Returns:
        engine: SQLAlchemy engine object or None if connection fails.
    """
    try:
        sql_user = os.getenv("DB_USER")
        sql_pass = os.getenv("DB_PASSWORD")
        sql_host = os.getenv("DB_HOST")
        sql_port = os.getenv("DB_PORT")
        sql_db = os.getenv("DB_NAME")
        sqlcmd = "mysql+pymysql://"
        # Chaîne de connexion
        connection_string = (
            f"{sqlcmd}{sql_user}:{sql_pass}@{sql_host}:{sql_port}/{sql_db}"
        )
        logger.info(f"Attempting to connect to {sql_host}:{sql_port} as {sql_user}")

        engine = create_engine(connection_string)
        logger.info("Connection to MySQL established successfully.")
        return engine

    except SQLAlchemyError as e:
        logger.error(f"Error connecting to MySQL: {e}")


def convert_json_to_csv(json_file: str, csv_file: str) -> None:
    """
    Converts a JSON file to CSV format.

    Args:
        json_file (str): Path to the input JSON file.
        csv_file (str): Path to output the converted csv file.
    """
    try:
        with open(json_file, "r") as file:
            data = json.load(file)
        if isinstance(data, dict):
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            columns = [
                "kline_open_time",
                "open_price",
                "high_price",
                "low_price",
                "close_price",
                "volume",
                "kline_close_time",
                "quote_asset_volume",
                "number_of_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ]
            df = pd.DataFrame(data, columns=columns)
            df.drop(columns=["ignore"], inplace=True)
        else:
            raise ValueError("Unsupported JSON format.")

        df.to_csv(csv_file, index=False)
        logger.info(f"Successfully converted {json_file} to {csv_file}")

    except Exception as e:
        logger.error(f"Error during conversion: {e}")


def convert_all_json_to_csv(json_dir: str, csv_dir: str) -> None:
    """
    Converts all JSON files in a directory to CSV files.

    Args:
        json_dir (str): Directory containing JSON files.
        csv_dir (str): Directory where CSV files will be saved.
    """
    os.makedirs(csv_dir, exist_ok=True)

    for filename in os.listdir(json_dir):
        if filename.endswith(".json"):
            json_file = os.path.join(json_dir, filename)
            csv_file = os.path.join(csv_dir, filename.replace(".json", ".csv"))
            convert_json_to_csv(json_file, csv_file)
            logger.info(f"Converted {filename} to CSV successfully.")


def insert_data_from_csv(engine, csv_file: str, table_name: str) -> None:
    """
    Inserts data from a CSV file into a MySQL database table.

    Args:
        engine (_type_): SQLAlchemy engine object for database connection.
        csv_file (str): Path to the CSV file to be inserted.
        table_name (str): Name of the target table in the database.
    """
    try:
        data = pd.read_csv(csv_file)

        with engine.begin() as connection:
            data.to_sql(table_name, con=connection, if_exists="append", index=False)
            logger.info(f"Inserted {len(data)} rows into the table {table_name}")
    except SQLAlchemyError as e:
        logger.error(f"Error inserting data from {csv_file} into {table_name}: {e}")


def close_engine(engine):
    """
    Closes the SQLAlchemy engine connection.

    Args:
        engine (_type_): The SQLAlchemy engine to be closed.
    """
    if engine:
        engine.dispose()
        logger.info("SQL connection closed.")


def setup_directories(dir):
    """
    Creates necessary directories if they don't exist.

    Args:
        json_dir (_type_): Directory for json files.
        csv_dir (_type_): Directory for csv files.
        interim_dir (_type_): Directory for interim files.
        failed_dir (_type_): Directory for failed files.
    """
    os.makedirs(dir, exist_ok=True)
    logger.info(f"Directory : {dir} now exists.")


def get_table_name(file_path):
    """
    Returns the table name base on the CSV file name.

    Args:
        file_path (str): Path of the CSV file.
    """
    if "klines" in file_path.lower():
        return "klines"
    elif "btc_24h" in file_path.lower():
        return "ticker24h"
    elif "daily" in file_path.lower():
        return "daily"
    else:
        logger.warning(f"File ignored : {file_path} (not a known file).")
        return "unknownfile"


def move_to_interim(file_path, interim_dir):
    """
    Moves a processed file to the interim directory.

    Args:
        file_path (str): Path of the processed file.
        interim_dir (str): Directory where the file should be moved.
    """
    destination = os.path.join(interim_dir, os.path.basename(file_path))
    shutil.move(file_path, destination)
    logger.info(f"File {file_path} moved to {destination}")
