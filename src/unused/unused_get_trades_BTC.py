import requests
import os
import json
from datetime import datetime, timedelta

url = "https://api.binance.com/api/v3/aggTrades"

now = datetime.now()
yesterday = now - timedelta(days=1)
start_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
end_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)

start_timestamp = int(start_yesterday.timestamp() * 1000)
end_timestamp = int(end_yesterday.timestamp() * 1000)

all_data = []
from_id = None

while True:
    # params API
    params = {"symbol": "BTCUSDT", "limit": 1000}

    if from_id is None:
        params["startTime"] = start_timestamp
        params["endTime"] = end_timestamp
    else:
        params["fromId"] = from_id

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if not data:
            print("Fin de boucle")
            break

        all_data.extend(data)
        from_id = data[-1]["a"]
        print(f"Nombre d'ordres récupérés : {len(all_data)}")
    else:
        print(f"Erreur : {response.status_code}")

file_path = f"~/BTC/data/1_raw/aggTrades_BTC_{start_yesterday}.json"
os.makedirs(os.path.dirname(file_path), exist_ok=True)

with open(file_path, "w") as f:
    json.dump(data, f, indent=4)

print(f"Données stockées dans le fichier {file_path}")


# Response_type :
# [
#   {
#     "a": 26129,         // Aggregate tradeId
#     "p": "0.01633102",  // Price
#     "q": "4.70443515",  // Quantity
#     "f": 27781,         // First tradeId
#     "l": 27781,         // Last tradeId
#     "T": 1498793709153, // Timestamp
#     "m": true,          // Was the buyer the maker?
#     "M": true           // Was the trade the best price match?
#   }
# ]
