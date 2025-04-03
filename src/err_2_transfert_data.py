from logging import getLogger
from btc_functions.logging.logger_config import setup_logger
import os
import sys
import glob
from dotenv import load_dotenv
import btc_functions.load_database.mysql as db_functions
from pathlib import Path

logger = getLogger(__name__)


def process_csv_files(engine, csv_dir: Path, interim_dir: Path):
    """
    Process all CSV files: insert data into the database and move processed files to interim.
    """
    for file_path in csv_dir.glob("*.csv"):
        table_name = db_functions.get_table_name(file_path)
        if table_name == "unknownfile":
            logger.warning(f"Skipping unrecognized file: {file_path}")
            continue

        try:
            db_functions.insert_data_from_csv(engine, file_path, table_name)
            db_functions.move_to_interim(file_path, interim_dir)
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}", exc_info=True)


def process_json_files(json_dir: Path, interim_dir: Path):
    """
    Move all processed JSON files to the interim directory.
    """
    for file_path in json_dir.glob("*.json"):
        db_functions.move_to_interim(file_path, interim_dir)


def main():
    setup_logger()
    load_dotenv(Path("~/BTC_app/env/private.env").expanduser())

    directories = {
        "json_dir": Path("~/BTC_app/data/1_raw").expanduser(),
        "csv_dir": Path("~/BTC_app/data/1_raw").expanduser(),
        "interim_dir": Path("~/BTC_app/data/2_interim").expanduser(),
        "failed_dir": Path("~/BTC_app/data/5_failed").expanduser(),
    }

    for name, dir_path in directories.items():
        db_functions.setup_directories(dir_path)

    engine = db_functions.create_connection()
    if not engine:
        logger.error("Database connection failed. Exiting script.")
        sys.exit(1)

    try:
        db_functions.convert_all_json_to_csv(
            directories["json_dir"], directories["csv_dir"]
        )
        logger.info("Conversion of .json files to .csv completed successfully.")

        process_csv_files(engine, directories["csv_dir"], directories["interim_dir"])
        process_json_files(directories["json_dir"], directories["interim_dir"])

        logger.info("All file processing completed successfully.")
    finally:
        db_functions.close_engine(engine)


if __name__ == "__main__":
    main()
