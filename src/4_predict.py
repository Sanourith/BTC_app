from logging import getLogger
import os
import pandas as pd
from joblib import load
from btc_functions.logging.logger_config import setup_logger
from btc_functions.transfert_data.get_data_as_df import get_df_change_timestamp
from btc_functions.transfert_data.best_model import format_time_ml, prepare_data

logger = getLogger(__name__)
setup_logger()

# tests en cours sur le ipynb
