# Objectifs du projet : (WIP)

## Récolter deux types de données:  

1.	Récolte des données, Extraction et Transformation


On peut aller récupérer des informations sur les cours des différents marchés (BTC-USDT, BTC-ETH, …).
Le but sera de créer une fonction de récupération de données générique afin de pouvoir avoir les données de n’importe quel marché.
Il faudra aussi créer un script de pré-processing pour réorganiser les données sortant du streaming afin qu’elles soient propres.

2.	Récupérer les données historiques, pré-processer pour pouvoir entraîner notre futur modèle

## Stockage de la donnée

## Consommation de la donnée

1. Utiliser un algo de Machine Learning appliqué à la finance qui permettra de retourner une décision d’achat ou non.
Aller plus loin: prédiction de gains

2. Il faudra aussi mettre en place ML Flow pour pouvoir faire du versioning de Modèles.

## Mesurer la dérive de la donnée

1. Faire une API pour tester le modèle de ML et pourquoi pas requêter les données historique

2. Dockeriser tout le projet pour qu’il soit reproduisible sur n’importe quel machine

3. Mesurer la dérive des données

## Automatisation des flux de monitoring

1. Il faudra automatiser à l’aide d’outils diverses la récupération des données

2. Créer un pipeline simple de CI pour déployer des nouveautés

3. Il faudra aussi monitorer l’application en production ainsi que les logs API

### Bibliographie :
https://www.binance.com/fr/binance-api

https://binance-docs.github.io/apidocs/spot/en/#change-log

Beaucoup de bots de trading sur youtube ou sur des github
