"""Data and model loading services with Streamlit caching.

This module contains all file/model loading functions used by the Streamlit
dashboard.

Model loading supports two environments:

1. Local development:
   If ``random_forest_model.pkl`` exists in the project directory, it is
   loaded directly. This preserves the existing local development workflow.

2. Hugging Face deployment:
   If the local model file is not available, the trained model is downloaded
   automatically from the public Hugging Face model repository.

This approach allows the same application code to work both locally and
inside the Hugging Face Docker Space.
"""

import os
import pickle
import numpy as np
import pandas as pd
import streamlit as st

try:
    from huggingface_hub import hf_hub_download
except ImportError:
    hf_hub_download = None


# ---------------------------------------------------------------------------
# MODEL CONFIGURATION
# ---------------------------------------------------------------------------

# Public Hugging Face repository containing the trained Random Forest model.
# The repository is public, so no Hugging Face authentication token is needed.
HF_MODEL_REPO = "ReddyWanga/aqi-random-forest"

# Name of the trained model file.
MODEL_FILENAME = "random_forest_model.pkl"


# ---------------------------------------------------------------------------
# MODEL LOADING
# ---------------------------------------------------------------------------

@st.cache_resource
def load_model():
    """Load the trained Random Forest model.

    The function first checks whether the model exists locally. This is useful
    during development because the existing local project already contains
    ``random_forest_model.pkl``.

    If the local model is not found, the function automatically downloads the
    model from the public Hugging Face repository.

    ``st.cache_resource`` ensures that the large model is loaded only once
    during the Streamlit application's lifetime rather than being loaded
    repeatedly on every Streamlit rerun.

    Returns:
        The deserialized trained machine-learning model.

    Raises:
        Streamlit stop:
            If the model cannot be found or loaded from either location.
    """

    # -----------------------------------------------------------------------
    # OPTION 1: LOAD THE MODEL FROM THE LOCAL PROJECT
    # -----------------------------------------------------------------------
    #
    # This keeps the current local development workflow working exactly as
    # before. If the 4.5 GB model exists in the project directory, we use it
    # directly and do not download anything from Hugging Face.
    #
    local_model_path = MODEL_FILENAME

    if os.path.exists(local_model_path):
        try:
            st.info("Loading the trained model from the local project...")

            with open(local_model_path, "rb") as file:
                model = pickle.load(file)

            st.success("Local model loaded successfully.")
            return model

        except Exception as exc:
            st.error(f"Failed to load the local model: {exc}")
            st.stop()

    # -----------------------------------------------------------------------
    # OPTION 2: DOWNLOAD THE MODEL FROM HUGGING FACE
    # -----------------------------------------------------------------------
    #
    # If the local model does not exist, we assume the application is running
    # in the Hugging Face Space.
    #
    if hf_hub_download is None:
        st.error(
            "The local model file is unavailable and the optional "
            "huggingface_hub package is not installed."
        )
        st.code("python -m pip install huggingface_hub")
        st.stop()

    # The model is downloaded using huggingface_hub. Hugging Face stores the
    # downloaded file in its local cache, so it does not need to be manually
    # downloaded every time the application code runs.
    #
    try:
        st.info("Local model not found. Downloading the trained model from Hugging Face...")
        st.caption(
            "The model is approximately 4.5 GB, so the first download may take "
            "some time."
        )

        model_path = hf_hub_download(
            repo_id=HF_MODEL_REPO,
            filename=MODEL_FILENAME,
        )

        # Load the downloaded model using Python's pickle module.
        with open(model_path, "rb") as file:
            model = pickle.load(file)

        st.success("Model downloaded from Hugging Face and loaded successfully.")
        return model

    except Exception as exc:
        st.error(
            "Failed to download or load the model from Hugging Face. "
            f"Error: {exc}"
        )
        st.stop()


# ---------------------------------------------------------------------------
# DAILY AIR QUALITY DATA
# ---------------------------------------------------------------------------

@st.cache_data
def load_daily_data() -> pd.DataFrame:
    """Load and clean the daily city AQI dataset.

    Returns:
        A pandas DataFrame containing the cleaned daily AQI data.
    """

    data_path = "my_air_data/city_day.csv"

    if not os.path.exists(data_path):
        st.error(f"Missing data file: {data_path}")
        st.stop()

    df = pd.read_csv(data_path, parse_dates=["Date"])

    # Ensure AQI values are numeric.
    df["AQI"] = pd.to_numeric(df["AQI"], errors="coerce")

    # Remove rows where AQI could not be converted to a valid number.
    df = df.dropna(subset=["AQI"])

    return df


# ---------------------------------------------------------------------------
# STATE DATA
# ---------------------------------------------------------------------------

@st.cache_data
def load_state_data(daily_df: pd.DataFrame) -> pd.DataFrame:
    """Ensure that a State column exists in the daily AQI dataset.

    If the State column is already present, the existing DataFrame is returned.

    Otherwise, the function attempts to obtain City/State mappings from the
    stations metadata file and merges them into the daily dataset.

    Args:
        daily_df: Daily AQI DataFrame.

    Returns:
        DataFrame containing State information where available.
    """

    # If State already exists, no additional processing is necessary.
    if "State" in daily_df.columns:
        return daily_df.copy()

    stations_file = "my_air_data/stations.csv"

    if os.path.exists(stations_file):
        stations_df = pd.read_csv(stations_file)

        if {"City", "State"}.issubset(stations_df.columns):
            city_state = (
                stations_df[["City", "State"]]
                .dropna()
                .drop_duplicates()
            )

            merged = daily_df.merge(
                city_state,
                on="City",
                how="left",
            )

            return merged

    # If station metadata is unavailable, return the original data.
    return daily_df.copy()


# ---------------------------------------------------------------------------
# CITY COORDINATES
# ---------------------------------------------------------------------------

@st.cache_data
def load_city_coords() -> pd.DataFrame:
    """Load Indian city coordinate data.

    Returns:
        DataFrame containing City, Latitude and Longitude columns.
    """

    coord_file = "city_coords.csv"

    if not os.path.exists(coord_file):
        st.error(
            "Missing city_coords.csv. "
            "Run generate_coords.py first."
        )
        st.stop()

    df = pd.read_csv(coord_file)

    required_cols = {
        "City",
        "Latitude",
        "Longitude",
    }

    if not required_cols.issubset(df.columns):
        st.error(
            f"{coord_file} must contain columns: {required_cols}"
        )
        st.stop()

    return df


# ---------------------------------------------------------------------------
# EU COUNTRY / CITY COORDINATES
# ---------------------------------------------------------------------------

@st.cache_data
def load_eu_countries() -> pd.DataFrame:
    """Load EU country and capital-city coordinate data.

    Returns:
        DataFrame containing EU country/city mapping and coordinates.
    """

    eu_file = "eu_countries.csv"

    if not os.path.exists(eu_file):
        st.error(
            "Missing eu_countries.csv. "
            "Please create it first."
        )
        st.stop()

    df = pd.read_csv(eu_file)

    required_cols = {
        "Country",
        "City",
        "Latitude",
        "Longitude",
        "type",
    }

    if not required_cols.issubset(df.columns):
        st.error(
            f"{eu_file} must contain columns: {required_cols}"
        )
        st.stop()

    # AQI is initially unavailable for these locations and will be populated
    # later by the relevant dashboard functionality.
    df["AQI"] = np.nan

    return df


# ---------------------------------------------------------------------------
# IRELAND COUNTY COORDINATES
# ---------------------------------------------------------------------------

@st.cache_data
def load_ireland_coords() -> pd.DataFrame:
    """Load Ireland county coordinate data used by the map.

    Returns:
        DataFrame containing county/city coordinates and map metadata.
    """

    ire_file = "ireland_counties.csv"

    if not os.path.exists(ire_file):
        st.error(
            "Missing ireland_counties.csv. "
            "Run generate_ireland_coords.py first."
        )
        st.stop()

    df = pd.read_csv(ire_file)

    # The map expects the geographic location to be represented by "City".
    if "County" in df.columns:
        df = df.rename(columns={"County": "City"})

    required_cols = {
        "City",
        "Latitude",
        "Longitude",
    }

    if not required_cols.issubset(df.columns):
        st.error(
            f"{ire_file} must contain columns: {required_cols}"
        )
        st.stop()

    # AQI values will be populated later using live data.
    df["AQI"] = np.nan

    # Identify these locations as Ireland locations for map processing.
    df["type"] = "ireland"

    return df


# ---------------------------------------------------------------------------
# MAP JAVASCRIPT
# ---------------------------------------------------------------------------

@st.cache_data
def load_map_js() -> str:
    """Load the embedded map JavaScript from map.js.

    Returns:
        Contents of map.js as a string.
    """

    try:
        with open(
            "map.js",
            "r",
            encoding="utf-8",
        ) as file:
            return file.read()

    except FileNotFoundError:
        st.error("Missing map.js file.")
        st.stop()

    except UnicodeDecodeError:
        # Fallback for files containing unexpected/non-UTF-8 characters.
        with open(
            "map.js",
            "r",
            encoding="utf-8",
            errors="ignore",
        ) as file:
            return file.read()
