import pandas as pd
from datetime import datetime
import logging
from contextlib import contextmanager
from pathlib import Path

from ..logging.logger_config import setup_logger
from ..load_database import mysql as db_functions

logger = logging.getLogger(__name__)


@contextmanager
def database_connection():
    """
    Gestionnaire de contexte pour la connexion à la base de données.
    Assure la fermeture de la connexion même en cas d'exception.
    """
    connection = None
    try:
        connection = db_functions.create_connection()
        yield connection
    except Exception as e:
        logger.error(f"Erreur de connexion à la base de données: {e}")
        raise
    finally:
        if connection:
            connection.close()
            logger.debug("Connexion à la base de données fermée")


def get_df_change_timestamp(table_name, col1, col2=None) -> pd.DataFrame:
    """
    Récupère une table SQL, applique reverse_timestamp sur les cols BIGINT spécifiées
    et retourne le DataFrame.

    Args:
        table_name (str): nom de la table cible (type BIGINT / timestamp)
        col1 (str): colonne à convertir en timestamp
        col2 (str, optional): 2e colonne à convertir. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame avec les colonnes de timestamp converties
    """
    setup_logger()

    # Construction de la requête
    query = f"SELECT * FROM {table_name}"

    # Récupération des données avec gestion de la connexion
    with database_connection() as engine:
        try:
            df = pd.read_sql_query(query, engine)
            logger.info(f"Table {table_name} récupérée avec succès: {len(df)} lignes")
        except Exception as e:
            logger.error(
                f"Erreur lors de la récupération de la table {table_name}: {e}"
            )
            raise

    # Conversion des timestamps
    if not df.empty:
        df = reverse_timestamp(df, col1, col2)

    return df


def reverse_timestamp(df: pd.DataFrame, col1: str, col2: str = None) -> pd.DataFrame:
    """
    Convertit les colonnes de timestamp Unix (millisecondes) en datetime.

    Args:
        df (pd.DataFrame): DataFrame source
        col1 (str): nom de la première colonne à transformer
        col2 (str, optional): nom de la deuxième colonne à transformer. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame avec les colonnes converties
    """
    cols = [col for col in [col1, col2] if col is not None]
    missing_cols = [col for col in cols if col not in df.columns]

    if missing_cols:
        logger.warning(f"Colonnes non trouvées dans le DataFrame: {missing_cols}")
        # Filtrer les colonnes manquantes
        cols = [col for col in cols if col in df.columns]

    if not cols:
        logger.warning("Aucune colonne valide à convertir")
        return df

    # Copie du DataFrame pour éviter les modifications en place
    result = df.copy()

    # Conversion plus efficace avec vectorisation
    for col in cols:
        try:
            # Conversion des timestamps de millisecondes à datetime
            result[col] = pd.to_datetime(result[col], unit="ms")
            logger.debug(f"Colonne {col} convertie en datetime")
        except Exception as e:
            logger.error(f"Erreur lors de la conversion de la colonne {col}: {e}")

    return result


def load_best_model():
    """
    Charge le meilleur modèle entraîné et le scaler associé.

    Returns:
        tuple: (model, scaler) - le modèle et le scaler pour les nouvelles prédictions
    """
    model_folder = Path("~/BTC_app/models_ml").expanduser()

    try:
        model_path = model_folder / "best_model.pickle"
        scaler_path = model_folder / "scaler.pickle"

        if not model_path.exists() or not scaler_path.exists():
            logger.error("Modèle ou scaler non trouvé")
            return None, None

        from joblib import load

        model = load(model_path)
        scaler = load(scaler_path)

        logger.info(f"Modèle {type(model).__name__} chargé avec succès")
        return model, scaler

    except Exception as e:
        logger.error(f"Erreur lors du chargement du modèle: {e}")
        return None, None


def predict_trend(X, model=None, scaler=None):
    """
    Prédit la tendance du prix du Bitcoin avec le modèle entraîné.

    Args:
        X (pd.DataFrame): Features pour la prédiction
        model: Modèle préchargé (optionnel)
        scaler: Scaler préchargé (optionnel)

    Returns:
        dict: Résultat de la prédiction avec probabilités et tendance
    """
    if model is None or scaler is None:
        model, scaler = load_best_model()
        if model is None:
            return {"error": "Impossible de charger le modèle"}

    try:
        # Préparation des données
        X_scaled = scaler.transform(X)

        # Prédiction
        prediction_raw = model.predict(X_scaled)
        prediction_binary = (prediction_raw > 0.5).astype(int)

        return {
            "prediction_raw": (
                float(prediction_raw[0])
                if hasattr(prediction_raw, "__len__")
                else float(prediction_raw)
            ),
            "trend": "HAUSSE" if prediction_binary[0] == 1 else "BAISSE",
            "confidence": (
                abs(float(prediction_raw[0]) - 0.5) * 2
                if hasattr(prediction_raw, "__len__")
                else abs(float(prediction_raw) - 0.5) * 2
            ),
        }

    except Exception as e:
        logger.error(f"Erreur lors de la prédiction: {e}")
        return {"error": str(e)}
