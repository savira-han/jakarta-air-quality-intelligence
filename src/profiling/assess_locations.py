
from pathlib import Path

import pandas as pd


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOCATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "openaq"
    / "location_inventory.csv"
)

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

OUTPUT_FILE = OUTPUT_DIR / "location_comparison.csv"


# ============================================================
# 2. LOAD INPUT DATA
# ============================================================

def load_data():
    """Load location and sensor inventories."""

    if not LOCATION_FILE.exists():
        raise FileNotFoundError(
            f"Location inventory not found: {LOCATION_FILE}"
        )

    if not SENSOR_FILE.exists():
        raise FileNotFoundError(
            f"Sensor inventory not found: {SENSOR_FILE}"
        )

    locations = pd.read_csv(LOCATION_FILE)
    sensors = pd.read_csv(SENSOR_FILE)

    required_location_columns = [
        "location_id",
        "location_name",
        "latitude",
        "longitude",
        "provider",
        "owner",
    ]

    required_sensor_columns = [
        "location_id",
        "sensor_id",
        "parameter_name",
    ]

    missing_location_columns = [
        column
        for column in required_location_columns
        if column not in locations.columns
    ]

    missing_sensor_columns = [
        column
        for column in required_sensor_columns
        if column not in sensors.columns
    ]

    if missing_location_columns:
        raise ValueError(
            "Missing location columns: "
            f"{missing_location_columns}"
        )

    if missing_sensor_columns:
        raise ValueError(
            "Missing sensor columns: "
            f"{missing_sensor_columns}"
        )

    return locations, sensors


# ============================================================
# 3. STANDARDIZE COMPARISON FIELDS
# ============================================================

def standardize_data(locations, sensors):
    """Standardize fields used for location comparisons."""

    locations = locations.copy()
    sensors = sensors.copy()

    # Use string IDs to avoid mismatches between numeric
    # and string representations of location IDs.
    locations["location_id"] = (
        locations["location_id"].astype("string").str.strip()
    )

    sensors["location_id"] = (
        sensors["location_id"].astype("string").str.strip()
    )

    # Normalize location names for duplicate-name detection.
    locations["normalized_location_name"] = (
        locations["location_name"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    # Convert coordinates into numeric values.
    locations["latitude"] = pd.to_numeric(
        locations["latitude"],
        errors="coerce",
    )

    locations["longitude"] = pd.to_numeric(
        locations["longitude"],
        errors="coerce",
    )

    # Normalize parameter names for PM2.5 identification.
    sensors["normalized_parameter_name"] = (
        sensors["parameter_name"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    return locations, sensors


# ============================================================
# 4. ASSESS SENSOR ASSOCIATIONS
# ============================================================

def assess_sensor_associations(locations, sensors):
    """Calculate sensor counts for each location."""

    sensor_summary = (
        sensors.groupby("location_id", dropna=False)
        .agg(
            sensor_count=("sensor_id", "nunique"),
            pm25_sensor_count=(
                "normalized_parameter_name",
                lambda values: values.eq("pm25").sum(),
            ),
        )
        .reset_index()
    )

    locations = locations.merge(
        sensor_summary,
        on="location_id",
        how="left",
    )

    locations["sensor_count"] = (
        locations["sensor_count"].fillna(0).astype(int)
    )

    locations["pm25_sensor_count"] = (
        locations["pm25_sensor_count"].fillna(0).astype(int)
    )

    return locations


# ============================================================
# 5. ASSESS LOCATION IDENTITIES
# ============================================================

def assess_location_identity(locations):
    """Identify repeated location names and coordinates."""

    # Count how many location records share each normalized name.
    name_counts = (
        locations.groupby("normalized_location_name")[
            "location_id"
        ]
        .transform("count")
    )

    locations["same_name_location_count"] = (
        name_counts.where(
            locations["normalized_location_name"].notna(),
            0,
        )
        .astype(int)
    )

    locations["duplicate_location_name"] = (
        locations["same_name_location_count"] > 1
    )

    # Capture the IDs associated with each repeated name.
    name_id_map = (
        locations.groupby("normalized_location_name")[
            "location_id"
        ]
        .agg(
            lambda values: "; ".join(
                sorted(values.dropna().unique())
            )
        )
    )

    locations["same_name_location_ids"] = (
        locations["normalized_location_name"]
        .map(name_id_map)
        .fillna("")
    )

    # Compare coordinates rounded to five decimal places.
    # This identifies matching reported coordinates,
    # not necessarily identical physical monitoring sites.
    locations["coordinate_group"] = (
        locations["latitude"].round(5).astype("string")
        + ","
        + locations["longitude"].round(5).astype("string")
    )

    valid_coordinates = (
        locations["latitude"].between(-90, 90)
        & locations["longitude"].between(-180, 180)
    )

    locations.loc[
        ~valid_coordinates,
        "coordinate_group",
    ] = pd.NA

    coordinate_counts = (
        locations.groupby("coordinate_group", dropna=True)[
            "location_id"
        ]
        .transform("count")
    )

    locations["same_coordinate_location_count"] = (
        coordinate_counts.reindex(locations.index)
        .fillna(0)
        .astype(int)
    )

    locations["duplicate_coordinates"] = (
        locations["same_coordinate_location_count"] > 1
    )

    return locations


# ============================================================
# 6. ASSESS MISSING AND INVALID INFORMATION
# ============================================================

def assess_location_data_quality(locations):
    """Identify missing and invalid location information."""

    locations["valid_coordinates"] = (
        locations["latitude"].between(-90, 90)
        & locations["longitude"].between(-180, 180)
    )

    checked_columns = [
        "location_name",
        "latitude",
        "longitude",
        "provider",
        "owner",
        "timezone",
    ]

    # Record missing fields for each location.
    def get_missing_fields(row):
        missing_fields = []

        for column in checked_columns:
            value = row[column]

            if pd.isna(value) or (
                isinstance(value, str) and not value.strip()
            ):
                missing_fields.append(column)

        return "; ".join(missing_fields)

    locations["missing_location_fields"] = locations.apply(
        get_missing_fields,
        axis=1,
    )

    locations["missing_field_count"] = (
        locations["missing_location_fields"]
        .apply(
            lambda value: (
                len(value.split("; "))
                if value
                else 0
            )
        )
    )

    return locations


# ============================================================
# 7. GENERATE ASSESSMENT NOTES
# ============================================================

def generate_assessment_notes(locations):
    """Generate descriptive notes for manual review."""

    def create_note(row):
        notes = []

        if row["duplicate_location_name"]:
            notes.append("Repeated location name")

        if row["duplicate_coordinates"]:
            notes.append("Matching reported coordinates")

        if not row["valid_coordinates"]:
            notes.append("Missing or invalid coordinates")

        if row["pm25_sensor_count"] == 0:
            notes.append("No PM2.5 sensor in inventory")

        if row["missing_field_count"] > 0:
            notes.append("Incomplete location metadata")

        if not notes:
            notes.append("No initial location issue identified")

        return "; ".join(notes)

    locations["assessment_notes"] = locations.apply(
        create_note,
        axis=1,
    )

    return locations


# ============================================================
# 8. BUILD LOCATION COMPARISON OUTPUT
# ============================================================

def build_location_assessment(locations):
    """Select and arrange assessment output columns."""

    output_columns = [
        "location_id",
        "location_name",
        "latitude",
        "longitude",
        "timezone",
        "provider",
        "owner",
        "is_mobile",
        "is_monitor",
        "sensor_count",
        "pm25_sensor_count",
        "same_name_location_count",
        "same_name_location_ids",
        "duplicate_location_name",
        "same_coordinate_location_count",
        "duplicate_coordinates",
        "valid_coordinates",
        "missing_field_count",
        "missing_location_fields",
        "assessment_notes",
    ]

    # Preserve only columns available in the source.
    output_columns = [
        column
        for column in output_columns
        if column in locations.columns
    ]

    return locations[output_columns].sort_values(
        by=["location_name", "location_id"],
        na_position="last",
    )


# ============================================================
# 9. SAVE OUTPUT AND PRINT SUMMARY
# ============================================================

def save_assessment(assessment):
    """Save the location assessment CSV."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    assessment.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nLocation assessment saved:")
    print(OUTPUT_FILE)


def print_summary(assessment):
    """Print a summary of the assessment results."""

    print("\n" + "=" * 60)
    print("LOCATION FEASIBILITY ASSESSMENT")
    print("=" * 60)

    print(f"Location records: {len(assessment)}")

    print(
        "Unique location IDs:",
        assessment["location_id"].nunique(),
    )

    print(
        "Locations with PM2.5 sensors:",
        (assessment["pm25_sensor_count"] > 0).sum(),
    )

    print(
        "Locations with repeated names:",
        assessment["duplicate_location_name"].sum(),
    )

    print(
        "Locations with matching coordinates:",
        assessment["duplicate_coordinates"].sum(),
    )

    print(
        "Locations with invalid or missing coordinates:",
        (~assessment["valid_coordinates"]).sum(),
    )

    print(
        "Locations with incomplete metadata:",
        (assessment["missing_field_count"] > 0).sum(),
    )

    print("\nAssessment notes:")
    print(
        assessment["assessment_notes"]
        .value_counts()
        .to_string()
    )

    print("\nFirst 10 records:")
    print(
        assessment[
            [
                "location_id",
                "location_name",
                "sensor_count",
                "pm25_sensor_count",
                "assessment_notes",
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


# ============================================================
# 10. MAIN EXECUTION
# ============================================================

def main():
    print("Starting location feasibility assessment...")

    locations, sensors = load_data()

    locations, sensors = standardize_data(
        locations,
        sensors,
    )

    locations = assess_sensor_associations(
        locations,
        sensors,
    )

    locations = assess_location_identity(locations)

    locations = assess_location_data_quality(locations)

    locations = generate_assessment_notes(locations)

    assessment = build_location_assessment(locations)

    save_assessment(assessment)

    print_summary(assessment)

    print("\nLocation assessment completed.")


if __name__ == "__main__":
    main()
