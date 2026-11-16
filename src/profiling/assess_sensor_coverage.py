
from pathlib import Path

import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SENSOR_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "openaq"
    / "sensor_inventory.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "feasibility"
)

OUTPUT_FILE = OUTPUT_DIR / "sensor_coverage_assessment.csv"


# ============================================================
# 2. LOAD SENSOR INVENTORY
# ============================================================

def load_data():
    """Load and validate the sensor inventory."""

    if not SENSOR_FILE.exists():
        raise FileNotFoundError(
            f"Sensor inventory not found: {SENSOR_FILE}"
        )

    sensors = pd.read_csv(SENSOR_FILE)

    required_columns = [
        "location_id",
        "location_name",
        "sensor_id",
        "parameter_name",
        "parameter_units",
        "first_observation",
        "last_observation",
        "percent_complete",
        "observed_count",
        "expected_count",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in sensors.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return sensors


# ============================================================
# 3. STANDARDIZE SENSOR METADATA
# ============================================================

def standardize_data(sensors):
    """Standardize fields used in the assessment."""

    sensors = sensors.copy()

    # Standardize identifiers.
    for column in ["location_id", "sensor_id"]:
        sensors[column] = (
            sensors[column]
            .astype("string")
            .str.strip()
        )

    # Standardize parameter names.
    sensors["normalized_parameter_name"] = (
        sensors["parameter_name"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    # Standardize measurement units.
    sensors["parameter_units"] = (
        sensors["parameter_units"]
        .astype("string")
        .str.strip()
    )

    # Convert numeric metadata.
    numeric_columns = [
        "percent_complete",
        "observed_count",
        "expected_count",
    ]

    for column in numeric_columns:
        sensors[column] = pd.to_numeric(
            sensors[column],
            errors="coerce",
        )

    # Parse observation dates.
    sensors["first_observation"] = pd.to_datetime(
        sensors["first_observation"],
        errors="coerce",
        utc=True,
    )

    sensors["last_observation"] = pd.to_datetime(
        sensors["last_observation"],
        errors="coerce",
        utc=True,
    )

    return sensors


# ============================================================
# 4. FILTER PM2.5 SENSORS
# ============================================================

def filter_pm25_sensors(sensors):
    """Select PM2.5 sensor records."""

    pm25_sensors = sensors[
        sensors["normalized_parameter_name"] == "pm25"
    ].copy()

    if pm25_sensors.empty:
        raise ValueError(
            "No PM2.5 sensor records found in the inventory."
        )

    return pm25_sensors


# ============================================================
# 5. ASSESS HISTORICAL DATE COVERAGE
# ============================================================

def assess_historical_period(sensors):
    """Evaluate the reported historical observation period."""

    sensors["date_range_days"] = (
        sensors["last_observation"]
        - sensors["first_observation"]
    ).dt.total_seconds() / 86400

    sensors["date_range_years"] = (
        sensors["date_range_days"] / 365.25
    )

    sensors["valid_observation_dates"] = (
        sensors["first_observation"].notna()
        & sensors["last_observation"].notna()
        & (sensors["last_observation"] >=
           sensors["first_observation"])
    )

    sensors["date_coverage_status"] = "Valid date range"

    sensors.loc[
        sensors["first_observation"].isna(),
        "date_coverage_status",
    ] = "Missing first observation date"

    sensors.loc[
        sensors["last_observation"].isna(),
        "date_coverage_status",
    ] = "Missing last observation date"

    sensors.loc[
        sensors["first_observation"].notna()
        & sensors["last_observation"].notna()
        & (
            sensors["last_observation"]
            < sensors["first_observation"]
        ),
        "date_coverage_status",
    ] = "Last observation precedes first observation"

    return sensors


# ============================================================
# 6. ASSESS OBSERVATION COUNTS
# ============================================================

def assess_observation_counts(sensors):
    """Evaluate observed and expected observation counts."""

    sensors["valid_observed_count"] = (
        sensors["observed_count"].notna()
        & (sensors["observed_count"] >= 0)
    )

    sensors["valid_expected_count"] = (
        sensors["expected_count"].notna()
        & (sensors["expected_count"] >= 0)
    )

    sensors["count_comparison_ratio"] = pd.NA

    valid_comparison = (
        sensors["valid_observed_count"]
        & sensors["valid_expected_count"]
        & (sensors["expected_count"] > 0)
    )

    sensors.loc[
        valid_comparison,
        "count_comparison_ratio",
    ] = (
        sensors.loc[valid_comparison, "observed_count"]
        / sensors.loc[valid_comparison, "expected_count"]
        * 100
    )

    sensors["count_metadata_status"] = "Available"

    sensors.loc[
        ~sensors["valid_observed_count"],
        "count_metadata_status",
    ] = "Missing or invalid observed count"

    sensors.loc[
        sensors["valid_observed_count"]
        & ~sensors["valid_expected_count"],
        "count_metadata_status",
    ] = "Missing or invalid expected count"

    sensors.loc[
        valid_comparison
        & (sensors["expected_count"] == 0),
        "count_metadata_status",
    ] = "Expected count is zero"

    # Identify observed counts exceeding expected counts.
    sensors["observed_exceeds_expected"] = (
        sensors["valid_observed_count"]
        & sensors["valid_expected_count"]
        & (sensors["observed_count"] >
           sensors["expected_count"])
    )

    return sensors


# ============================================================
# 7. ASSESS COMPLETENESS METADATA
# ============================================================

def assess_completeness(sensors):
    """Evaluate OpenAQ's reported completeness percentage."""

    sensors["valid_percent_complete"] = (
        sensors["percent_complete"].notna()
        & sensors["percent_complete"].between(0, 100)
    )

    sensors["completeness_status"] = "Valid percentage"

    sensors.loc[
        sensors["percent_complete"].isna(),
        "completeness_status",
    ] = "Missing completeness metadata"

    sensors.loc[
        sensors["percent_complete"].notna()
        & ~sensors["percent_complete"].between(0, 100),
        "completeness_status",
    ] = "Percentage outside valid range"

    return sensors


# ============================================================
# 8. ASSESS SENSOR METADATA
# ============================================================

def assess_sensor_metadata(sensors):
    """Identify missing and inconsistent sensor metadata."""

    checked_columns = [
        "location_id",
        "location_name",
        "sensor_id",
        "parameter_units",
    ]

    def get_missing_fields(row):
        missing_fields = []

        for column in checked_columns:
            value = row[column]

            if pd.isna(value) or (
                isinstance(value, str)
                and not value.strip()
            ):
                missing_fields.append(column)

        return "; ".join(missing_fields)

    sensors["missing_sensor_fields"] = sensors.apply(
        get_missing_fields,
        axis=1,
    )

    sensors["missing_field_count"] = (
        sensors["missing_sensor_fields"]
        .apply(
            lambda value: (
                len(value.split("; "))
                if value
                else 0
            )
        )
    )

    # Check whether sensor IDs appear more than once.
    sensor_id_counts = (
        sensors.groupby("sensor_id")["location_id"]
        .transform("size")
    )

    sensors["duplicate_sensor_id"] = (
        sensor_id_counts > 1
    )

    return sensors


# ============================================================
# 9. GENERATE ASSESSMENT NOTES
# ============================================================

def generate_assessment_notes(sensors):
    """Generate descriptive notes for manual investigation."""

    def create_note(row):
        notes = []

        if not row["valid_observation_dates"]:
            notes.append(row["date_coverage_status"])

        if row["completeness_status"] != "Valid percentage":
            notes.append(row["completeness_status"])

        if row["count_metadata_status"] != "Available":
            notes.append(row["count_metadata_status"])

        if row["observed_exceeds_expected"]:
            notes.append("Observed count exceeds expected count")

        if row["missing_field_count"] > 0:
            notes.append("Incomplete sensor metadata")

        if row["duplicate_sensor_id"]:
            notes.append("Duplicate sensor ID in PM2.5 inventory")

        if not notes:
            notes.append("No initial coverage metadata issue identified")

        return "; ".join(notes)

    sensors["assessment_notes"] = sensors.apply(
        create_note,
        axis=1,
    )

    return sensors


# ============================================================
# 10. BUILD SENSOR COVERAGE OUTPUT
# ============================================================

def build_assessment(sensors):
    """Select and arrange the assessment output columns."""

    output_columns = [
        "location_id",
        "location_name",
        "sensor_id",
        "parameter_name",
        "parameter_units",
        "first_observation",
        "last_observation",
        "date_range_days",
        "date_range_years",
        "valid_observation_dates",
        "date_coverage_status",
        "observed_count",
        "expected_count",
        "count_comparison_ratio",
        "count_metadata_status",
        "observed_exceeds_expected",
        "percent_complete",
        "valid_percent_complete",
        "completeness_status",
        "missing_field_count",
        "missing_sensor_fields",
        "duplicate_sensor_id",
        "assessment_notes",
    ]

    return sensors[output_columns].sort_values(
        by=["percent_complete", "date_range_days"],
        ascending=[False, False],
        na_position="last",
    )


# ============================================================
# 11. SAVE ASSESSMENT
# ============================================================

def save_assessment(assessment):
    """Save the sensor coverage assessment."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    assessment.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nSensor coverage assessment saved:")
    print(OUTPUT_FILE)


# ============================================================
# 12. PRINT ASSESSMENT SUMMARY
# ============================================================

def print_summary(assessment):
    """Print a summary of the sensor coverage assessment."""

    print("\n" + "=" * 65)
    print("PM2.5 SENSOR COVERAGE ASSESSMENT")
    print("=" * 65)

    print(f"PM2.5 sensor records: {len(assessment)}")

    print(
        "Unique sensor IDs:",
        assessment["sensor_id"].nunique(),
    )

    print(
        "Sensors with valid observation dates:",
        assessment["valid_observation_dates"].sum(),
    )

    print(
        "Sensors with valid completeness metadata:",
        assessment["valid_percent_complete"].sum(),
    )

    print(
        "Sensors with valid observed counts:",
        assessment["observed_count"].notna().sum(),
    )

    print(
        "Sensors with valid expected counts:",
        assessment["expected_count"].notna().sum(),
    )

    print(
        "Sensors with duplicate IDs:",
        assessment["duplicate_sensor_id"].sum(),
    )

    print(
        "Sensors with missing metadata:",
        (assessment["missing_field_count"] > 0).sum(),
    )

    print("\nCompleteness metadata distribution:")

    print(
        assessment["completeness_status"]
        .value_counts()
        .to_string()
    )

    print("\nAssessment notes:")

    print(
        assessment["assessment_notes"]
        .value_counts()
        .to_string()
    )

    print("\nSensor coverage comparison:")

    display_columns = [
        "sensor_id",
        "location_name",
        "first_observation",
        "last_observation",
        "date_range_years",
        "observed_count",
        "expected_count",
        "percent_complete",
        "assessment_notes",
    ]

    print(
        assessment[display_columns]
        .to_string(index=False)
    )


# ============================================================
# 13. MAIN EXECUTION
# ============================================================

def main():
    print("Starting PM2.5 sensor coverage assessment...")

    sensors = load_data()

    sensors = standardize_data(sensors)

    sensors = filter_pm25_sensors(sensors)

    sensors = assess_historical_period(sensors)

    sensors = assess_observation_counts(sensors)

    sensors = assess_completeness(sensors)

    sensors = assess_sensor_metadata(sensors)

    sensors = generate_assessment_notes(sensors)

    assessment = build_assessment(sensors)

    save_assessment(assessment)

    print_summary(assessment)

    print("\nSensor coverage assessment completed.")


if __name__ == "__main__":
    main()
