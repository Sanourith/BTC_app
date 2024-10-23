import os 
import json 
import requests 
from datetime import datetime, timedelta

url = "https://api.binance.com"
# /klines
endpoint_Klines = "/api/v3/klines"
endpoint_24h = "/api/v3/ticker/24hr"

now = datetime.now()
yesterday = now - timedelta(days=1)
start_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
end_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

start_timestamp = int(start_yesterday.timestamp() * 1000)
end_timestamp = int(end_yesterday.timestamp() * 1000)

params_Klines = {
    'symbol': 'BTCUSDT',
    'interval': '5m', #intervalle d'espacement pour revoir les chiffres
    'startTime': start_timestamp,
    'endTime': end_timestamp,
    'limit': 1000
}

response_k = requests.get(url + endpoint_Klines, params=params_Klines)
if response_k.status_code == 200:
    data = response_k.json()
    file_path = f"/home/sanou/BTC/data/1_raw/prices_BTC_KLINES{start_yesterday}.json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Données enregistrées dans le fichier {file_path}.")
else:
    print(f"Erreur sur la requête Kline : {response_k.status_code}")

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

params_24h = {
    'symbol': 'BTCUSDT'
}

response_24 = requests.get(url + endpoint_24h, params=params_24h)
if response_24.status_code == 200:
    data = response_24.json()
    file_path = f"/home/sanou/BTC/data/1_raw/prices_BTC_24h_{start_yesterday}.json"
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Données enregistrées dans le fichier {file_path}.")
else:
    print(f"Erreur sur la requête Kline : {response_k.status_code}")

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