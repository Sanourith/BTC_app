from logging import getLogger
from dotenv import load_dotenv
import pandas as pd
from btc_functions.logging.logger_config import setup_logger
from btc_functions.transfert_data.get_data_as_df import get_df_change_timestamp
from joblib import dump

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

# import pandas as pd
# import btc_functions.load_database.mysql as db_functions
# from btc_functions.logging.logger_config import setup_logger
import os


logger = getLogger(__name__)


# def get_model_path(
#     model_name: str, base_folder: str = "/home/sanou/BTC_app/models_ml"
# ) -> str:
#     """
#     Génère le chemin d'accès pour sauvegarder un modèle ML et crée le dossier
#     s'il n'existe pas.

#     Args:
#         model_name (str): Nom du modèle.
#         base_folder (str, optional): Dossier de stockage.
#                                         Par défaut : "/home/sanou/BTC_app/models_ml".

#     Returns:
#         str: Chemin complet du fichier modèle.
#     """
#     os.makedirs(base_folder, exist_ok=True)
#     return os.path.join(base_folder, f"{model_name}_model.pickle")


def compute_model_score(model, X, y) -> float:
    """
    Calcule le score de validation croisée négatif moyen carré.

    Args:
        model (sklearn estimator): Modèle à évaluer.
        X (pd.DataFrame): Matrice de caractéristiques.
        y (pd.Series): Variable cible.

    Returns:
        float: Score moyen de validation croisée.
    """
    cross_validation = cross_val_score(
        model, X, y, cv=3, scoring="neg_mean_squared_error"
    )
    score = cross_validation.mean()
    logger.info(f"Score {model}: {score:.4f}")
    return score


def train_and_save_model(model, X, y, path_to_model: str):
    """
    Entraîne un modèle et le sauvegarde dans un fichier.

    Args:
        model (sklearn estimator): Modèle à entraîner.
        X (pd.DataFrame): Matrice de caractéristiques.
        y (pd.Series): Variable cible.
        path_to_model (str): Chemin pour sauvegarder le modèle.
    """
    model.fit(X, y)
    dump(model, path_to_model)
    logger.info(f"Modèle {model} sauvegardé à {path_to_model}")


def prepare_data(df: pd.DataFrame) -> tuple:
    """
    Prépare les données pour l'entraînement ML.

    Args:
        df (pd.DataFrame): DataFrame avec les colonnes nécessaires.

    Returns:
        tuple: (X, y), où X est la matrice de caractéristiques et y la variable cible.
    """
    features_columns = [
        "open_price",
        "high_price",
        "low_price",
        "close_price",
        "volume_x",
        "priceChange",
        "priceChangePercent",
    ]

    X = df[features_columns].copy()
    X["price_change"] = X["close_price"].shift(-1) - df["close_price"]
    X["trend"] = (X["price_change"] > 0).astype(int)
    # 1 si le prix augmente, 0 sinon

    y = X["trend"]
    X = X.drop(["trend", "price_change"], axis=1)
    return X, y


def merge_dfs(df1, df2, col1, col2, typ) -> pd.DataFrame:
    """
    Merges two DataFrames on specified columns.

    Args:
        df1 (pd.DataFrame): First DataFrame.
        df2 (pd.DataFrame): Second DataFrame.
        col1 (str): Column to merge on in df1.
        col2 (str): Column to merge on in df2.
        typ (str): Type of merge (e.g., 'inner', 'outer').

    Returns:
        pd.DataFrame: Merged DataFrame.
    """
    return pd.merge(df1, df2, left_on=col1, right_on=col2, how=typ)


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
    df[col] = pd.to_datetime(df[col]).dt.floor("D")
    if col == "openTime":
        df[col] = df[col] - pd.Timedelta(days=1)
    return df


def train_and_select_best_models(merge_df: pd.DataFrame) -> str:
    """
    Trains multiple models, selects the best, and saves it.

    Args:
        merge_df (pd.DataFrame): DataFrame containing features and target.

    Returns:
        str: The name of the best-performing model.
    """
    X, y = prepare_data(merge_df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    models = {
        "LinearRegression": LinearRegression(),
        "DecisionTreeRegressor": DecisionTreeRegressor(random_state=42),
        "RandomForestRegressor": RandomForestRegressor(random_state=42),
    }

    scores_models = {}
    path_model_folder = "/home/sanou/BTC_app/models_ml"
    os.makedirs(path_model_folder, exist_ok=True)

    for name, model in models.items():
        score = compute_model_score(model, X_train, y_train)
        logger.info(f"Score {name} = {score} <<<")
        scores_models[name] = score
        path_to_model = os.path.join(path_model_folder, f"{name}_model.pickle")
        train_and_save_model(model, X_train, y_train, path_to_model)

    best_model_name = max(scores_models, key=scores_models.get)
    best_model = models[best_model_name]
    logger.info(
        f"{best_model_name} selected with score: {scores_models[best_model_name]:.4f}"
    )
    best_model_path = os.path.join(path_model_folder, f"best_{best_model_name}.pickle")
    train_and_save_model(best_model, X_train, y_train, best_model_path)

    # Prediction
    y_pred = best_model.predict(X_test)
    y_pred_binary = (y_pred > 0.5).astype(int)

    accuracy = (y_test == y_pred_binary).mean()
    logger.info(f"Accuracy of best model ({best_model_name}): {accuracy:.4f}")

    # predictions_df = pd.DataFrame({"Actual": y_test, "Predicted": y_pred_binary})
    # predictions_df.to_csv("/home/sanou/BTC_app/models_ml/predictions.csv", index=False)
    # logger.info("Predictions saved in /home/sanou/BTC_app/models_ml/predictions.csv")

    return best_model_name


# prepare_ml
def main():
    setup_logger()
    logger.info("Starting data preparation...")

    df_klines = get_df_change_timestamp("klines", "kline_open_time", "kline_close_time")
    df_daily = get_df_change_timestamp("daily", "openTime", "closeTime")

    logger.info("Récupération des DataFrames Klines & 24hr. Préparation merge")

    df_klines = format_time_ml(df_klines, "kline_open_time")
    df_daily = format_time_ml(df_daily, "openTime")
    logger.info("DataFrames formatted successfully.")

    try:
        merge_df = merge_dfs(
            df_klines, df_daily, "kline_open_time", "openTime", "inner"
        )
        logger.info("DataFrames merged successfully.")
    except BufferError as e:
        raise BufferError(f"Error merging tables: {e}.")

    best_model = train_and_select_best_models(merge_df)
    logger.info(f"Best model : {best_model}")

    return


# TODO : check la cohérence et la réponse ML pour le projet

if __name__ == "__main__":
    load_dotenv("/home/sanou/BTC_app/env/private.env")
    main()


# model = load("/home/sanou/BTC_app/models_ml/best_LinearRegression().pickle")

# prediction = model.predict(df)[0]
# logger.info(f"{prediction = }")
