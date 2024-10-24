from btc_functions.get_binance_dailies import get_data_from_binance
from btc_functions.logger_config import setup_logger
import logging

logger = logging.getLogger(__name__)

def main():
    setup_logger()
    endpoints = ["klines", "ticker/24hr"]
    for endpoint in endpoints:
        get_data_from_binance(endpoint)
        logger.info(f"Données ajoutées depuis la fonction pour {endpoint}")

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