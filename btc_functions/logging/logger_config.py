import logging
import os
from pathlib import Path

# Define the log directory and ensure it exists
LOG_DIR = Path("~/BTC_app/logs").expanduser()
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger(log_name: str = "logs.log") -> None:
    """
    Configures the logging system to log messages to both a file and the console.

    Args:
        log_name (str): Name of the log file. Default is "logs.log".
    """
    log_file = LOG_DIR / log_name
    logging.basicConfig(
        level=logging.INFO,  # Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),  # Log messages to a file
            logging.StreamHandler(),  # Display logs in the console
        ],
    )
