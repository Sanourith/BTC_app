from setuptools import setup, find_packages

setup(
    name="btc_functions",
    version="0.1",
    packages=find_packages(),
    author="Matthieu Serrano",
    install_requires=[  # Dépendances requises
        "requests",  # Par exemple, requests pour faire des requêtes HTTP
        "mysql-connector-python",  # Si tu utilises un connecteur MySQL
        # Si autres dépendances nécessaires
    ],
    # entry_points={
    #     'console_scripts': [
    #         'get_binance_data = btc_functions.get_binance_data:main', # Exemple de point d'entrée
    #     ]
    # },
)
