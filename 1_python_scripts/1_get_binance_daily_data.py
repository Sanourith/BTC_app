# import sys
# import os
# # Ajouter le répertoire parent au PYTHONPATH
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from BTC_app.btc_functions.extract_data.binance_dailies import get_data_from_binance
from btc_functions.logging.logger_config import setup_logger
import logging

logger = logging.getLogger(__name__)


def main():
    """
    Main function to fetch data from Binance API for specified endpoints.

    This function initializes the logger,iterates through list of Binance API endpoints,
    and calls the `get_data_from_binance` function for each endpoint.
    Logs are generated for each operation to provide status updates.
    """
    setup_logger()
    endpoints = ["klines", "ticker/24hr", "ticker/tradingDay"]  # ticker/tradingDay
    for endpoint in endpoints:
        get_data_from_binance(endpoint)
        logger.info(f"Data successfully fetched and saved for endpoint: {endpoint}")


if __name__ == "__main__":
    main()

# Response_type Klines :
# [
#   [
#     1499040000000,      // Kline open time
#     "0.01634790",       // Open price
#     "0.80000000",       // High price
#     "0.01575800",       // Low price
#     "0.01577100",       // Close price
#     "148976.11427815",  // Volume
#     1499644799999,      // Kline Close time
#     "2434.19055334",    // Quote asset volume
#     308,                // Number of trades
#     "1756.87402397",    // Taker buy base asset volume
#     "28.46694368",      // Taker buy quote asset volume
#     "0"                 // Unused field, ignore.
#   ]
# ]

# Response_type 24h :
# {
#   "symbol": "BNBBTC",
#   "priceChange": "-94.99999800",
#   "priceChangePercent": "-95.960",
#   "weightedAvgPrice": "0.29628482",
#   "prevClosePrice": "0.10002000",
#   "lastPrice": "4.00000200",
#   "lastQty": "200.00000000",
#   "bidPrice": "4.00000000",
#   "bidQty": "100.00000000",
#   "askPrice": "4.00000200",
#   "askQty": "100.00000000",
#   "openPrice": "99.00000000",
#   "highPrice": "100.00000000",
#   "lowPrice": "0.10000000",
#   "volume": "8913.30000000",
#   "quoteVolume": "15.30000000",
#   "openTime": 1499783499040,
#   "closeTime": 1499869899040,
#   "firstId": 28385,   // First tradeId
#   "lastId": 28460,    // Last tradeId
#   "count": 76         // Trade count
# }

# Réponse bookTicker :
# {
#   "symbol": "LTCBTC",
#   "bidPrice": "4.00000000",
#   "bidQty": "431.00000000",
#   "askPrice": "4.00000200",
#   "askQty": "9.00000000"
# }
