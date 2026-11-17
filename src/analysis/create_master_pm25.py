"""
Combine all the OpenAQ hourly PM2.5 files into one CSV.

Input folder looks like this:
    data/raw/openaq/pm25_hours/sensor_7748548/2026-01.csv
    data/raw/openaq/pm25_hours/sensor_7748548/2026-02.csv
    data/raw/openaq/pm25_hours/sensor_1234567/2026-01.csv
    ...

Output:
    data/processed/master_pm25_hourly.csv
"""

from pathlib import Path

import pandas as pd

INPUT_DIR = Path("data/raw/openaq/pm25_hours")
OUTPUT_DIR = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "master_pm25_hourly.csv"


def read_all_files():
    """Read every sensor_*/YYYY-MM.csv file and return a list of dataframes."""
    files = sorted(INPUT_DIR.glob("sensor_*/*.csv"))
    print("Found", len(files), "files")

    all_data = []
    for file in files:
        df = pd.read_csv(file)

        # some months may have no data, skip them
        if df.empty:
            print("  empty file, skipped:", file)
            continue

        all_data.append(df)

    return all_data


def main():
    if not INPUT_DIR.exists():
        print("Input folder not found:", INPUT_DIR)
        return

    all_data = read_all_files()
    if len(all_data) == 0:
        print("No data to combine.")
        return

    # put everything in one table
    master = pd.concat(all_data, ignore_index=True)

    # sort by sensor and time
    master = master.sort_values(["sensor_id", "period.datetimeFrom.utc"])

    # remove duplicated hours (same sensor and same hour), keep the last one
    rows_before = len(master)
    master = master.drop_duplicates(
        subset=["sensor_id", "period.datetimeFrom.utc"], keep="last"
    )
    print("Removed", rows_before - len(master), "duplicate rows")

    # save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    master.to_csv(OUTPUT_FILE, index=False)

    # quick summary
    print()
    print("Saved:", OUTPUT_FILE)
    print("Rows:", len(master))
    print("Sensors:", master["sensor_id"].nunique())
    print("From:", master["period.datetimeFrom.utc"].min())
    print("To:  ", master["period.datetimeFrom.utc"].max())


if __name__ == "__main__":
    main()