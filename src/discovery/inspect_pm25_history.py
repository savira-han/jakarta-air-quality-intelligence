
import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


# --------------------------------------------------
# 1. Project configuration
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SENSOR_INVENTORY_PATH = (
    PROJECT_ROOT / "data" / "raw" / "openaq" / "sensor_inventory.csv"
)

OUTPUT_PATH = (
    PROJECT_ROOT / "data" / "raw" / "openaq" / "pm25_history_sample.csv"
)

API_URL = "https://api.openaq.org/v3/sensors/{sensor_id}/hours"

API_LIMIT = 1000
SAMPLE_SENSOR_COUNT = 4


# --------------------------------------------------
# 2. Load API key
# --------------------------------------------------

load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("OPENAQ_API_KEY")

if not API_KEY:
    raise ValueError(
        "OPENAQ_API_KEY was not found. "
        "Check that your .env file exists and contains the API key."
    )

HEADERS = {
    "X-API-Key": API_KEY
}


# --------------------------------------------------
# 3. Load PM2.5 sensor inventory
# --------------------------------------------------

def load_pm25_sensors():

    if not SENSOR_INVENTORY_PATH.exists():
        raise FileNotFoundError(
            f"Sensor inventory not found: {SENSOR_INVENTORY_PATH}"
        )

    sensors = pd.read_csv(SENSOR_INVENTORY_PATH)

    required_columns = {
        "sensor_id",
        "location_id",
        "parameter_name"
    }

    missing_columns = required_columns - set(sensors.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns in sensor inventory: "
            f"{missing_columns}"
        )

    pm25_sensors = sensors[
        sensors["parameter_name"]
        .astype(str)
        .str.lower()
        .isin(["pm25", "pm2.5"])
    ].copy()

    pm25_sensors = pm25_sensors.drop_duplicates(
        subset=["sensor_id"]
    )

    if pm25_sensors.empty:
        raise ValueError("No PM2.5 sensors found in the inventory.")

    return pm25_sensors.head(SAMPLE_SENSOR_COUNT)


# --------------------------------------------------
# 4. Retrieve hourly observations
# --------------------------------------------------

def get_hourly_observations(sensor_id):

    url = API_URL.format(sensor_id=sensor_id)

    params = {
        "limit": API_LIMIT,
        "page": 1
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    return response.json().get("results", [])


# --------------------------------------------------
# 5. Collect observations from sample sensors
# --------------------------------------------------

def collect_pm25_history(sensors):

    all_observations = []

    for _, sensor in sensors.iterrows():

        sensor_id = sensor["sensor_id"]
        location_id = sensor["location_id"]

        print(f"Retrieving observations for sensor {sensor_id}...")

        observations = get_hourly_observations(sensor_id)

        print(f"Retrieved {len(observations):,} observations.")

        if not observations:
            continue

        sensor_data = pd.json_normalize(
            observations,
            sep="_"
        )

        sensor_data.insert(0, "location_id", location_id)
        sensor_data.insert(0, "sensor_id", sensor_id)

        all_observations.append(sensor_data)

    if not all_observations:
        return pd.DataFrame()

    return pd.concat(
        all_observations,
        ignore_index=True
    )


# --------------------------------------------------
# 6. Save CSV and display terminal preview
# --------------------------------------------------

def main():

    print("\nLoading PM2.5 sensor inventory...")

    pm25_sensors = load_pm25_sensors()

    print(
        f"Selected {len(pm25_sensors)} PM2.5 sensors "
        "for sample inspection.\n"
    )

    observations = collect_pm25_history(pm25_sensors)

    if observations.empty:
        print("\nNo hourly observations were returned.")
        return

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    observations.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\n----------------------------------------")
    print("PM2.5 HISTORY INSPECTION")
    print("----------------------------------------")

    print(f"Total observations retrieved: {len(observations):,}")
    print(f"Number of sensors inspected: {observations['sensor_id'].nunique()}")
    print(f"CSV output: {OUTPUT_PATH}")

    print("\nFirst 10 rows:")

    print(
        observations.head(10).to_string(index=False)
    )

    print("\nInspection completed.")


if __name__ == "__main__":
    main()
