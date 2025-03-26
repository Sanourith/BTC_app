from logging import getLogger
from btc_functions.logging.logger_config import setup_logger
import os
import sys
import glob
from dotenv import load_dotenv
import btc_functions.load_database.mysql as db_functions

logger = getLogger(__name__)


def main():
    setup_logger()

    spe_directories = {
        "json_dir": "/home/sanou/work/BTC_app/data/1_raw",
        "csv_dir": "/home/sanou/work/BTC_app/data/1_raw",
        "interim_dir": "/home/sanou/work/BTC_app/data/2_interim",
        "failed_dir": "/home/sanou/work/BTC_app/data/5_failed",
    }
    json_dir = "/home/sanou/work/BTC_app/data/1_raw"
    csv_dir = "/home/sanou/work/BTC_app/data/1_raw"
    interim_dir = "/home/sanou/work/BTC_app/data/2_interim"
    # failed_dir = "/home/sanou/work/BTC_app/data/5_failed"

    for name, dir in spe_directories.items():
        db_functions.setup_directories(dir)

    engine = db_functions.create_connection()
    if not engine:
        logger.error("Database connection failed. Exiting script.")
        sys.exit(1)

    try:
        db_functions.convert_all_json_to_csv(json_dir, csv_dir)
        logger.info("Conversion of .json files to .csv completed successfully.")

        for file_path in glob.glob(os.path.join(csv_dir, "*.csv")):
            table_name = db_functions.get_table_name(file_path)
            if table_name == "unknownfile":
                continue

            try:
                db_functions.insert_data_from_csv(engine, file_path, table_name)
                db_functions.move_to_interim(file_path, interim_dir)
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}", exc_info=True)

        for file_path in glob.glob(os.path.join(json_dir, "*.json")):
            db_functions.move_to_interim(file_path, interim_dir)

        logger.info("All file processing completed.")

    finally:
        db_functions.close_engine(engine)


if __name__ == "__main__":
    load_dotenv("/home/sanou/work/BTC_app/env/private.env")
    main()
