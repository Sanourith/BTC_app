#! /bin/bash

echo "Extraction des données J-1 sur Binance, pour les données suivantes :"
echo "Open price, High price, Low price, Close price, Volume, Number of Trades, Taker assets buy volume"

cd /home/sanou/BTC/docker-compose
docker compose up -d

wait 10

python3 /home/sanou/BTC/1_get_data_scripts/get_binance_daily_data.py
echo "Extraction des données du jour terminée."

wait 10

python3 /home/sanou/BTC/2_store_data_scripts/transfert_data_to_mysql.py
echo "Transfert des données vers MySQL effectué."

docker compose down