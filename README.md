---
title: AQI Prediction Dashboard
emoji: 🌍
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
python_version: "3.11"
pinned: false
---

# AQI Estimation and Monitoring Platform

A Streamlit application for estimating Air Quality Index (AQI) from pollutant measurements, exploring historical Indian AQI data, and viewing live AQI data on an interactive map.

The project combines a machine-learning training pipeline with a role-based dashboard. Historical data is used for prediction and analytics; live map values are requested from the World Air Quality Index (WAQI) API when a user supplies a valid WAQI token.

## Features

- **AQI prediction:** Estimates AQI from 12 pollutant measurements using a trained Random Forest model.

- **Model training and evaluation:** Trains linear regression, polynomial regression, decision-tree, and Random Forest regressors; evaluates them with RMSE, MAE, and R².

- **MLflow tracking:** Logs the final Random Forest parameters, held-out test metrics, and model artefact locally.

- **Historical analytics:** Displays daily AQI trends for Indian cities and compares two Indian states using bar, pie, radar, and pollutant charts.

- **Interactive map:** Shows historical Indian city AQI alongside on-demand live AQI for Indian, Irish, EU-capital, and selected world locations.

- **Role-based access:** Basic users can predict AQI; analysts can also access charts; administrators can access the map.

- **Cached loading:** Streamlit caches the trained model and reusable data resources to improve responsiveness.

## Technology Stack

- Python and Streamlit
- pandas and NumPy
- scikit-learn
- Plotly and Leaflet
- MLflow
- WAQI API

## Architecture Overview

The application has two connected workflows.

### Training Workflow

```text
my_air_data CSV files
        ↓
data_loader.py
(load and preprocess)
        ↓
train.py
(train, evaluate, grid search, clustering)
        ↓
MLflow metrics and plots/
        ↓
random_forest_model.pkl
```

### Dashboard Workflow

```text
Browser
    ↓
app.py
    ↓
auth.py
(login and role permissions)
    ↓
services/loaders.py
and city_data_service.py
(cached resources)
    ↓
UI modules
(prediction, charts, map, sidebar, styles)
    ↓
Leaflet map
and optional live WAQI requests
```

The dashboard does not retrain the model. It loads the previously saved `random_forest_model.pkl` file and uses it for manual AQI estimation.

## Project Structure

```text
.
├── app.py                       # Streamlit dashboard entry point
├── main.py                      # Model-training entry point
├── config.yaml                  # Training, MLflow, clustering, and output settings
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container image definition
├── .dockerignore                # Docker build-context exclusions
├── .gitlab-ci.yml               # GitLab CI template
├── map.js                       # Leaflet and WAQI map behaviour
├── random_forest_model.pkl      # Trained model used by the dashboard
├── users.json                   # Demo user accounts and roles
├── city_coords.csv              # Indian city coordinates
├── eu_countries.csv             # EU capital coordinates
├── ireland_counties.csv         # Irish county coordinates
├── my_air_data/
│   ├── city_day.csv             # Historical city-level AQI data
│   ├── city_hour.csv
│   ├── station_day.csv
│   ├── station_hour.csv
│   └── stations.csv             # Station metadata, including state information
└── src/
    ├── auth.py                  # Login and feature permissions
    ├── data_loader.py           # Training-data loading and preprocessing
    ├── model.py                 # Model factories, metrics, and AQI categories
    ├── train.py                 # Training pipeline and MLflow logging
    ├── services/                # Cached dashboard data-loading services
    ├── ui/                      # Dashboard sections and styling
    └── utils/                   # AQI colour and JSON helpers
```

## Prerequisites

- Python 3.11 is recommended, matching the supplied Docker image.
- `pip` for installing dependencies.
- A WAQI token is required only for live map readings.

A WAQI token can be obtained from the [WAQI Data Platform](https://aqicn.org/data-platform/token/).

## Installation

From the project root, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Ensure that the following files and directories are present before starting the dashboard:

- `random_forest_model.pkl`
- `city_coords.csv`
- `eu_countries.csv`
- `ireland_counties.csv`
- Required CSV files inside `my_air_data/`

## Run the Dashboard

Start the Streamlit application with:

```powershell
streamlit run app.py
```

Open the local URL shown by Streamlit in your browser.

The sidebar provides:

- Logout functionality
- AQI-category guidance
- An optional WAQI-token field

Live map readings remain unavailable until a valid WAQI token is supplied.

## User Roles

| Role | Available functionality |
|------|--------------------------|
| **Basic** | Manual AQI prediction |
| **Analyst** | Manual AQI prediction and historical charts/state comparison |
| **Admin** | Manual AQI prediction, historical charts/state comparison, and interactive map |

The repository currently contains demonstration accounts in `users.json`.

These credentials and the JSON-based SHA-256 authentication mechanism are intended for local demonstration only and must be replaced with a production authentication solution before public deployment.

## Train a Model

The training pipeline reads the source configured in `config.yaml`, preprocesses the data, trains and evaluates several regression models, performs the configured Random Forest grid search, and saves the selected Random Forest model to:

```text
random_forest_model.pkl
```

Run the training pipeline with:

```powershell
python main.py
```

The pipeline also:

1. Uses the `test_size` value in `config.yaml`. The current value is `0.25`, which creates a 75:25 training/test split.

2. Reports RMSE, MAE, and R² for candidate models.

3. Optionally performs K-Means clustering and PCA when enabled in `config.yaml`.

4. Saves clustering/PCA plots to `plots/` when enabled.

5. Logs final Random Forest parameters and metrics to the local MLflow store configured in `config.yaml`.

> Training and hold-out metrics evaluate the predictive model. They are not a substitute for an automated software test suite.

## Run with Docker

Build the image from the project root:

```powershell
docker build -t aqi-platform .
```

The current `.dockerignore` deliberately excludes `random_forest_model.pkl`.

When running the container locally, mount the locally trained model:

```powershell
docker run --rm -p 7860:7860 -v "${PWD}\random_forest_model.pkl:/app/random_forest_model.pkl" aqi-platform
```

Then open:

```text
http://localhost:7860
```

For a hosted deployment, the trusted trained-model artifact should be made available through a secure volume or approved artifact store.

Do not permit users to upload arbitrary pickle files.

## CI/CD and Testing Status

The repository includes a `.gitlab-ci.yml` file, but it is currently GitLab's starter template. It prints demonstration build, test, lint, and deployment messages rather than running the project, automated tests, a linter, or a real deployment.

It must not be interpreted as evidence of a working CI/CD pipeline.

No automated unit, integration, or end-to-end test suite is currently included.

The training pipeline's 75:25 hold-out split and its RMSE, MAE, and R² outputs evaluate predictive-model performance only; they do not test dashboard functionality.

Functional validation has therefore been performed manually.

## Data and Live AQI Notes

- Historical Indian charts and city averages are based on the local `city_day.csv` dataset; they do not update automatically.

- The map uses Leaflet and OpenStreetMap tiles in the browser.

- WAQI requests are made on demand after a marker is clicked and are cached in the browser for five minutes by `map.js`.

- In the present implementation, a WAQI token is sent to the browser for map requests. A shared production token should instead be kept server-side behind a rate-limited, cached proxy.

## Current Limitations and Future Work

- No automated unit, integration, or end-to-end test suite is currently included. A future version should add `pytest` tests and GitLab CI execution.

- The existing GitLab CI file is a placeholder and should be replaced with real install, test, lint, image-build, and deployment jobs.

- The current login approach uses local demo users and is not suitable for a public deployment.

- Live AQI availability depends on the WAQI API and the availability of a nearby monitoring station.

- `mlflow.db` is suitable for local experiment tracking, not for multi-user production storage.

- Package versions are not pinned in `requirements.txt`; a locked dependency set should be created before a reproducible deployment.

- Public deployment should use managed authentication, secure secret storage, server-side WAQI requests, and a persistent data store where required.

## License

No licence has been specified for this project.

Add an appropriate licence before distributing or reusing the code publicly.