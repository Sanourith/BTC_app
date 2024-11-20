from logging import getLogger
from btc_functions.logging.logger_config import setup_logger
import os
from dotenv import load_dotenv
import btc_functions.database.mysql as db_functions

logger = getLogger(__name__)


def prepare_ml():
    return X, y


def round_numbers(file):
    return file


def format_timestamp():
    return


def get_data_from_db():
    setup_logger()

    load_dotenv("/home/sanou/BTC_app/env/private.env")

    return


#
#
#
#
# récupère les données from DB

# tri les données et ordonne les résultats
# timestamps => dates
# données chiffres arrondies à round(X, 2)

# Préparation de la donnée à prédire
