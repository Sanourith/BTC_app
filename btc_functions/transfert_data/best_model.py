import logging
import os
from pathlib import Path
import pandas as pd
import numpy as np
from joblib import dump, load
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, accuracy_score

logger = logging.getLogger(__name__)

# Constants
FEATURES_COLUMNS = [
    "open_price",
    "high_price",
    "low_price",
    "close_price",
    "volume_x",
    "priceChange",
    "priceChangePercent",
]
MODEL_FOLDER = os.path.expanduser("~/BTC_app/models_ml")


def compute_model_score(model, X, y, cv=3) -> float:
    """
    Calcule le score de validation croisée et retourne l'opposé du MSE pour
    compatibilité avec les fonctions de maximisation.

    Args:
        model (sklearn estimator): Modèle à évaluer.
        X (pd.DataFrame): Matrice de caractéristiques.
        y (pd.Series): Variable cible.
        cv (int): Nombre de plis pour validation croisée.

    Returns:
        float: Score moyen de validation croisée (négatif du MSE).
    """
    with np.errstate(divide="ignore", invalid="ignore"):
        cross_validation = cross_val_score(
            model, X, y, cv=cv, scoring="neg_mean_squared_error"
        )
    score = cross_validation.mean()
    logger.info(f"Score {type(model).__name__}: {score:.4f}")
    return score


def train_and_save_model(model, X, y, path_to_model):
    """
    Entraîne un modèle et le sauvegarde dans un fichier.

    Args:
        model (sklearn estimator): Modèle à entraîner.
        X (pd.DataFrame): Matrice de caractéristiques.
        y (pd.Series): Variable cible.
        path_to_model (str or Path): Chemin pour sauvegarder le modèle.
    """
    model.fit(X, y)
    dump(model, path_to_model)
    logger.info(f"Modèle {type(model).__name__} sauvegardé à {path_to_model}")


def prepare_data(df: pd.DataFrame) -> tuple:
    """
    Prépare les données pour l'entraînement ML.

    Args:
        df (pd.DataFrame): DataFrame avec les colonnes nécessaires.

    Returns:
        tuple: (X, y), où X est la matrice de caractéristiques et y la variable cible.
    """
    missing_cols = [col for col in FEATURES_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Colonnes manquantes dans le DataFrame: {missing_cols}")

    # Copier seulement les colonnes nécessaires
    X = df[FEATURES_COLUMNS].copy()

    # Calcul de la variation de prix pour la prédiction
    X["price_change"] = X["close_price"].shift(-1) - X["close_price"]

    # Création de la variable cible (tendance: hausse ou baisse)
    y = (X["price_change"] > 0).astype(int)

    # Supprimer la colonne price_change qui contient des informations futures
    X = X.drop(["price_change"], axis=1)

    # Supprimer les lignes avec des valeurs manquantes
    valid_indices = ~X.isna().any(axis=1) & ~y.isna()
    X = X[valid_indices]
    y = y[valid_indices]

    return X, y


def merge_dfs(df1, df2, col1, col2, typ="inner") -> pd.DataFrame:
    """
    Merges two DataFrames on specified columns with error handling.

    Args:
        df1 (pd.DataFrame): First DataFrame.
        df2 (pd.DataFrame): Second DataFrame.
        col1 (str): Column to merge on in df1.
        col2 (str): Column to merge on in df2.
        typ (str): Type of merge (e.g., 'inner', 'outer').

    Returns:
        pd.DataFrame: Merged DataFrame.
    """
    # Vérification de la présence des colonnes
    if col1 not in df1.columns:
        raise ValueError(f"Colonne {col1} non trouvée dans le premier DataFrame")
    if col2 not in df2.columns:
        raise ValueError(f"Colonne {col2} non trouvée dans le deuxième DataFrame")

    # Effectuer la fusion
    try:
        merged_df = pd.merge(df1, df2, left_on=col1, right_on=col2, how=typ)
        logger.info(f"Fusion réussie: {len(merged_df)} lignes résultantes")
        return merged_df
    except Exception as e:
        logger.error(f"Erreur lors de la fusion: {str(e)}")
        raise


def format_time_ml(df, col) -> pd.DataFrame:
    """
    Formats a DataFrame column as datetime, floored to day, and adjusts
    specific columns if needed.

    Args:
        df (pd.DataFrame): Input DataFrame.
        col (str): Column name to format.

    Returns:
        pd.DataFrame: DataFrame with formatted time column.
    """
    if col not in df.columns:
        raise ValueError(f"Colonne {col} non trouvée dans le DataFrame")

    # Créer une copie pour éviter les SettingWithCopyWarning
    result_df = df.copy()

    # Convertir en datetime et arrondir au jour
    result_df[col] = pd.to_datetime(result_df[col]).dt.floor("D")

    # Ajustement spécifique pour openTime
    if col == "openTime":
        result_df[col] = result_df[col] - pd.Timedelta(days=1)

    return result_df


def train_and_select_best_models(merge_df: pd.DataFrame) -> str:
    """
    Trains multiple models, selects the best, and saves it.

    Args:
        merge_df (pd.DataFrame): DataFrame containing features and target.

    Returns:
        str: The name of the best-performing model.
    """
    X, y = prepare_data(merge_df)
    if len(X) == 0:
        raise ValueError("Aucune donnée valide après préparation")

    # Division train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Normalisation des données
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Sauvegarde du scaler pour utilisation future
    os.makedirs(MODEL_FOLDER, exist_ok=True)
    dump(scaler, os.path.join(MODEL_FOLDER, "scaler.pickle"))

    # Définition des modèles à tester
    models = {
        "LinearRegression": LinearRegression(),
        "DecisionTreeRegressor": DecisionTreeRegressor(random_state=42),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=100, random_state=42
        ),
    }

    # Évaluation des modèles
    scores_models = {}
    for name, model in models.items():
        # Calcul du score par validation croisée
        score = compute_model_score(model, X_train_scaled, y_train)
        scores_models[name] = score

        # Entraînement et sauvegarde du modèle
        path_to_model = os.path.join(MODEL_FOLDER, f"{name}_model.pickle")
        train_and_save_model(model, X_train_scaled, y_train, path_to_model)

    # Sélection du meilleur modèle
    best_model_name = max(scores_models, key=scores_models.get)
    best_model = models[best_model_name]
    logger.info(
        f"{best_model_name} sélectionné avec score: {scores_models[best_model_name]:.4f}"
    )

    # Sauvegarde du meilleur modèle
    best_model_path = os.path.join(MODEL_FOLDER, f"best_model.pickle")
    train_and_save_model(best_model, X_train_scaled, y_train, best_model_path)

    # Évaluation sur l'ensemble de test
    y_pred = best_model.predict(X_test_scaled)
    y_pred_binary = (y_pred > 0.5).astype(int)

    # Calcul des métriques
    mse = mean_squared_error(y_test, y_pred)
    accuracy = accuracy_score(y_test, y_pred_binary)

    logger.info(f"MSE du meilleur modèle ({best_model_name}): {mse:.4f}")
    logger.info(f"Précision du meilleur modèle ({best_model_name}): {accuracy:.4f}")

    # Sauvegarde des prédictions pour analyse
    predictions_df = pd.DataFrame(
        {"Actual": y_test, "Predicted_Raw": y_pred, "Predicted_Binary": y_pred_binary}
    )
    predictions_path = os.path.join(MODEL_FOLDER, "predictions.csv")
    predictions_df.to_csv(predictions_path, index=False)
    logger.info(f"Prédictions sauvegardées dans {predictions_path}")

    return best_model_name
