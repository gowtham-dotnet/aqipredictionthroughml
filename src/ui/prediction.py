"""Prediction panel rendering for manual AQI estimation."""

import pandas as pd
import streamlit as st

from src.model import get_aqi_quality


def render_prediction_panel(allowed_features, model, selected_city, city_df) -> None:
    """Render manual prediction UI and output metrics."""
    if "manual_predict" in allowed_features:
        st.sidebar.header("Predict AQI")
        with st.sidebar.form("prediction_form"):
            col1, col2 = st.columns(2)

            with col1:
                pm25 = st.number_input("PM2.5", value=26.0, step=0.1)
                pm10 = st.number_input("PM10", value=50.0, step=0.1)
                no = st.number_input("NO", value=1.0, step=0.1)
                no2 = st.number_input("NO2", value=18.0, step=0.1)
                nox = st.number_input("NOx", value=17.0, step=0.1)
                nh3 = st.number_input("NH3", value=23.0, step=0.1)

            with col2:
                co = st.number_input("CO", value=1.0, step=0.1)
                so2 = st.number_input("SO2", value=3.0, step=0.1)
                o3 = st.number_input("O3", value=42.0, step=0.1)
                benzene = st.number_input("Benzene", value=2.0, step=0.1)
                toluene = st.number_input("Toluene", value=6.0, step=0.1)
                xylene = st.number_input("Xylene", value=1.0, step=0.1)

            submitted = st.form_submit_button("Predict AQI", type="primary")

        if submitted:
            input_df = pd.DataFrame(
                [[pm25, pm10, no, no2, nox, nh3, co, so2, o3, benzene, toluene, xylene]],
                columns=["PM2.5", "PM10", "NO", "NO2", "NOx", "NH3", "CO", "SO2", "O3", "Benzene", "Toluene", "Xylene"],
            )

            prediction = float(model.predict(input_df)[0])
            mcol1, mcol2 = st.columns(2)
            mcol1.metric("Predicted AQI", f"{prediction:.0f}", get_aqi_quality(prediction))

            if selected_city in city_df["City"].values:
                hist_avg = city_df.loc[city_df["City"] == selected_city, "AQI"].iloc[0]
                mcol2.metric("Historical Avg", f"{hist_avg:.0f}")
    else:
        st.info("Your role does not allow manual AQI prediction.")
