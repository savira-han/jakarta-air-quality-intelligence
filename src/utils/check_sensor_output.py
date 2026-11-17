import pandas as pd

df = pd.read_csv(
    "data/raw/openaq/sensor_inventory.csv"
)

print(df.groupby("parameter_name").size())

print(
    df[df["parameter_name"].str.lower() == "pm25"][
        [
            "location_id",
            "location_name",
            "sensor_id",
            "first_observation",
            "last_observation",
            "percent_complete"
        ]
    ]
)