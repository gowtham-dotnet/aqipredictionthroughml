"""City data preparation services for AQI app."""

import numpy as np
import pandas as pd
import streamlit as st

from src.utils.aqi_utils import color_from_aqi
from src.utils.json_utils import safe_json_dumps


def build_city_average_dataframe(daily_df: pd.DataFrame) -> pd.DataFrame:
    """Build city-level average dataframe and normalize pollutant column names."""
    pollutant_cols = [
        "AQI", "PM2.5", "PM10", "NO2", "NO", "NOx",
        "NH3", "CO", "SO2", "O3", "Benzene", "Toluene", "Xylene",
    ]
    available_cols = [col for col in pollutant_cols if col in daily_df.columns]

    city_avg = daily_df.groupby("City", as_index=False)[available_cols].mean()
    rename_map = {
        "PM2.5": "pm25",
        "PM10": "pm10",
        "NO2": "no2",
        "SO2": "so2",
        "O3": "o3",
        "CO": "co",
        "NO": "no",
        "NOx": "nox",
        "NH3": "nh3",
        "Benzene": "benzene",
        "Toluene": "toluene",
        "Xylene": "xylene",
    }

    city_avg = city_avg.rename(columns=rename_map)
    city_avg["AQI"] = pd.to_numeric(city_avg["AQI"], errors="coerce")
    return city_avg


def build_indian_cities(city_avg: pd.DataFrame, coord_df: pd.DataFrame) -> pd.DataFrame:
    """Merge city averages with coordinates and enrich display fields."""
    city_df = pd.merge(city_avg, coord_df, on="City", how="inner")
    city_df = city_df.dropna(subset=["Latitude", "Longitude", "AQI"])
    city_df["color"] = city_df["AQI"].apply(color_from_aqi)

    indian_cities = city_df.copy()
    indian_cities["type"] = "india"
    return indian_cities


def build_world_cities() -> pd.DataFrame:
    """Create fixed global city seed dataset for live AQI click behavior."""
    return pd.DataFrame(
        {
            "City": [
                "London", "New York", "Tokyo", "Paris", "Sydney", "Singapore",
                "Dubai", "Toronto", "Los Angeles", "Berlin", "Moscow", "Cairo",
            ],
            "Latitude": [
                51.5074, 40.7128, 35.6895, 48.8566, -33.8688, 1.3521,
                25.2048, 43.6532, 34.0522, 52.5200, 55.7558, 30.0444,
            ],
            "Longitude": [
                -0.1278, -74.0060, 139.6917, 2.3522, 151.2093, 103.8198,
                55.2708, -79.3832, -118.2437, 13.4050, 37.6173, 31.2357,
            ],
            "AQI": [np.nan] * 12,
            "type": ["world"] * 12,
        }
    )


def build_all_cities(indian_cities: pd.DataFrame, ireland_df: pd.DataFrame, eu_df: pd.DataFrame) -> pd.DataFrame:
    """Concatenate all map city datasets into one dataframe."""
    world_cities = build_world_cities()
    return pd.concat([indian_cities, world_cities, ireland_df, eu_df], ignore_index=True)


def build_cities_json(all_cities: pd.DataFrame) -> str:
    """Convert map city dataframe into safe JSON payload for embedded JS."""
    export_cols = [
        "Country", "City", "Latitude", "Longitude", "AQI", "type",
        "pm25", "pm10", "no2", "so2", "o3", "co",
        "no", "nox", "nh3", "benzene", "toluene", "xylene",
    ]
    available_export_cols = [col for col in export_cols if col in all_cities.columns]

    records = (
        all_cities[available_export_cols]
        .where(all_cities[available_export_cols].notna(), other=None)
        .to_dict(orient="records")
    )
    return safe_json_dumps(records)


@st.cache_data
def build_city_average_dataframe_cached(daily_df: pd.DataFrame) -> pd.DataFrame:
    """Cached wrapper for city-level average dataframe creation."""
    return build_city_average_dataframe(daily_df)


@st.cache_data
def build_all_cities_cached(city_df: pd.DataFrame, ireland_df: pd.DataFrame, eu_df: pd.DataFrame) -> pd.DataFrame:
    """Cached wrapper for concatenated map city dataset."""
    return build_all_cities(city_df, ireland_df, eu_df)


@st.cache_data
def build_cities_json_cached(all_cities: pd.DataFrame) -> str:
    """Cached wrapper for map JSON payload creation."""
    return build_cities_json(all_cities)
