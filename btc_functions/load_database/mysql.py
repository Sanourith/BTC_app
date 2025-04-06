import os
import json
import shutil
import pandas as pd
from logging import getLogger
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from pathlib import Path

logger = getLogger(__name__)


def create_connection():
    """
    Establishes a connection to the MySQL database using SQLAlchemy and environment variables.

    Returns:
        engine: SQLAlchemy engine object or None if connection fails.
    """
    try:
        sql_user = os.getenv("DB_USER")
        sql_pass = os.getenv("DB_PASSWORD")
        sql_host = os.getenv("DB_HOST")
        sql_port = os.getenv("DB_PORT")
        sql_db = os.getenv("DB_NAME")

        if not all([sql_user, sql_pass, sql_host, sql_port, sql_db]):
            missing_vars = [
                var
                for var, val in {
                    "DB_USER": sql_user,
                    "DB_PASSWORD": sql_pass,
                    "DB_HOST": sql_host,
                    "DB_PORT": sql_port,
                    "DB_NAME": sql_db,
                }.items()
                if not val
            ]

            logger.error(f"Missing environment variables: {', '.join(missing_vars)}")
            return None

        sqlcmd = "mysql+pymysql://"
        # Chaîne de connexion
        connection_string = (
            f"{sqlcmd}{sql_user}:{sql_pass}@{sql_host}:{sql_port}/{sql_db}"
        )
        logger.info(f"Attempting to connect to {sql_host}:{sql_port} as {sql_user}")

        engine = create_engine(connection_string)
        # Tester la connexion
        with engine.connect() as conn:
            pass

        logger.info("Connection to MySQL established successfully.")
        return engine

    except SQLAlchemyError as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None


def convert_json_to_csv(json_file: str, csv_file: str) -> bool:
    """
    Converts a JSON file to CSV format.

    Args:
        json_file (str): Path to the input JSON file.
        csv_file (str): Path to output the converted csv file.

    Returns:
        bool: True if conversion was successful, False otherwise.
    """
    try:
        with open(json_file, "r") as file:
            data = json.load(file)

        if not data:
            logger.warning(f"JSON file is empty: {json_file}")
            return False

        if isinstance(data, dict):
            # Pour les données de type ticker/24hr ou ticker/tradingDay
            df = pd.DataFrame([data])
        elif isinstance(data, list):
            # Pour les données de type klines
            if all(isinstance(item, list) for item in data):
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
            logger.error(f"Unsupported JSON format in {json_file}")
            return False

        df.to_csv(csv_file, index=False)
        logger.info(f"Successfully converted {json_file} to {csv_file}")
        return True

    except Exception as e:
        logger.error(f"Error during conversion of {json_file}: {e}")
        return False


def convert_all_json_to_csv(json_dir: str, csv_dir: str) -> int:
    """
    Converts all JSON files in a directory to CSV files.

    Args:
        json_dir (str): Directory containing JSON files.
        csv_dir (str): Directory where CSV files will be saved.

    Returns:
        int: Number of files successfully converted.
    """
    json_path = Path(os.path.expanduser(json_dir))
    csv_path = Path(os.path.expanduser(csv_dir))

    # Créer le répertoire CSV s'il n'existe pas
    csv_path.mkdir(parents=True, exist_ok=True)

    successful_conversions = 0
    json_files = list(json_path.glob("*.json"))
    logger.info(f"Found {len(json_files)} JSON files to convert.")

    for json_file in json_files:
        csv_file = csv_path / json_file.name.replace(".json", ".csv")
        if convert_json_to_csv(str(json_file), str(csv_file)):
            successful_conversions += 1

    logger.info(f"Converted {successful_conversions} out of {len(json_files)} files.")
    return successful_conversions


def insert_data_from_csv(engine, csv_file: str, table_name: str) -> bool:
    """
    Inserts data from a CSV file into a MySQL database table.

    Args:
        engine: SQLAlchemy engine object for database connection.
        csv_file (str): Path to the CSV file to be inserted.
        table_name (str): Name of the target table in the database.

    Returns:
        bool: True if insertion was successful, False otherwise.
    """
    try:
        data = pd.read_csv(csv_file)
        if data.empty:
            logger.warning(f"No data to insert from {csv_file}")
            return False

        with engine.begin() as connection:
            data.to_sql(table_name, con=connection, if_exists="append", index=False)
            logger.info(f"Inserted {len(data)} rows into the table {table_name}")
        return True

    # ERRORS
    except pd.errors.EmptyDataError:
        logger.warning(f"CSV file is empty: {csv_file}")
        return False
    except SQLAlchemyError as e:
        logger.error(
            f"Database error inserting data from {csv_file} into {table_name}: {e}"
        )
        return False
    except Exception as e:
        logger.error(f"Unexpected error processing {csv_file}: {e}")
        return False


def close_engine(engine):
    """
    Closes the SQLAlchemy engine connection.

    Args:
        engine: The SQLAlchemy engine to be closed.
    """
    if engine:
        engine.dispose()
        logger.info("SQL connection closed.")


def setup_directories(dir_path):
    """
    Creates necessary directory if it doesn't exist.

    Args:
        dir_path (str): Directory path to create.

    Returns:
        Path: Path object of the created directory.
    """
    directory = Path(os.path.expanduser(dir_path))
    directory.mkdir(parents=True, exist_ok=True)
    logger.info(f"Directory: {directory} now exists.")
    return directory


def get_table_name(file_path):
    """
    Returns the table name based on the CSV file name.

    Args:
        file_path (str): Path of the CSV file.

    Returns:
        str: Table name or "unknownfile" if file type isn't recognized.
    """
    file_path = file_path.lower()

    if "klines" in file_path:
        return "klines"
    elif "btc_24h" in file_path:
        return "ticker24h"
    elif "daily" in file_path:
        return "daily"
    else:
        logger.warning(f"File ignored: {file_path} (not a known file).")
        return "unknownfile"


def move_to_interim(file_path, interim_dir):
    """
    Moves a processed file to the interim directory safely.

    Args:
        file_path (str): Path of the processed file.
        interim_dir (str): Directory where the file should be moved.

    Returns:
        bool: True if the file was moved successfully, False otherwise.
    """
    try:
        source = Path(file_path)
        target_dir = Path(os.path.expanduser(interim_dir))
        target_dir.mkdir(parents=True, exist_ok=True)

        destination = target_dir / source.name

        # Gérer les cas où le fichier de destination existe déjà
        if destination.exists():
            # Ajouter un timestamp pour éviter les collisions
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            destination = target_dir / f"{source.stem}_{timestamp}{source.suffix}"

        shutil.move(str(source), str(destination))
        logger.info(f"File {source} moved to {destination}")
        return True

    except Exception as e:
        logger.error(f"Error moving file {file_path} to {interim_dir}: {e}")
        return False
