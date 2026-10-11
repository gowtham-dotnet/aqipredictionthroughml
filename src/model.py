"""
Model definitions, evaluation metrics, and utility functions.
Includes all regression models from the original notebook.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from math import sqrt
import yaml
import os

# Load configuration (relative to project root)
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

RANDOM_STATE = config['training']['random_state']


def create_linear_regression():
    """Create a Linear Regression model."""
    return LinearRegression(**config['model']['linear_regression'])


def create_polynomial_regression(degree=2):
    """
    Create a pipeline: PolynomialFeatures + LinearRegression.
    Returns (poly_transformer, linear_model) for separate fit/transform steps.
    """
    poly = PolynomialFeatures(degree=degree)
    lin_reg = LinearRegression(**config['model']['linear_regression'])
    return poly, lin_reg


def create_decision_tree():
    """Create a Decision Tree Regressor."""
    return DecisionTreeRegressor(**config['model']['decision_tree'])


def create_random_forest(params=None):
    """Create a Random Forest Regressor. If params is None, use config defaults."""
    if params is None:
        params = config['model']['random_forest']
    return RandomForestRegressor(**params)


def evaluate_model(y_true, y_pred):
    """
    Compute RMSE, MAE, R² and return as a dict.
    """
    rmse = sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return {'RMSE': rmse, 'MAE': mae, 'R2': r2}


def print_metrics(metrics, title="Model Performance"):
    """Pretty print evaluation metrics."""
    print(f"\n{title}")
    print(f"RMSE: {metrics['RMSE']:.4f}")
    print(f"MAE : {metrics['MAE']:.4f}")
    print(f"R²  : {metrics['R2']:.4f}")


def get_aqi_quality(aqi):
    """Map AQI value to qualitative category."""
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Satisfactory"
    elif aqi <= 200:
        return "Moderate"
    elif aqi <= 300:
        return "Poor"
    elif aqi <= 400:
        return "Very Poor"
    else:
        return "Severe"
    

