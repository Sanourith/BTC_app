import requests 

# Premier essai sur Binance, pour récupérer le cours du BTC actuel
url = "https://api.binance.com"

endpoint = "/api/v3/ticker/price"
# Old trade lookup
endpoint_old = "/api/v3/historicalTrades"

params = {
    'symbol': 'BTCUSDT'
}

response = requests.get(url + endpoint, params=params)

if response.status_code == 200:
    data = response.json()
    print(f"Prix actuel du BTC/USDT : {data['price']}")
else: 
    print(f'Erreur : {response.status_code}')

