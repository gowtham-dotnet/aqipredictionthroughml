import os
import pickle
import yaml
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.utils import resample
from tqdm import tqdm
import mlflow
import mlflow.sklearn
import gc

from .data_loader import load_data, preprocess_data, get_features_target
from .model import (create_linear_regression, create_polynomial_regression,
                    create_decision_tree, create_random_forest,
                    evaluate_model, print_metrics, get_aqi_quality)

with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

RANDOM_STATE = config['training']['random_state']
TEST_SIZE = config['training']['test_size']


def predict_in_batches(model, X, batch_size=10000, desc="Predicting"):
    """Make predictions in batches to control memory usage."""
    n_samples = len(X)
    n_batches = (n_samples + batch_size - 1) // batch_size
    predictions = []
    with tqdm(total=n_batches, desc=desc, unit="batch", leave=False) as pbar:
        for i in range(0, n_samples, batch_size):
            end = min(i + batch_size, n_samples)
            pred = model.predict(X[i:end])
            predictions.append(pred)
            pbar.update(1)
    return np.concatenate(predictions)


def train_and_evaluate_all_models(X_train, X_test, y_train, y_test):
    models = {}

    # 1. Linear Regression
    print("\n--- Linear Regression ---")
    lr = create_linear_regression()
    with tqdm(total=100, desc="Training Linear Regression", leave=False) as pbar:
        lr.fit(X_train, y_train)
        pbar.update(100)
    y_pred = lr.predict(X_test)
    print_metrics(evaluate_model(y_test, y_pred), "Test Set")
    models['LinearRegression'] = lr
    gc.collect()

    # 2. Polynomial Regression (degree=2) – memory safe version (sampling is kept)
    print("\n--- Polynomial Regression (degree=2) ---")
    sample_size = min(100000, len(X_train))
    print(f"  Using {sample_size} samples for training ({(sample_size/len(X_train)*100):.1f}%)")
    X_train_sampled, y_train_sampled = resample(
        X_train, y_train, n_samples=sample_size, random_state=RANDOM_STATE, replace=False
    )

    poly = PolynomialFeatures(degree=2, include_bias=False)
    with tqdm(total=100, desc="Fitting polynomial features", leave=False) as pbar:
        X_train_poly = poly.fit_transform(X_train_sampled)
        pbar.update(50)
        scaler = StandardScaler()
        X_train_poly = scaler.fit_transform(X_train_poly)
        pbar.update(50)

    lin_reg = LinearRegression()
    with tqdm(total=100, desc="Training Polynomial Regression", leave=False) as pbar:
        lin_reg.fit(X_train_poly, y_train_sampled)
        pbar.update(100)

    print("  Transforming test set in batches...")
    batch_size = 5000
    n_test = len(X_test)
    n_batches = (n_test + batch_size - 1) // batch_size
    y_pred_batches = []
    with tqdm(total=n_batches, desc="Test set batches", unit="batch", leave=False) as pbar:
        for i in range(0, n_test, batch_size):
            end = min(i + batch_size, n_test)
            X_batch = X_test[i:end]
            X_batch_poly = poly.transform(X_batch)
            X_batch_poly = scaler.transform(X_batch_poly)
            y_batch_pred = lin_reg.predict(X_batch_poly)
            y_pred_batches.append(y_batch_pred)
            pbar.update(1)
    y_pred = np.concatenate(y_pred_batches)

    print_metrics(evaluate_model(y_test, y_pred), "Test Set")
    models['PolynomialRegression'] = (poly, scaler, lin_reg)
    gc.collect()

    # 3. Decision Tree
    print("\n--- Decision Tree Regression ---")
    dt = create_decision_tree()
    with tqdm(total=100, desc="Training Decision Tree", leave=False) as pbar:
        dt.fit(X_train, y_train)
        pbar.update(100)
    y_pred = dt.predict(X_test)
    print_metrics(evaluate_model(y_test, y_pred), "Test Set")
    models['DecisionTree'] = dt
    gc.collect()

    # 4. Random Forest (default params) – NOW USING FULL DATA
    print("\n--- Random Forest Regression (default) ---")
    rf_params = config['model']['random_forest'].copy()
    rf_params['n_jobs'] = 1          # keep parallelism low to avoid memory spikes
    rf = RandomForestRegressor(**rf_params)
    with tqdm(total=100, desc="Training Random Forest", leave=False) as pbar:
        rf.fit(X_train, y_train)
        pbar.update(100)
    y_pred = predict_in_batches(rf, X_test, desc="RF Prediction")
    print_metrics(evaluate_model(y_test, y_pred), "Test Set")
    models['RandomForest_default'] = rf
    gc.collect()

    return models


def perform_grid_search(X_train, y_train):
    print("\n--- Grid Search for Random Forest ---")
    rf = RandomForestRegressor(random_state=RANDOM_STATE)
    param_grid = config['training']['grid_search_params']
    n_jobs = config['training'].get('grid_search_n_jobs', 1)   # sequential to save memory
    grid_search = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=5,
        scoring='neg_mean_squared_error',
        n_jobs=n_jobs,
        verbose=1
    )
    # No sampling – use full training data
    grid_search.fit(X_train, y_train)
    print(f"Best parameters: {grid_search.best_params_}")
    print(f"Best CV RMSE: {np.sqrt(-grid_search.best_score_):.4f}")
    return grid_search.best_estimator_, grid_search.best_params_


def train_best_model(X_train, y_train):
    if config['training']['perform_grid_search']:
        best_rf, _ = perform_grid_search(X_train, y_train)
        print("Training final model with best parameters...")
        # No sampling – train on full data
        with tqdm(total=100, desc="Training Best RF", leave=False) as pbar:
            best_rf.fit(X_train, y_train)
            pbar.update(100)
    else:
        best_rf = create_random_forest()
        with tqdm(total=100, desc="Training Random Forest", leave=False) as pbar:
            best_rf.fit(X_train, y_train)
            pbar.update(100)
    return best_rf


def save_model(model, path):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
    with open(path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {path}")


def run_clustering_analysis(df):
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    import matplotlib.pyplot as plt

    print("\n--- Clustering Analysis ---")
    X_clust = df.drop(columns=['AQI', 'Air_quality'], errors='ignore')
    X_clust = X_clust.select_dtypes(include=[np.number])

    # Sampling for clustering is optional – keep if you want faster execution
    max_cluster_samples = 50000
    if len(X_clust) > max_cluster_samples:
        X_clust = X_clust.sample(n=max_cluster_samples, random_state=RANDOM_STATE)

    n_clusters = config['clustering']['n_clusters']
    kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=RANDOM_STATE)
    with tqdm(total=100, desc="K-Means", leave=False) as pbar:
        clusters = kmeans.fit_predict(X_clust)
        pbar.update(100)

    if 'PM2.5' in X_clust.columns and 'PM10' in X_clust.columns:
        os.makedirs(config['output']['plots_dir'], exist_ok=True)
        plt.figure(figsize=(8, 6))
        plt.scatter(X_clust['PM2.5'], X_clust['PM10'], c=clusters, cmap='viridis')
        plt.xlabel('PM2.5')
        plt.ylabel('PM10')
        plt.title('K-Means Clustering')
        plt.savefig(os.path.join(config['output']['plots_dir'], 'kmeans_clusters.png'))
        plt.close()
        print("K-Means plot saved.")

    if config['clustering']['perform_pca']:
        n_comp = config['clustering']['pca_components']
        pca = PCA(n_components=n_comp)
        with tqdm(total=100, desc="PCA", leave=False) as pbar:
            pca_result = pca.fit_transform(X_clust)
            pbar.update(100)
        os.makedirs(config['output']['plots_dir'], exist_ok=True)
        plt.figure(figsize=(8, 6))
        plt.scatter(pca_result[:, 0], pca_result[:, 1])
        plt.xlabel('PC1')
        plt.ylabel('PC2')
        plt.title('PCA Results')
        plt.savefig(os.path.join(config['output']['plots_dir'], 'pca.png'))
        plt.close()
        print("PCA plot saved.")


def demo_prediction(models, sample_input):
    print("\n--- Sample Prediction Demo ---")
    feature_names = ['PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3',
                     'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene']
    sample_df = pd.DataFrame([sample_input], columns=feature_names)

    lr = models.get('LinearRegression')
    if lr:
        pred = lr.predict(sample_df)[0]
        print(f"Linear Regression: AQI = {pred:.2f} ({get_aqi_quality(pred)})")

    pr = models.get('PolynomialRegression')
    if pr:
        poly, scaler, lin_reg = pr
        X_poly = poly.transform(sample_df)
        X_poly = scaler.transform(X_poly)
        pred = lin_reg.predict(X_poly)[0]
        print(f"Polynomial Regression: AQI = {pred:.2f} ({get_aqi_quality(pred)})")

    dt = models.get('DecisionTree')
    if dt:
        pred = dt.predict(sample_df)[0]
        print(f"Decision Tree: AQI = {pred:.2f} ({get_aqi_quality(pred)})")

    rf = models.get('RandomForest_default') or models.get('RandomForest_best')
    if rf:
        pred = rf.predict(sample_df)[0]
        print(f"Random Forest: AQI = {pred:.2f} ({get_aqi_quality(pred)})")


def train_pipeline(data_source=None):
    mlflow.set_tracking_uri(config['mlflow']['tracking_uri'])
    mlflow.set_experiment(config['mlflow']['experiment_name'])

    print("Loading data...")
    with tqdm(total=100, desc="Loading", leave=False) as pbar:
        df_raw = load_data(data_source)
        pbar.update(50)
        print("Preprocessing...")
        df_clean = preprocess_data(df_raw)
        pbar.update(50)

    sample_frac = config['training'].get('sample_frac', 1.0)
    if sample_frac < 1.0:
        with tqdm(total=100, desc="Sampling data", leave=False) as pbar:
            df_clean = df_clean.sample(frac=sample_frac, random_state=RANDOM_STATE)
            pbar.update(100)
        print(f"Using {sample_frac*100:.0f}% of data ({len(df_clean)} rows)")

    X, y = get_features_target(df_clean)
    print(f"Final dataset shape: {X.shape}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print(f"Train size: {X_train.shape[0]}, Test size: {X_test.shape[0]}")

    all_models = train_and_evaluate_all_models(X_train, X_test, y_train, y_test)

    if config['clustering']['perform_kmeans']:
        run_clustering_analysis(df_clean)

    with mlflow.start_run():
        best_rf = train_best_model(X_train, y_train)
        # Use batched prediction for the best RF to avoid memory issues
        y_pred = predict_in_batches(best_rf, X_test, desc="Best RF Prediction")
        test_metrics = evaluate_model(y_test, y_pred)
        print("\n--- Best Random Forest on Test Set ---")
        print_metrics(test_metrics)

        with tqdm(total=100, desc="MLflow logging", leave=False) as pbar:
            mlflow.log_params(best_rf.get_params())
            pbar.update(33)
            mlflow.log_metrics({'test_rmse': test_metrics['RMSE'],
                                'test_mae': test_metrics['MAE'],
                                'test_r2': test_metrics['R2']})
            pbar.update(33)
            mlflow.sklearn.log_model(best_rf, "random_forest_model")
            pbar.update(34)
        print("Model logged to MLflow.")

    save_model(best_rf, config['output']['model_save_path'])
    all_models['RandomForest_best'] = best_rf

    sample_input = [26, 50, 1, 19, 18, 23, 1, 3, 42, 2, 6, 1]
    demo_prediction(all_models, sample_input)

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_source', type=str, default=None)
    args = parser.parse_args()
    train_pipeline(args.data_source)