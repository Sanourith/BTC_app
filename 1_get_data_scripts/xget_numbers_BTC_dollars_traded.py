import requests 

url = "https://api.binance.com/api/v3/ticker/24hr"
params = {
    'symbol': 'BTCUSDT'
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    volume = data['volume']  # Volume en BTC
    quote_volume = data['quoteVolume']  # Volume en USDT
    
    print(f"Volume de BTC tradé dans les dernières 24h : {volume} BTC")
    print(f"Volume en USDT tradé dans les dernières 24h : {quote_volume} USDT")
else:
    print(f"Erreur : {response.status_code}")