
from pathlib import Path
import pandas as pd
import numpy as np

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_DIR = Path("data/raw/openaq/pm25_hours")
OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "pm25_sensor_verification.csv"

LOCAL_TIMEZONE = "Asia/Jakarta"

# Candidate column names, in case the CSV schema varies slightly.
COLUMN_CANDIDATES = {
    "sensor_id": ["sensor_id"],
    "parameter": ["parameter_name", "parameter.name"],
    "value": ["value"],
    "datetime": [
        "period.datetimeFrom.utc",
        "period.datetimeFrom.local",
    ],
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def find_column(df, logical_name):
    """Find a column using case-insensitive candidate names."""

    candidates = COLUMN_CANDIDATES[logical_name]
    lookup = {col.lower(): col for col in df.columns}

    for candidate in candidates:
        if candidate.lower() in lookup:
            return lookup[candidate.lower()]

    raise ValueError(
        f"Cannot find column for '{logical_name}'. "
        f"Available columns: {df.columns.tolist()}"
    )


def normalize_parameter(value):
    """Normalize PM2.5 parameter labels."""

    if pd.isna(value):
        return ""

    return (
        str(value)
        .lower()
        .replace(".", "")
        .replace("_", "")
        .replace("-", "")
        .replace(" ", "")
    )


# ============================================================
# 1. LOAD ALL CSV FILES
# ============================================================

csv_files = sorted(INPUT_DIR.rglob("*.csv"))

if not csv_files:
    raise FileNotFoundError(
        f"No CSV files found in: {INPUT_DIR.resolve()}"
    )

print(f"Found {len(csv_files)} CSV files.")

dataframes = []

for file in csv_files:
    try:
        temp = pd.read_csv(file)

        if temp.empty:
            print(f"Skipping empty file: {file.name}")
            continue

        dataframes.append(temp)

    except Exception as error:
        print(f"Could not read {file}: {error}")

if not dataframes:
    raise ValueError("No readable CSV data found.")

df = pd.concat(dataframes, ignore_index=True)

print(f"Total raw rows loaded: {len(df):,}")


# ============================================================
# 2. IDENTIFY COLUMNS
# ============================================================

sensor_col = find_column(df, "sensor_id")
parameter_col = find_column(df, "parameter")
value_col = find_column(df, "value")
datetime_col = find_column(df, "datetime")

df = df.rename(
    columns={
        sensor_col: "sensor_id",
        parameter_col: "parameter",
        value_col: "value",
        datetime_col: "datetime",
    }
)


# ============================================================
# 3. FILTER PM2.5 AND NON-NULL VALUES
# ============================================================

df["parameter_normalized"] = df["parameter"].apply(
    normalize_parameter
)

df["value"] = pd.to_numeric(df["value"], errors="coerce")

df["datetime"] = pd.to_datetime(
    df["datetime"],
    errors="coerce",
    utc=True
)

df["sensor_id"] = df["sensor_id"].astype("string")

df = df[
    (df["parameter_normalized"] == "pm25")
    & df["value"].notna()
    & df["sensor_id"].notna()
].copy()

print(f"PM2.5 rows with non-null values: {len(df):,}")


# ============================================================
# 4. PREPARE TIMESTAMPS
# ============================================================

# Convert UTC timestamps to Jakarta local time.
df["datetime_local"] = (
    df["datetime"].dt.tz_convert(LOCAL_TIMEZONE)
)

# Calendar date in Jakarta local time.
df["date"] = df["datetime_local"].dt.date

# Keep only records with valid timestamps for time-based metrics.
valid_time_df = df[df["datetime_local"].notna()].copy()

# Sort observations chronologically.
valid_time_df = valid_time_df.sort_values(
    ["sensor_id", "datetime_local"]
)


# ============================================================
# 5. CALCULATE SENSOR-LEVEL METRICS
# ============================================================

results = []

for sensor_id, group in df.groupby("sensor_id"):

    valid_group = valid_time_df[
        valid_time_df["sensor_id"] == sensor_id
    ].copy()

    # Unique timestamps are used for reporting intervals.
    # This prevents duplicate observations from creating
    # artificial zero-hour intervals.
    unique_timestamps = (
        valid_group["datetime_local"]
        .drop_duplicates()
        .sort_values()
    )

    time_diffs = (
        unique_timestamps.diff()
        .dropna()
        .dt.total_seconds()
        / 3600
    )

    # Dates are counted in Jakarta local time.
    valid_dates = valid_group["date"].dropna()

    results.append({
        "sensor_id": sensor_id,

        # Observation counts
        "count_rows": len(group),
        "count_date": len(valid_dates),
        "count_distinct_date": valid_dates.nunique(),

        # Observation period
        "min_date": (
            valid_group["datetime_local"].min()
            if not valid_group.empty else pd.NaT
        ),
        "max_date": (
            valid_group["datetime_local"].max()
            if not valid_group.empty else pd.NaT
        ),

        # Reporting intervals, in hours
        "avg_timediff_hours": time_diffs.mean(),
        "min_timediff_hours": time_diffs.min(),
        "max_timediff_hours": time_diffs.max(),

        # Additional data-quality indicators
        "count_missing_timestamp": (
            group["datetime"].isna().sum()
        ),
        "count_unique_timestamps": unique_timestamps.nunique(),
        "count_duplicate_timestamps": (
            len(valid_group) - unique_timestamps.nunique()
        ),
    })


# ============================================================
# 6. EXPORT RESULTS
# ============================================================

summary = pd.DataFrame(results)

summary = summary.sort_values(
    "count_rows",
    ascending=False
)

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

summary.to_csv(OUTPUT_FILE, index=False)

print("\nVerification completed.")
print(f"Total sensors: {len(summary)}")
print(f"Total valid PM2.5 observations: {summary['count_rows'].sum():,}")
print(f"Output saved to: {OUTPUT_FILE.resolve()}")

print("\nSensor verification summary:")
print(summary.to_string(index=False))
