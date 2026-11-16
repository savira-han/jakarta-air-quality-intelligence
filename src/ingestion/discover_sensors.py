
import os
import requests
import pandas as pd

from dotenv import load_dotenv


# ============================================================
# 1. CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("OPENAQ_API_KEY")

BASE_URL = "https://api.openaq.org/v3"

HEADERS = {
    "X-API-Key": API_KEY
}

OUTPUT_DIR = "data/raw/openaq"
OUTPUT_FILE = f"{OUTPUT_DIR}/sensor_inventory.csv"


# ============================================================
# 2. API REQUEST
# ============================================================

def get_sensors(location_id):
    """Retrieve sensors associated with a location."""

    url = f"{BASE_URL}/locations/{location_id}/sensors"

    response = requests.get(
        url,
        headers=HEADERS,
        params={"limit": 1000},
        timeout=60
    )

    response.raise_for_status()

    return response.json().get("results", [])


# ============================================================
# 3. EXTRACT SENSOR INFORMATION
# ============================================================

def extract_sensor_records(location_id, location_name, sensors):
    """Extract relevant sensor metadata from API responses."""

    records = []

    for sensor in sensors:

        parameter = sensor.get("parameter") or {}
        coverage = sensor.get("coverage") or {}

        # Observation dates are top-level sensor fields.
        datetime_first = sensor.get("datetimeFirst") or {}
        datetime_last = sensor.get("datetimeLast") or {}

        records.append({

            "location_id": location_id,
            "location_name": location_name,

            "sensor_id": sensor.get("id"),

            "parameter_id": parameter.get("id"),
            "parameter_name": parameter.get("name"),
            "parameter_units": parameter.get("units"),

            "sensor_name": sensor.get("name"),

            "first_observation": datetime_first.get("utc"),
            "last_observation": datetime_last.get("utc"),

            "percent_complete": coverage.get("percentComplete"),
            "observed_count": coverage.get("observedCount"),
            "expected_count": coverage.get("expectedCount")

        })

    return records


# ============================================================
# 4. SENSOR DISCOVERY
# ============================================================

def discover_all_sensors(locations):
    """Retrieve sensor metadata for all discovered locations."""

    all_sensors = []

    for _, location in locations.iterrows():

        location_id = int(location["location_id"])

        location_name = location["location_name"]

        print(
            f"Discovering sensors for location "
            f"{location_id} - {location_name}"
        )

        sensors = get_sensors(location_id)

        sensor_records = extract_sensor_records(
            location_id,
            location_name,
            sensors
        )

        all_sensors.extend(sensor_records)

    return pd.DataFrame(all_sensors)


# ============================================================
# 5. SAVE SENSOR INVENTORY
# ============================================================

def save_sensor_inventory(df):
    """Save the sensor inventory as a CSV file."""

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nSensor inventory saved:")
    print(OUTPUT_FILE)


# ============================================================
# 6. PRINT DISCOVERY SUMMARY
# ============================================================

def print_summary(df):
    """Print a summary of discovered sensors."""

    print("\n" + "=" * 60)
    print("SENSOR DISCOVERY SUMMARY")
    print("=" * 60)

    print(f"Total sensor records: {len(df)}")

    if df.empty:
        print("No sensors were returned.")
        return

    print(
        f"Unique sensor IDs: "
        f"{df['sensor_id'].nunique()}"
    )

    print("\nAvailable parameters:")

    print(
        df["parameter_name"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nPM2.5 sensor records:")

    pm25 = df[
        df["parameter_name"]
        .astype("string")
        .str.casefold()
        .eq("pm25")
    ]

    print(f"Total PM2.5 records: {len(pm25)}")

    print("\nPM2.5 observation metadata:")

    if not pm25.empty:

        print(
            pm25[
                [
                    "sensor_id",
                    "location_name",
                    "first_observation",
                    "last_observation",
                    "observed_count",
                    "expected_count",
                    "percent_complete"
                ]
            ].to_string(index=False)
        )


# ============================================================
# 7. MAIN EXECUTION
# ============================================================

def main():

    if not API_KEY:
        raise ValueError(
            "OPENAQ_API_KEY not found. "
            "Check your .env configuration."
        )

    locations = pd.read_csv(
        "data/raw/openaq/location_inventory.csv"
    )

    all_sensors = discover_all_sensors(locations)

    save_sensor_inventory(all_sensors)

    print_summary(all_sensors)

    print("\nSensor discovery completed.")


if __name__ == "__main__":
    main()
