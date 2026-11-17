
from pathlib import Path

import pandas as pd


# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data" / "raw"
OPENAQ_DIR = DATA_DIR / "openaq"
WEATHER_DIR = DATA_DIR / "open_meteo"

REPORT_PATH = (
    PROJECT_ROOT / "docs" / "DATA_DISCOVERY.md"
)

LOCATION_FILE = OPENAQ_DIR / "location_inventory.csv"
SENSOR_FILE = OPENAQ_DIR / "sensor_inventory.csv"
PM25_FILE = OPENAQ_DIR / "pm25_history_sample.csv"


# ==================================================
# 2. GENERAL HELPER FUNCTIONS
# ==================================================

def read_csv(path):
    """Read a CSV file if it exists."""

    if not path.exists():
        return None

    return pd.read_csv(path)


def find_column(df, candidates):
    """
    Find a column using case-insensitive matching.
    Spaces, underscores and dots are ignored.
    """

    if df is None:
        return None

    normalized_columns = {
        str(col).lower().replace("_", "").replace(".", "").replace(" ", ""): col
        for col in df.columns
    }

    for candidate in candidates:
        normalized = (
            candidate.lower()
            .replace("_", "")
            .replace(".", "")
            .replace(" ", "")
        )

        if normalized in normalized_columns:
            return normalized_columns[normalized]

    return None


def format_number(value):
    """Format numbers for readable report output."""

    if pd.isna(value):
        return "Not available"

    return f"{int(value):,}"


def format_percentage(value):
    if pd.isna(value):
        return "Not available"

    return f"{value:.2f}%"


def markdown_table(headers, rows):
    """Create a Markdown table without requiring tabulate."""

    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |"
    ]

    for row in rows:
        values = [
            str(value).replace("|", "\\|").replace("\n", " ")
            for value in row
        ]

        lines.append("| " + " | ".join(values) + " |")

    return "\n".join(lines)


def basic_file_summary(name, df):
    """Summarize the structure and quality of a CSV."""

    if df is None:
        return [
            f"### {name}",
            "",
            "The CSV file was not found during report generation.",
            ""
        ]

    row_count = len(df)
    column_count = len(df.columns)
    duplicate_count = int(df.duplicated().sum())

    missing_cells = int(df.isna().sum().sum())
    total_cells = row_count * column_count

    missing_pct = (
        missing_cells / total_cells * 100
        if total_cells > 0 else 0
    )

    lines = [
        f"### {name}",
        "",
        f"- Rows: {format_number(row_count)}",
        f"- Columns: {format_number(column_count)}",
        f"- Duplicate rows: {format_number(duplicate_count)}",
        f"- Missing cells: {format_number(missing_cells)}",
        f"- Missing-cell percentage: {missing_pct:.2f}%",
        "",
        "**Columns:**",
        "",
        ", ".join(f"`{col}`" for col in df.columns),
        ""
    ]

    return lines


# ==================================================
# 3. LOCATION INVENTORY SUMMARY
# ==================================================

def summarize_locations(df):

    lines = ["## 2. Location Inventory", ""]

    if df is None:
        lines += ["Location inventory CSV was not found.", ""]
        return lines

    location_id_col = find_column(
        df, ["id", "location_id"]
    )

    name_col = find_column(
        df, ["name", "location_name"]
    )

    locality_col = find_column(
        df, ["locality", "city", "town"]
    )

    mobile_col = find_column(
        df, ["isMobile", "is_mobile"]
    )

    monitor_col = find_column(
        df, ["isMonitor", "is_monitor"]
    )

    location_count = (
        df[location_id_col].nunique()
        if location_id_col else len(df)
    )

    lines += [
        f"- Total location records: {format_number(len(df))}",
        f"- Unique locations: {format_number(location_count)}",
        ""
    ]

    if name_col:
        lines += [
            f"- Unique location names: {format_number(df[name_col].nunique())}",
            ""
        ]

    if locality_col:
        localities = (
            df[locality_col]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        lines += [
            f"- Localities represented: {len(localities)}",
            "- Locality values: " + (
                ", ".join(localities[:20])
                if localities else "Not available"
            ),
            ""
        ]

    if mobile_col:
        mobile_count = (
            df[mobile_col]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes"])
            .sum()
        )

        lines += [
            f"- Locations marked as mobile: {format_number(mobile_count)}",
            ""
        ]

    if monitor_col:
        monitor_count = (
            df[monitor_col]
            .astype(str)
            .str.lower()
            .isin(["true", "1", "yes"])
            .sum()
        )

        lines += [
            f"- Locations marked as monitors: {format_number(monitor_count)}",
            ""
        ]

    if name_col:
        preview = df[
            [col for col in [location_id_col, name_col, locality_col]
             if col is not None]
        ].drop_duplicates().head(10)

        lines += [
            "**Location examples:**",
            "",
            markdown_table(
                list(preview.columns),
                preview.fillna("Not available").values.tolist()
            ),
            ""
        ]

    return lines


# ==================================================
# 4. SENSOR INVENTORY SUMMARY
# ==================================================

def summarize_sensors(df):

    lines = ["## 3. Sensor Inventory", ""]

    if df is None:
        lines += ["Sensor inventory CSV was not found.", ""]
        return lines

    sensor_id_col = find_column(
        df, ["sensor_id", "id"]
    )

    parameter_col = find_column(
        df, ["parameter_name", "parameter"]
    )

    location_col = find_column(
        df, ["location_id"]
    )

    unique_sensors = (
        df[sensor_id_col].nunique()
        if sensor_id_col else len(df)
    )

    lines += [
        f"- Total sensor records: {format_number(len(df))}",
        f"- Unique sensors: {format_number(unique_sensors)}",
        ""
    ]

    if location_col:
        lines += [
            f"- Locations represented by sensors: "
            f"{format_number(df[location_col].nunique())}",
            ""
        ]

    if parameter_col:

        parameter_summary = (
            df[parameter_col]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .rename_axis("Parameter")
            .reset_index(name="Sensor count")
        )

        lines += [
            "**Sensor distribution by parameter:**",
            "",
            markdown_table(
                ["Parameter", "Sensor count"],
                parameter_summary.values.tolist()
            ),
            ""
        ]

        pm25_sensors = df[
            df[parameter_col]
            .astype(str)
            .str.lower()
            .isin(["pm25", "pm2.5"])
        ]

        lines += [
            f"- PM2.5 sensor records: {format_number(len(pm25_sensors))}",
            ""
        ]

    # Historical coverage metadata, if available

    first_col = find_column(
        df,
        ["coverage_datetimeFirst", "datetimeFirst", "first_datetime"]
    )

    last_col = find_column(
        df,
        ["coverage_datetimeLast", "datetimeLast", "last_datetime"]
    )

    if first_col or last_col:

        lines += [
            "**Reported sensor coverage metadata:**",
            ""
        ]

        if first_col:
            dates = pd.to_datetime(
                df[first_col],
                errors="coerce",
                utc=True
            )

            lines += [
                f"- Earliest reported first observation: "
                f"{dates.min() if dates.notna().any() else 'Not available'}",
                ""
            ]

        if last_col:
            dates = pd.to_datetime(
                df[last_col],
                errors="coerce",
                utc=True
            )

            lines += [
                f"- Latest reported last observation: "
                f"{dates.max() if dates.notna().any() else 'Not available'}",
                ""
            ]

    return lines


# ==================================================
# 5. PM2.5 HISTORY SAMPLE SUMMARY
# ==================================================

def summarize_pm25(df):

    lines = ["## 4. PM2.5 Historical Data Inspection", ""]

    if df is None:
        lines += [
            "PM2.5 history sample CSV was not found.",
            ""
        ]
        return lines

    sensor_col = find_column(
        df, ["sensor_id"]
    )

    location_col = find_column(
        df, ["location_id"]
    )

    value_col = find_column(
        df, ["value", "measurement_value"]
    )

    timestamp_col = find_column(
        df,
        [
            "period_datetimeFrom_utc",
            "period_datetimeFrom",
            "datetime",
            "timestamp",
            "date"
        ]
    )

    lines += [
        f"- Total observations retrieved: {format_number(len(df))}",
        ""
    ]

    if sensor_col:
        lines += [
            f"- Sensors represented: "
            f"{format_number(df[sensor_col].nunique())}",
            ""
        ]

    if location_col:
        lines += [
            f"- Locations represented: "
            f"{format_number(df[location_col].nunique())}",
            ""
        ]

    if timestamp_col:

        timestamps = pd.to_datetime(
            df[timestamp_col],
            errors="coerce",
            utc=True
        )

        valid_timestamps = timestamps.dropna()

        if not valid_timestamps.empty:

            lines += [
                f"- Earliest observation: {valid_timestamps.min()}",
                f"- Latest observation: {valid_timestamps.max()}",
                f"- Rows with invalid timestamps: "
                f"{format_number(timestamps.isna().sum())}",
                ""
            ]

    if value_col:

        values = pd.to_numeric(
            df[value_col],
            errors="coerce"
        )

        lines += [
            "**PM2.5 measurement summary:**",
            "",
            markdown_table(
                ["Metric", "Value"],
                [
                    ["Valid measurements", format_number(values.notna().sum())],
                    ["Missing / invalid measurements", format_number(values.isna().sum())],
                    ["Minimum", values.min()],
                    ["Median", values.median()],
                    ["Mean", values.mean()],
                    ["Maximum", values.max()]
                ]
            ),
            ""
        ]

    if sensor_col:

        sensor_summary = df.groupby(sensor_col).size().reset_index(
            name="Observation count"
        )

        sensor_summary = sensor_summary.sort_values(
            "Observation count",
            ascending=False
        )

        lines += [
            "**Observations by sensor:**",
            "",
            markdown_table(
                list(sensor_summary.columns),
                sensor_summary.head(20).values.tolist()
            ),
            ""
        ]

    lines += [
        "**Interpretation note:**",
        "",
        "This file represents a limited historical-data inspection sample. "
        "It should not be treated as the complete historical dataset or "
        "as evidence of continuous monitoring.",
        ""
    ]

    return lines


# ==================================================
# 6. WEATHER DATA SUMMARY
# ==================================================

def summarize_weather():

    lines = ["## 5. Weather Data Availability", ""]

    weather_files = (
        sorted(WEATHER_DIR.glob("*.csv"))
        if WEATHER_DIR.exists()
        else []
    )

    if not weather_files:
        lines += [
            "No weather CSV files were found in `data/raw/open_meteo/`.",
            "",
            "The Open-Meteo API connection test should be completed "
            "before weather data availability can be assessed.",
            ""
        ]

        return lines

    for path in weather_files:

        df = read_csv(path)

        lines += [
            f"### {path.name}",
            "",
            f"- Rows: {format_number(len(df))}",
            f"- Columns: {format_number(len(df.columns))}",
            "- Available fields: "
            + ", ".join(f"`{col}`" for col in df.columns),
            ""
        ]

        timestamp_col = find_column(
            df, ["time", "datetime", "timestamp"]
        )

        if timestamp_col:

            timestamps = pd.to_datetime(
                df[timestamp_col],
                errors="coerce"
            )

            if timestamps.notna().any():

                lines += [
                    f"- Earliest timestamp: {timestamps.min()}",
                    f"- Latest timestamp: {timestamps.max()}",
                    ""
                ]

    return lines


# ==================================================
# 7. PRELIMINARY DATA SCOPE ASSESSMENT
# ==================================================

def summarize_scope(locations, sensors, pm25):

    lines = [
        "## 6. Preliminary Data Scope Assessment",
        ""
    ]

    if locations is not None:
        lines += [
            f"- The location inventory contains "
            f"{format_number(len(locations))} location records."
        ]

    if sensors is not None:

        parameter_col = find_column(
            sensors, ["parameter_name", "parameter"]
        )

        if parameter_col:

            pm25_count = sensors[
                sensors[parameter_col]
                .astype(str)
                .str.lower()
                .isin(["pm25", "pm2.5"])
            ].shape[0]

            lines += [
                f"- The sensor inventory contains "
                f"{format_number(len(sensors))} sensor records, "
                f"including {format_number(pm25_count)} PM2.5 sensor records."
            ]

    if pm25 is not None:

        sensor_col = find_column(pm25, ["sensor_id"])

        sensor_count = (
            pm25[sensor_col].nunique()
            if sensor_col else "an unknown number of"
        )

        lines += [
            f"- The PM2.5 sample contains "
            f"{format_number(len(pm25))} observations from "
            f"{sensor_count} sensors."
        ]

    lines += [
        "",
        "### Preliminary interpretation",
        "",
        "The discovery outputs establish the initial availability "
        "of monitoring locations, sensor metadata, and a sample of "
        "historical PM2.5 observations.",
        "",
        "The final geographical scope and analysis period should not "
        "be decided from inventory counts alone. Sensor-level historical "
        "coverage, reporting continuity, missing intervals, and data "
        "quality must be examined before selecting the monitoring "
        "locations for the analytical dataset.",
        "",
        "Weather data availability and its temporal alignment with "
        "air-quality observations must also be verified before "
        "conducting the combined analysis.",
        ""
    ]

    return lines


# ==================================================
# 8. GENERATE REPORT
# ==================================================

def main():

    print("\nLoading discovery CSV files...")

    locations = read_csv(LOCATION_FILE)
    sensors = read_csv(SENSOR_FILE)
    pm25 = read_csv(PM25_FILE)

    print("Generating data discovery report...")

    report = [
        "# Jakarta Air Quality Intelligence",
        "",
        "# Data Discovery Report",
        "",
        "## 1. Discovery Overview",
        "",
        "This report summarizes the initial data discovery outputs "
        "collected from OpenAQ and Open-Meteo. It documents the "
        "available data, its structure, and preliminary coverage "
        "before full historical ingestion and data quality assessment.",
        "",
        "The figures in this report are generated directly from the "
        "available CSV files. Missing files or unavailable fields are "
        "not interpreted as zero or as evidence that the data does not exist.",
        ""
    ]

    report += basic_file_summary(
        "Location Inventory",
        locations
    )

    report += basic_file_summary(
        "Sensor Inventory",
        sensors
    )

    report += basic_file_summary(
        "PM2.5 History Sample",
        pm25
    )

    report += summarize_locations(locations)
    report += summarize_sensors(sensors)
    report += summarize_pm25(pm25)
    report += summarize_weather()
    report += summarize_scope(locations, sensors, pm25)

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    REPORT_PATH.write_text(
        "\n".join(report),
        encoding="utf-8"
    )

    print("\n----------------------------------------")
    print("DATA DISCOVERY REPORT GENERATED")
    print("----------------------------------------")

    print(f"Report location: {REPORT_PATH}")

    print("\nCSV files detected:")

    for path in [LOCATION_FILE, SENSOR_FILE, PM25_FILE]:
        status = "Found" if path.exists() else "Not found"
        print(f"- {path.name}: {status}")

    print("\nReport generation completed.")


if __name__ == "__main__":
    main()
