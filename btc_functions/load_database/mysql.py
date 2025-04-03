import os
import json
import shutil
import pandas as pd
from pathlib import Path
from logging import getLogger
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Logger configuration
logger = getLogger(__name__)


def create_connection():
    """
    Establishes a connection to the MySQL database using credentials from environment variables.

    Returns:
        engine (sqlalchemy.engine.base.Engine | None): SQLAlchemy engine object if connection is successful, otherwise None.
    """
    try:
        connection_string = (
            f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )
        engine = create_engine(connection_string)
        logger.info("Successfully connected to MySQL.")
        return engine
    except SQLAlchemyError as e:
        logger.error(f"MySQL connection error: {e}")
        return None


def convert_json_to_csv(json_file: Path, csv_file: Path) -> None:
    """
    Converts a JSON file to CSV format.

    Args:
        json_file (Path): Path to the input JSON file.
        csv_file (Path): Path to the output CSV file.
    """
    try:
        with json_file.open("r") as file:
            data = json.load(file)

        if not data:
            raise ValueError("The JSON file is empty or incorrectly formatted.")

        df = pd.DataFrame([data]) if isinstance(data, dict) else pd.DataFrame(data)

        if "ignore" in df.columns:
            df.drop(columns=["ignore"], inplace=True)

        df.to_csv(csv_file, index=False)
        logger.info(f"Successfully converted: {json_file} → {csv_file}")
    except Exception as e:
        logger.error(f"Conversion error {json_file}: {e}")


def convert_all_json_to_csv(json_dir: Path, csv_dir: Path) -> None:
    """
    Converts all JSON files in a given directory to CSV files.

    Args:
        json_dir (Path): Path to the directory containing JSON files.
        csv_dir (Path): Path to the directory where CSV files will be saved.
    """
    csv_dir.mkdir(parents=True, exist_ok=True)

    for json_file in json_dir.glob("*.json"):
        convert_json_to_csv(json_file, csv_dir / json_file.with_suffix(".csv").name)


def insert_data_from_csv(engine, csv_file: Path, table_name: str) -> None:
    """
    Inserts data from a CSV file into a MySQL database table.

    Args:
        engine (sqlalchemy.engine.base.Engine): SQLAlchemy engine object for database connection.
        csv_file (Path): Path to the CSV file to be inserted.
        table_name (str): Name of the target database table.
    """
    try:
        df = pd.read_csv(csv_file)
        df.to_sql(table_name, con=engine, if_exists="append", index=False)
        logger.info(f"Successfully inserted: {len(df)} rows into {table_name}")
    except SQLAlchemyError as e:
        logger.error(f"Insertion error {csv_file} → {table_name}: {e}")


def close_engine(engine):
    """
    Closes the SQLAlchemy engine connection if it exists.

    Args:
        engine (sqlalchemy.engine.base.Engine | None): SQLAlchemy engine object to be closed.
    """
    if engine:
        engine.dispose()
        logger.info("SQL connection closed.")


def setup_directories(directory: Path) -> None:
    """
    Creates a directory if it does not already exist.

    Args:
        directory (Path): Path of the directory to be created.
    """
    directory.mkdir(parents=True, exist_ok=True)
    logger.info(f"Directory ready: {directory}")


def get_table_name(file_path: Path) -> str:
    """
    Determines the database table name based on the given file name.

    Args:
        file_path (Path): Path to the file whose name will be used to infer the table name.

    Returns:
        str: The corresponding table name if recognized, otherwise "unknownfile".
    """
    filename = file_path.stem.lower()
    table_map = {"klines": "klines", "btc_24h": "ticker24h", "daily": "daily"}

    for key, table in table_map.items():
        if key in filename:
            return table

    logger.warning(f"File ignored: {file_path} (unknown name).")
    return "unknownfile"


def move_to_interim(file_path: Path, interim_dir: Path) -> None:
    """
    Moves a processed file to an interim directory.

    Args:
        file_path (Path): Path of the processed file.
        interim_dir (Path): Path of the interim directory where the file will be moved.
    """
    interim_dir.mkdir(parents=True, exist_ok=True)
    destination = interim_dir / file_path.name
    shutil.move(str(file_path), str(destination))
    logger.info(f"Moved: {file_path} → {destination}")
