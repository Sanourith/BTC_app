import logging
import os

path_to_log = "/home/sanou/BTC_app/logs"
os.makedirs(path_to_log, exist_ok=True)


def setup_logger(name="logs.log"):
    log_file = os.path.join(path_to_log, name)
    logging.basicConfig(
        level=logging.INFO,  # Niveau du logger (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Format message
        handlers=[
            logging.FileHandler(log_file),  # Enregistre les logs dans un fichier
            logging.StreamHandler(),  # Affiche les logs dans la console
        ],
    )
