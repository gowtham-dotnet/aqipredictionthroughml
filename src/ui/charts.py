"""Chart rendering helpers for AQI trends and comparisons."""

import os

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.model import get_aqi_quality


def render_city_historical_chart(allowed_features, daily_df, all_cities_list):
    """Render city-wise historical AQI chart section."""
    selected_city = all_cities_list[0] if all_cities_list else None

    if "charts" in allowed_features:
        st.subheader("City-wise Historical AQI")
        selected_city = st.selectbox("Select city", options=all_cities_list)

        if selected_city:
            st.subheader(f"{selected_city} Historical AQI")
            city_history = daily_df[daily_df["City"] == selected_city].sort_values("Date")

            if not city_history.empty:
                fig = px.line(city_history, x="Date", y="AQI", title="Daily AQI Trend")
                for lvl, color in zip([50, 100, 200, 300, 400], ["green", "yellow", "orange", "red", "purple"]):
                    fig.add_hline(y=lvl, line_dash="dot", line_color=color)
                st.plotly_chart(fig, use_container_width=True)

    return selected_city


def render_state_comparison_section(allowed_features, daily_state_df) -> None:
    """Render two-state AQI and pollutant comparison charts."""
    if "charts" in allowed_features:
        st.subheader("Compare Two Indian States")

        if "State" in daily_state_df.columns and daily_state_df["State"].notna().any():
            state_options = sorted(daily_state_df["State"].dropna().unique())

            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                state_1 = st.selectbox("Select State 1", state_options, key="state_1")
            with c2:
                default_index = 1 if len(state_options) > 1 else 0
                state_2 = st.selectbox("Select State 2", state_options, index=default_index, key="state_2")
            with c3:
                chart_type = st.selectbox("Chart Type", ["Bar", "Pie", "Radar"], index=0, key="chart_type")

            compare_df = (
                daily_state_df[daily_state_df["State"].isin([state_1, state_2])]
                .groupby("State", as_index=False)["AQI"]
                .mean()
            )

            if not compare_df.empty:
                m1, m2 = st.columns(2)

                state_1_row = compare_df[compare_df["State"] == state_1]
                if not state_1_row.empty:
                    state_1_aqi = state_1_row["AQI"].iloc[0]
                    m1.metric(
                        f"{state_1} Avg AQI",
                        f"{state_1_aqi:.0f}",
                        get_aqi_quality(state_1_aqi),
                    )
                else:
                    m1.metric(f"{state_1} Avg AQI", "N/A")

                state_2_row = compare_df[compare_df["State"] == state_2]
                if not state_2_row.empty:
                    state_2_aqi = state_2_row["AQI"].iloc[0]
                    m2.metric(
                        f"{state_2} Avg AQI",
                        f"{state_2_aqi:.0f}",
                        get_aqi_quality(state_2_aqi),
                    )
                else:
                    m2.metric(f"{state_2} Avg AQI", "N/A")

                if chart_type == "Bar":
                    fig_compare = px.bar(
                        compare_df,
                        x="State",
                        y="AQI",
                        color="State",
                        title="Average AQI Comparison Between Two Indian States",
                        text_auto=".1f",
                    )
                    fig_compare.update_layout(showlegend=False)
                    st.plotly_chart(fig_compare, use_container_width=True)
                elif chart_type == "Pie":
                    fig_compare = px.pie(
                        compare_df,
                        names="State",
                        values="AQI",
                        title="AQI Share Between Two Selected Indian States",
                        hole=0.35,
                    )
                    st.plotly_chart(fig_compare, use_container_width=True)
                else:
                    pollutant_candidates = ["PM2.5", "PM10", "NO2", "SO2", "O3", "CO"]
                    available_pollutants = [col for col in pollutant_candidates if col in daily_state_df.columns]

                    if len(available_pollutants) < 3:
                        st.warning("Radar chart needs at least 3 pollutant columns (from PM2.5, PM10, NO2, SO2, O3, CO).")
                    else:
                        pollutant_summary = (
                            daily_state_df[daily_state_df["State"].isin([state_1, state_2])]
                            .groupby("State", as_index=False)[available_pollutants]
                            .mean()
                        )

                        radar_df = pollutant_summary.set_index("State")
                        if state_1 in radar_df.index and state_2 in radar_df.index:
                            theta = available_pollutants + [available_pollutants[0]]
                            values_1 = radar_df.loc[state_1, available_pollutants].tolist()
                            values_2 = radar_df.loc[state_2, available_pollutants].tolist()
                            values_1 += [values_1[0]]
                            values_2 += [values_2[0]]

                            fig_compare = go.Figure()
                            fig_compare.add_trace(
                                go.Scatterpolar(
                                    r=values_1,
                                    theta=theta,
                                    fill="toself",
                                    name=state_1,
                                )
                            )
                            fig_compare.add_trace(
                                go.Scatterpolar(
                                    r=values_2,
                                    theta=theta,
                                    fill="toself",
                                    name=state_2,
                                )
                            )
                            fig_compare.update_layout(
                                title="Pollutant Profile Comparison (Radar)",
                                polar=dict(radialaxis=dict(visible=True)),
                                showlegend=True,
                            )
                            st.plotly_chart(fig_compare, use_container_width=True)
                        else:
                            st.info("Not enough data available to render radar chart for selected states.")

                pollutant_candidates = ["PM2.5", "PM10", "NO2", "SO2", "O3", "CO"]
                available_pollutants = [col for col in pollutant_candidates if col in daily_state_df.columns]

                if available_pollutants:
                    st.markdown("### Pollutant Comparison")
                    pollutant_summary = (
                        daily_state_df[daily_state_df["State"].isin([state_1, state_2])]
                        .groupby("State", as_index=False)[available_pollutants]
                        .mean()
                    )
                    pollutant_long = pollutant_summary.melt(
                        id_vars="State",
                        value_vars=available_pollutants,
                        var_name="Pollutant",
                        value_name="Value",
                    )

                    fig_pollutants = px.bar(
                        pollutant_long,
                        x="Pollutant",
                        y="Value",
                        color="State",
                        barmode="group",
                        title="Average Pollutant Levels by State",
                    )
                    st.plotly_chart(fig_pollutants, use_container_width=True)
        else:
            st.warning("State comparison is unavailable because no State column was found in the dataset.")

        if os.path.exists("plots/pca.png"):
            with st.expander("ML Model Analysis"):
                st.image("plots/pca.png", caption="PCA of pollutant features")
    else:
        st.info("Your role does not allow analytics charts.")
