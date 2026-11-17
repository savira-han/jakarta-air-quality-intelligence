
import requests
import pandas as pd

URL = "https://archive-api.open-meteo.com/v1/archive"

PARAMS = {
    "latitude": -6.2088,
    "longitude": 106.8456,

    "start_date": "2025-01-01",
    "end_date": "2025-01-03",

    "hourly": (
        "temperature_2m,"
        "relative_humidity_2m,"
        "wind_speed_10m,"
        "wind_direction_10m,"
        "precipitation"
    ),

    "timezone": "Asia/Jakarta",
    "wind_speed_unit": "ms"
}


def main():

    response = requests.get(
        URL,
        params=PARAMS,
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    hourly = data["hourly"]

    df = pd.DataFrame(hourly)

    print("Weather API connection successful.")

    print("\nReturned location:")
    print(data["latitude"], data["longitude"])

    print("\nReturned variables:")
    print(data["hourly_units"])

    print("\nSample observations:")
    print(df.head())

    print("\nTotal observations:")
    print(len(df))


if __name__ == "__main__":
    main()
