
import os
import requests
import pandas as pd

from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAQ_API_KEY")

BASE_URL = "https://api.openaq.org/v3"

HEADERS = {
    "X-API-Key": API_KEY
}

PARAMS = {
    "bbox": "106.4,-6.4,107.1,-5.9",
    "iso": "ID",
    "limit": 1000
}


def get_locations():

    all_locations = []
    page = 1

    while True:

        params = {
            **PARAMS,
            "page": page
        }

        response = requests.get(
            f"{BASE_URL}/locations",
            headers=HEADERS,
            params=params,
            timeout=60
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results", [])

        if not results:
            break

        all_locations.extend(results)

        print(f"Retrieved page {page}: {len(results)} locations")

        meta = data.get("meta", {})
        found = meta.get("found")

        if found is not None and len(all_locations) >= found:
            break

        if len(results) < PARAMS["limit"]:
            break

        page += 1

    return all_locations


def main():

    locations = get_locations()

    if not locations:
        print("No monitoring locations found.")
        return

    records = []

    for location in locations:

        coordinates = location.get("coordinates") or {}

        records.append({
            "location_id": location.get("id"),
            "location_name": location.get("name"),
            "locality": location.get("locality"),
            "latitude": coordinates.get("latitude"),
            "longitude": coordinates.get("longitude"),
            "timezone": location.get("timezone"),
            "provider": (location.get("provider") or {}).get("name"),
            "owner": (location.get("owner") or {}).get("name"),
            "is_mobile": location.get("isMobile"),
            "is_monitor": location.get("isMonitor")
        })

    df = pd.DataFrame(records)

    os.makedirs("data/raw/openaq", exist_ok=True)

    df.to_csv(
        "data/raw/openaq/location_inventory.csv",
        index=False
    )

    print("\nLocation discovery completed.")
    print(f"Total locations: {len(df)}")
    print(df.head())


if __name__ == "__main__":
    main()
