from logging import getLogger
from dotenv import load_dotenv
from btc_functions.logging.logger_config import setup_logger
from btc_functions.transfert_data.get_data_as_df import get_df_change_timestamp
import btc_functions.transfert_data.best_model as bm


logger = getLogger(__name__)


def main():
    setup_logger()
    logger.info("Starting data preparation...")

    df_klines = get_df_change_timestamp("klines", "kline_open_time", "kline_close_time")
    df_daily = get_df_change_timestamp("daily", "openTime", "closeTime")

    logger.info("DataFrames Klines & 24hr recuperation. Merging preparation.")

    df_klines = bm.format_time_ml(df_klines, "kline_open_time")
    df_daily = bm.format_time_ml(df_daily, "openTime")
    logger.info("DataFrames formatted successfully.")

    try:
        merge_df = bm.merge_dfs(
            df_klines, df_daily, "kline_open_time", "openTime", "inner"
        )
        logger.info("DataFrames merged successfully.")
    except BufferError as e:
        raise BufferError(f"Error merging tables: {e}.")

    best_model = bm.train_and_select_best_models(merge_df)
    logger.info(f"Best model : {best_model}")
    return


if __name__ == "__main__":
    load_dotenv("/home/sanou/BTC_app/env/private.env")
    main()


# model = load("/home/sanou/BTC_app/models_ml/best_LinearRegression().pickle")

# prediction = model.predict(df)[0]
# logger.info(f"{prediction = }")
