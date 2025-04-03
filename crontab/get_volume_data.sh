#! /bin/bash

echo "Extraction des données J-1 sur Binance, pour les données suivantes :"
echo "Open price, High price, Low price, Close price, Volume, Number of Trades, Taker assets buy volume"

cd
source .venv_btc/bin/activate

cd /home/sanou/BTC_app/docker-compose

docker compose up -d

sleep 5

python3 /home/sanou/BTC_app/src/1_get_binance_daily_data.py
echo "Extraction des données du jour terminée."

sleep 3

python3 /home/sanou/BTC_app/src/2_transfert_data.py
echo "Transfert des données vers MySQL effectué."

sleep 3

python3 /home/sanou/BTC_app/src/3_etl_prepare_ml.py
echo "Enregistrement des modèles terminée"

sleep 3

docker compose down

sleep 2

deactivate