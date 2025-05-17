import os
import sys
import logging
import argparse
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
from btc_functions.logging.logger_config import setup_logger
from btc_functions.transfert_data.get_data_as_df import get_df_change_timestamp
import btc_functions.transfert_data.best_model as bm

# Ajout du répertoire parent au chemin de recherche des modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Préparation des données et entraînement de modèles ML pour Bitcoin"
    )
    parser.add_argument(
        "--env-file",
        type=str,
        default="~/BTC_app/env/private.env",
        help="Chemin vers le fichier .env avec les variables d'environnement",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="~/BTC_app/models_ml",
        help="Répertoire de sortie pour les modèles et prédictions",
    )
    parser.add_argument("--debug", action="store_true", help="Activer le mode debug")
    return parser.parse_args()


def prepare_data():
    """
    Récupère et prépare les données pour l'entraînement.

    Returns:
        pd.DataFrame: DataFrame fusionné prêt pour l'entraînement
    """
    try:
        # Récupération des données depuis la base
        logger.info("Récupération des données de klines...")
        df_klines = get_df_change_timestamp(
            "klines", "kline_open_time", "kline_close_time"
        )

        logger.info("Récupération des données quotidiennes...")
        df_daily = get_df_change_timestamp("daily", "openTime", "closeTime")

        # Vérification des données récupérées
        if df_klines.empty or df_daily.empty:
            raise ValueError("Les DataFrames récupérés sont vides")

        logger.info(
            f"Données récupérées: {len(df_klines)} klines, {len(df_daily)} entrées quotidiennes"
        )

        # Formatage des colonnes temporelles
        df_klines = bm.format_time_ml(df_klines, "kline_open_time")
        df_daily = bm.format_time_ml(df_daily, "openTime")
        logger.info("Formatage des colonnes temporelles effectué")

        # Fusion des DataFrames
        merge_df = bm.merge_dfs(
            df_klines, df_daily, "kline_open_time", "openTime", "inner"
        )
        logger.info(f"Fusion réussie: {len(merge_df)} lignes résultantes")

        return merge_df

    except Exception as e:
        logger.error(f"Erreur lors de la préparation des données: {e}")
        raise


def main():
    """
    Fonction principale du script ETL.
    """
    args = parse_arguments()

    # Configuration du logger
    setup_logger()

    # Chargement des variables d'environnement
    env_path = os.path.expanduser(args.env_file)
    if os.path.exists(env_path):
        load_dotenv(env_path)
        logger.info(f"Variables d'environnement chargées depuis {env_path}")
    else:
        logger.warning(f"Fichier d'environnement {env_path} non trouvé")

    # Création du répertoire de sortie si nécessaire
    output_dir = Path(os.path.expanduser(args.output_dir))
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=== Démarrage du processus ETL ===")

    try:
        # Préparation des données
        logger.info("Préparation des données...")
        merge_df = prepare_data()

        # Sauvegarde du DataFrame fusionné pour analyse
        sample_path = output_dir / "sample_data.csv"
        merge_df.head(100).to_csv(sample_path, index=False)
        logger.info(f"Échantillon de données sauvegardé dans {sample_path}")

        # Entraînement des modèles
        logger.info("Entraînement des modèles...")
        best_model = bm.train_and_select_best_models(merge_df)
        logger.info(f"Meilleur modèle: {best_model}")

        # Résumé des opérations
        logger.info("=== Processus ETL terminé avec succès ===")
        return 0

    except Exception as e:
        logger.error(f"Erreur lors du processus ETL: {e}")
        logger.exception("Détails de l'erreur:")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
