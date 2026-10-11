"""Interactive map rendering helpers."""

import streamlit as st

from src.utils.json_utils import safe_json_dumps


def build_map_html(cities_json: str, selected_city, waqi_token: str, map_js: str) -> str:
    """Build HTML payload for embedded Leaflet map."""
    api_token_safe = waqi_token.replace("\\", "\\\\").replace("'", "\\'")

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8" />
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <script src="https://leaflet.github.io/Leaflet.heat/dist/leaflet-heat.js"></script>
        <style>
            body {{
                margin: 0;
                padding: 10px;
                font-family: Arial, sans-serif;
            }}
            #map {{
                height: 600px;
                width: 100%;
                border-radius: 10px;
            }}
            .leaflet-popup-content {{
                font-size: 14px;
                max-height: 280px;
                overflow-y: auto;
                line-height: 1.5;
            }}
            .leaflet-tooltip {{
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            const citiesData = {cities_json};
            const waqiToken = '{api_token_safe}';
            const selectedCityName = {safe_json_dumps(selected_city)};
        </script>
        <script>
            {map_js}
        </script>
    </body>
    </html>
    """


def render_map_section(allowed_features, cities_json: str, selected_city, map_js: str) -> None:
    """Render map section if permission allows."""
    if "map" in allowed_features:
        st.subheader("Interactive AQI Map")
        st.info(
            "India cities: Hover for historical AQI, click for historical + live WAQI | "
            "Ireland counties: Click for live WAQI | "
            "EU countries: Click for live AQI at capital city | "
            "World cities: Click for live WAQI"
        )

        html_content = build_map_html(
            cities_json=cities_json,
            selected_city=selected_city,
            waqi_token=st.session_state.get("waqi_token", ""),
            map_js=map_js,
        )
        st.components.v1.html(html_content, height=620, scrolling=True)
        st.caption("Features: India historical + live WAQI, Ireland county live WAQI, EU capital live AQI, and world city live WAQI.")
    else:
        st.info("Your role does not allow map access.")
