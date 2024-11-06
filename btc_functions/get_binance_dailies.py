import os 
import json 
import requests 
from datetime import datetime, timedelta
from logging import getLogger

logger = getLogger(__name__)

# Les endpoints utilisables : klines, ticker/24h

def data_to_json(data, file, start_yesterday):
    if data:
        file_path = f"/home/sanou/BTC/data/1_raw/{file}_{start_yesterday}.json"
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Données enregistrées dans le fichier {file_path}.")
    else:
        logger.warning(f"Erreur sur l'enregistrement de la requête, pas de données.")

def request_data(url, endpoint, params):
    full_endpoint = url + endpoint
    response = requests.get(full_endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Erreur de requête HTTP : {response.status_code}")
        return None 
  
def get_data_from_binance(endpoint):
    url = "https://api.binance.com"
    endpoint = "/api/v3/" + endpoint
    
    now = datetime.now()
    yesterday = now - timedelta(days=5)
    start_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    end_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

    start_timestamp = int(start_yesterday.timestamp() * 1000)
    end_timestamp = int(end_yesterday.timestamp() * 1000)

    if endpoint == "/api/v3/klines":
        params = {
            'symbol': 'BTCUSDT',
            'interval': '5m', #intervalle d'espacement pour revoir les chiffres
            'startTime': start_timestamp,
            'endTime': end_timestamp,
            'limit': 1000
        }
        file = "prices_BTC_KLINES"

    elif endpoint == "/api/v3/ticker/24hr":
        params = {
            'symbol': 'BTCUSDT'
        } 
        file = "prices_BTC_24h"

    elif endpoint == "/api/v3/ticker/bookTicker":
        params ={
            'symbol': 'BTCUSDT'
        }
        file = "bookticker"

    else:
        logger.error(message:= f'Endpoint non utilisable ({endpoint}), utiliser "klines" ou "ticker/24h".')
        raise ValueError(message)
    
    data = request_data(url, endpoint, params)
    if data:
        data_to_json(data, file, start_yesterday)

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
