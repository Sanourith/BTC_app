#! /bin/bash

echo "Extraction des données J-1 sur Binance, pour les données suivantes :"
echo "Open price, High price, Low price, Close price, Volume, Number of Trades, Taker assets buy volume"

cd
source venv/bin/activate

cd /home/sanou/BTC_app/docker-compose

docker compose up -d

sleep 10

python3 /home/sanou/BTC_app/1_python_scripts/1_get_binance_daily_data.py
echo "Extraction des données du jour terminée."

sleep 10

python3 /home/sanou/BTC_app/1_python_scripts/2_transfert_data.py
echo "Transfert des données vers MySQL effectué."

sleep 10

docker compose down

sleep 5

deactivate