from logging import getLogger
from dotenv import load_dotenv
from btc_functions.logging.logger_config import setup_logger
from btc_functions.transfert_data.get_data_as_df import get_df_change_timestamp
import btc_functions.transfert_data.best_model as bm
from pathlib import Path

logger = getLogger(__name__)


def prepare_data():
    """
    Load, transform, and merge datasets for model training.
    """
    logger.info("Starting data preparation...")

    df_klines = get_df_change_timestamp("klines", "kline_open_time", "kline_close_time")
    df_daily = get_df_change_timestamp("daily", "openTime", "closeTime")
    logger.info("DataFrames loaded successfully.")

    df_klines = bm.format_time_ml(df_klines, "kline_open_time")
    df_daily = bm.format_time_ml(df_daily, "openTime")
    logger.info("DataFrames formatted successfully.")

    try:
        merged_df = bm.merge_dfs(
            df_klines, df_daily, "kline_open_time", "openTime", "inner"
        )
        logger.info("DataFrames merged successfully.")
        return merged_df
    except Exception as e:
        logger.error(f"Error merging tables: {e}", exc_info=True)
        raise


def main():
    setup_logger()
    load_dotenv(Path("~/BTC_app/env/private.env").expanduser())

    merged_df = prepare_data()
    best_model = bm.train_and_select_best_models(merged_df)
    logger.info(f"Best model selected: {best_model}")


if __name__ == "__main__":
    main()
