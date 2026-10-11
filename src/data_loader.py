"""
Data loading and preprocessing module.
Handles multiple CSV files, missing value imputation, sub‑index calculation,
and feature/target extraction.
"""

import os
import glob
import pandas as pd
import numpy as np
import yaml

# Load configuration (relative to project root)
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Set random seed for reproducibility
np.random.seed(config['training']['random_state'])

# Expected feature columns (adjust if your CSV headers differ)
FEATURE_COLUMNS = [
    'PM2.5', 'PM10', 'NO', 'NO2', 'NOx', 'NH3',
    'CO', 'SO2', 'O3', 'Benzene', 'Toluene', 'Xylene'
]
TARGET_COLUMN = 'AQI'


def load_data(source=None, pattern=None):
    """
    Load data from a single CSV file or a directory containing multiple CSV files.
    If source is None, read from config.
    Automatically drops a leading unnamed index column if present.
    """
    if source is None:
        source = config['data']['source']
        pattern = config['data']['pattern']

    if os.path.isfile(source):
        df = pd.read_csv(source)
        print(f"Loaded single file: {source}, rows: {len(df)}")
    elif os.path.isdir(source):
        all_files = glob.glob(os.path.join(source, pattern))
        if not all_files:
            raise FileNotFoundError(f"No files matching {pattern} in {source}")
        df_list = []
        for file in all_files:
            df = pd.read_csv(file)
            df_list.append(df)
            print(f"Loaded {file}, rows: {len(df)}")
        df = pd.concat(df_list, ignore_index=True)
        print(f"Total combined rows: {len(df)}")
    else:
        raise FileNotFoundError(f"Source not found: {source}")

    # Drop any column that looks like an unnamed index (e.g., named "1", "2", or containing only digits)
    for col in df.columns:
        if str(col).isdigit() or (isinstance(col, str) and col.strip().isdigit()):
            df.drop(columns=[col], inplace=True)
            print(f"Dropped index column: {col}")
            break  # assume only one such column
    return df

def _calculate_subindices(df):
    """
    Calculate sub‑indices for each pollutant using CPCB breakpoints.
    These are used only to impute missing AQI values.
    """
    # PM10 Sub-Index
    def get_PM10_subindex(x):
        if x <= 50:
            return x
        elif x <= 100:
            return x
        elif x <= 250:
            return 100 + (x - 100) * 100 / 150
        elif x <= 350:
            return 200 + (x - 250)
        elif x <= 430:
            return 300 + (x - 350) * 100 / 80
        else:
            return 400 + (x - 430) * 100 / 80

    # PM2.5 Sub-Index
    def get_PM25_subindex(x):
        if x <= 30:
            return x * 50 / 30
        elif x <= 60:
            return 50 + (x - 30) * 50 / 30
        elif x <= 90:
            return 100 + (x - 60) * 100 / 30
        elif x <= 120:
            return 200 + (x - 90) * 100 / 30
        elif x <= 250:
            return 300 + (x - 120) * 100 / 130
        else:
            return 400 + (x - 250) * 100 / 130

    # SO2 Sub-Index
    def get_SO2_subindex(x):
        if x <= 40:
            return x * 50 / 40
        elif x <= 80:
            return 50 + (x - 40) * 50 / 40
        elif x <= 380:
            return 100 + (x - 80) * 100 / 300
        elif x <= 800:
            return 200 + (x - 380) * 100 / 420
        elif x <= 1600:
            return 300 + (x - 800) * 100 / 800
        else:
            return 400 + (x - 1600) * 100 / 800

    # NOx Sub-Index
    def get_NOx_subindex(x):
        if x <= 40:
            return x * 50 / 40
        elif x <= 80:
            return 50 + (x - 40) * 50 / 40
        elif x <= 180:
            return 100 + (x - 80) * 100 / 100
        elif x <= 280:
            return 200 + (x - 180) * 100 / 100
        elif x <= 400:
            return 300 + (x - 280) * 100 / 120
        else:
            return 400 + (x - 400) * 100 / 120

    # NH3 Sub-Index
    def get_NH3_subindex(x):
        if x <= 200:
            return x * 50 / 200
        elif x <= 400:
            return 50 + (x - 200) * 50 / 200
        elif x <= 800:
            return 100 + (x - 400) * 100 / 400
        elif x <= 1200:
            return 200 + (x - 800) * 100 / 400
        elif x <= 1800:
            return 300 + (x - 1200) * 100 / 600
        else:
            return 400 + (x - 1800) * 100 / 600

    # CO Sub-Index
    def get_CO_subindex(x):
        if x <= 1:
            return x * 50 / 1
        elif x <= 2:
            return 50 + (x - 1) * 50 / 1
        elif x <= 10:
            return 100 + (x - 2) * 100 / 8
        elif x <= 17:
            return 200 + (x - 10) * 100 / 7
        elif x <= 34:
            return 300 + (x - 17) * 100 / 17
        else:
            return 400 + (x - 34) * 100 / 17

    # O3 Sub-Index
    def get_O3_subindex(x):
        if x <= 50:
            return x * 50 / 50
        elif x <= 100:
            return 50 + (x - 50) * 50 / 50
        elif x <= 168:
            return 100 + (x - 100) * 100 / 68
        elif x <= 208:
            return 200 + (x - 168) * 100 / 40
        elif x <= 748:
            return 300 + (x - 208) * 100 / 539
        else:
            return 400 + (x - 400) * 100 / 539

    # Apply functions to create sub‑index columns
    df["PM10_SubIndex"] = df["PM10"].astype(int).apply(get_PM10_subindex)
    df["PM2.5_SubIndex"] = df["PM2.5"].astype(int).apply(get_PM25_subindex)
    df["SO2_SubIndex"] = df["SO2"].astype(int).apply(get_SO2_subindex)
    df["NOx_SubIndex"] = df["NOx"].astype(int).apply(get_NOx_subindex)   
    df["NH3_SubIndex"] = df["NH3"].astype(int).apply(get_NH3_subindex)
    df["CO_SubIndex"] = df["CO"].astype(int).apply(get_CO_subindex)
    df["O3_SubIndex"] = df["O3"].astype(int).apply(get_O3_subindex)

    return df


def preprocess_data(df):
    """
    Clean and prepare the DataFrame for modeling.
    """
    # Rename if present
    if 'AQI_Bucket' in df.columns:
        df.rename(columns={'AQI_Bucket': 'Air_quality'}, inplace=True)

    # Fill missing numeric values with column mean
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())

    # Calculate sub‑indices (needed for AQI imputation)
    df = _calculate_subindices(df)

    # If AQI is still missing, fill with the maximum of the sub‑indices
    if df[TARGET_COLUMN].isna().any():
        subindex_cols = [
            "PM2.5_SubIndex", "PM10_SubIndex", "SO2_SubIndex",
            "NOx_SubIndex", "NH3_SubIndex", "CO_SubIndex", "O3_SubIndex"
        ]
        df[TARGET_COLUMN] = df[TARGET_COLUMN].fillna(
            round(df[subindex_cols].max(axis=1))
        )

    # Fill Air_quality if missing (using the original notebook's mapping)
    if 'Air_quality' in df.columns and df['Air_quality'].isna().any():
        def get_air_quality(aqi):
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
        df['Air_quality'] = df['Air_quality'].fillna(df[TARGET_COLUMN].apply(get_air_quality))

    # Drop temporary sub‑index columns
    subindex_cols = [c for c in df.columns if "SubIndex" in c]
    df.drop(columns=subindex_cols, inplace=True, errors='ignore')

    # Drop columns that are not used as features or target
    cols_to_drop = ['Date', 'City', 'Month', 'Year', 'Air_quality']
    existing_cols = [c for c in cols_to_drop if c in df.columns]
    df.drop(columns=existing_cols, inplace=True, errors='ignore')

    return df


def get_features_target(df, feature_cols=None, target_col=TARGET_COLUMN):
    """
    Split DataFrame into feature matrix X and target vector y.
    """
    if feature_cols is None:
        feature_cols = FEATURE_COLUMNS
    X = df[feature_cols]
    y = df[target_col]
    return X, y