
from __future__ import annotations

import json
import math
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from shapely.geometry import Point, shape
from shapely.ops import unary_union


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOCATION_INVENTORY_PATH = (
    PROJECT_ROOT / "data/raw/openaq/location_inventory.csv"
)

SENSOR_INVENTORY_PATH = (
    PROJECT_ROOT / "data/raw/openaq/sensor_inventory.csv"
)

BOUNDARY_PATH = (
    PROJECT_ROOT / "data/reference/dki_jakarta_boundary.geojson"
)

OUTPUT_ROOT = (
    PROJECT_ROOT / "data/raw/openaq/pm25_hours"
)

FEASIBILITY_OUTPUT = (
    PROJECT_ROOT / "data/processed/feasibility"
)

API_BASE_URL = "https://api.openaq.org/v3"

BOUNDARY_QUERY_URL = (
    "https://gis-dpmptsp.jakarta.go.id/arcgis/rest/services/"
    "Hosted/Batas_Administrasi_Kecamatan_Jakarta/"
    "FeatureServer/0/query"
)

# Study period:
# November 2025 through October 2026.
#
# The API timestamps hourly observations at the END of
# each measurement period.
# For example, 01:00 represents 00:00-00:59.
#
# Therefore, each monthly request starts at 01:00 on the
# first day and ends at 00:00 on the first day of the
# following month.

STUDY_START = pd.Timestamp("2025-11-01 00:00:00")
STUDY_END_EXCLUSIVE = pd.Timestamp("2026-11-01 00:00:00")

LOCAL_TIMEZONE = "Asia/Jakarta"
LOCAL_UTC_OFFSET = "+07:00"

API_LIMIT = 1000
REQUEST_TIMEOUT = (15, 120)

MAX_PAGES_PER_WINDOW = 100

# Retry temporary API failures, including HTTP 408.
RETRY_TOTAL = 5
RETRY_BACKOFF = 2

# Small pause between requests.
REQUEST_PAUSE_SECONDS = 0.2


# ============================================================
# SESSION AND AUTHENTICATION
# ============================================================

def create_session(api_key: str) -> requests.Session:
    """
    Create an authenticated session with retry handling.
    """

    session = requests.Session()

    session.headers.update(
        {
            "X-API-Key": api_key,
            "Accept": "application/json",
        }
    )

    retry_strategy = Retry(
        total=RETRY_TOTAL,
        connect=RETRY_TOTAL,
        read=RETRY_TOTAL,
        status=RETRY_TOTAL,
        backoff_factor=RETRY_BACKOFF,
        status_forcelist=[
            408,
            429,
            500,
            502,
            503,
            504,
        ],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
        raise_on_status=False,
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy
    )

    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def get_api_key() -> str:
    """
    Load OpenAQ API key from the root .env file.
    """

    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.getenv("OPENAQ_API_KEY")

    if not api_key:
        raise ValueError(
            "OPENAQ_API_KEY was not found. "
            "Check the root .env file."
        )

    return api_key


# ============================================================
# DIRECTORY SETUP
# ============================================================

def create_output_directories() -> None:
    """
    Create required output directories.
    """

    BOUNDARY_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    FEASIBILITY_OUTPUT.mkdir(
        parents=True,
        exist_ok=True,
    )


# ============================================================
# JAKARTA ADMINISTRATIVE BOUNDARY
# ============================================================

def retrieve_jakarta_boundary(
    session: requests.Session,
):
    """
    Download the DKI Jakarta administrative boundary
    if it is not already available locally.

    The boundary layer contains administrative
    subdistrict polygons.
    """

    if BOUNDARY_PATH.exists():
        print("Using cached DKI Jakarta boundary.")

        with open(
            BOUNDARY_PATH,
            "r",
            encoding="utf-8",
        ) as file:
            geojson = json.load(file)

    else:
        print("Downloading DKI Jakarta boundary...")

        params = {
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
        }

        response = session.get(
            BOUNDARY_QUERY_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        geojson = response.json()

        if not geojson.get("features"):
            raise ValueError(
                "The Jakarta boundary response "
                "does not contain any features."
            )

        with open(
            BOUNDARY_PATH,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                geojson,
                file,
                ensure_ascii=False,
            )

    features = geojson.get("features", [])

    geometries = [
        shape(feature["geometry"])
        for feature in features
        if feature.get("geometry")
    ]

    if not geometries:
        raise ValueError(
            "No valid geometries found in the "
            "Jakarta boundary file."
        )

    boundary = unary_union(geometries)

    if boundary.is_empty or not boundary.is_valid:
        raise ValueError(
            "The Jakarta boundary geometry is invalid."
        )

    print(
        f"Boundary loaded successfully: "
        f"{len(geometries)} polygons."
    )

    return boundary


# ============================================================
# SENSOR INVENTORY AND GEOGRAPHICAL FILTERING
# ============================================================

def load_inventory() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load location and sensor inventories.
    """

    if not LOCATION_INVENTORY_PATH.exists():
        raise FileNotFoundError(
            f"Missing file: {LOCATION_INVENTORY_PATH}"
        )

    if not SENSOR_INVENTORY_PATH.exists():
        raise FileNotFoundError(
            f"Missing file: {SENSOR_INVENTORY_PATH}"
        )

    locations = pd.read_csv(
        LOCATION_INVENTORY_PATH
    )

    sensors = pd.read_csv(
        SENSOR_INVENTORY_PATH
    )

    required_location_columns = {
        "location_id",
        "latitude",
        "longitude",
    }

    required_sensor_columns = {
        "sensor_id",
        "location_id",
        "parameter_name",
    }

    missing_location_columns = (
        required_location_columns
        - set(locations.columns)
    )

    missing_sensor_columns = (
        required_sensor_columns
        - set(sensors.columns)
    )

    if missing_location_columns:
        raise ValueError(
            "Missing location inventory columns: "
            f"{sorted(missing_location_columns)}"
        )

    if missing_sensor_columns:
        raise ValueError(
            "Missing sensor inventory columns: "
            f"{sorted(missing_sensor_columns)}"
        )

    locations["location_id"] = (
        locations["location_id"].astype(str)
    )

    sensors["location_id"] = (
        sensors["location_id"].astype(str)
    )

    sensors["sensor_id"] = (
        sensors["sensor_id"].astype(str)
    )

    if sensors["sensor_id"].duplicated().any():
        raise ValueError(
            "Duplicate sensor IDs detected in "
            "sensor_inventory.csv. Resolve these "
            "before retrieval."
        )

    return locations, sensors


def identify_jakarta_pm25_sensors(
    locations: pd.DataFrame,
    sensors: pd.DataFrame,
    boundary,
) -> pd.DataFrame:
    """
    Identify PM2.5 sensors whose location coordinates
    fall inside the DKI Jakarta administrative boundary.

    All PM2.5 sensors are retained in the output
    candidate file, including excluded sensors.
    """
    location_columns = [
        "location_id",
        "latitude",
        "longitude",
    ]

    optional_location_columns = [
        "provider",
        "owner",
        "timezone",
    ]

    for column in optional_location_columns:
        if (
            column in locations.columns
            and column not in sensors.columns
        ):
            location_columns.append(column)

    for column in optional_location_columns:
        if column in locations.columns:
            location_columns.append(column)

    location_data = locations[
        location_columns
    ].copy()

    merged = sensors.merge(
        location_data,
        on="location_id",
        how="left",
        suffixes=("_sensor", "_location"),
        validate="many_to_one",
    )

    parameter_normalized = (
        merged["parameter_name"]
        .astype(str)
        .str.lower()
        .str.replace(
            r"[^a-z0-9]",
            "",
            regex=True,
        )
    )

    pm25 = merged[
        parameter_normalized == "pm25"
    ].copy()

    if pm25.empty:
        raise ValueError(
            "No PM2.5 sensors found in the inventory."
        )

    pm25["latitude"] = pd.to_numeric(
        pm25["latitude"],
        errors="coerce",
    )

    pm25["longitude"] = pd.to_numeric(
        pm25["longitude"],
        errors="coerce",
    )

    pm25["inside_dki_jakarta"] = False
    pm25["exclusion_reason"] = ""

    for index, row in pm25.iterrows():

        latitude = row["latitude"]
        longitude = row["longitude"]

        if pd.isna(latitude) or pd.isna(longitude):
            pm25.at[
                index,
                "exclusion_reason",
            ] = "Missing or invalid coordinates"

            continue

        if not (-90 <= latitude <= 90):
            pm25.at[
                index,
                "exclusion_reason",
            ] = "Invalid latitude"

            continue

        if not (-180 <= longitude <= 180):
            pm25.at[
                index,
                "exclusion_reason",
            ] = "Invalid longitude"

            continue

        point = Point(
            longitude,
            latitude,
        )

        if boundary.covers(point):
            pm25.at[
                index,
                "inside_dki_jakarta",
            ] = True

        else:
            pm25.at[
                index,
                "exclusion_reason",
            ] = "Outside DKI Jakarta boundary"

    candidate_path = (
        FEASIBILITY_OUTPUT
        / "jakarta_pm25_sensor_candidates.csv"
    )

    pm25.to_csv(
        candidate_path,
        index=False,
    )

    candidates = pm25[
        pm25["inside_dki_jakarta"]
    ].copy()

    print("\nSensor selection summary")
    print("------------------------")
    print(f"PM2.5 sensors in inventory: {len(pm25)}")
    print(f"Inside DKI Jakarta: {len(candidates)}")
    print(
        f"Outside or excluded: "
        f"{len(pm25) - len(candidates)}"
    )

    print(
        f"\nCandidate list saved to: {candidate_path}"
    )

    return candidates


# ============================================================
# MONTHLY WINDOW GENERATION
# ============================================================

def generate_monthly_windows() -> list[dict]:
    """
    Generate one request window per calendar month.

    OpenAQ uses time-ending timestamps for hourly data.

    For example:
    2025-11-01 01:00 Jakarta represents
    2025-11-01 00:00 to 00:59 Jakarta.

    The monthly windows are therefore:
    2025-11-01 01:00 through 2025-12-01 00:00
    2025-12-01 01:00 through 2026-01-01 00:00
    and so on.
    """

    windows = []

    month_start = STUDY_START

    while month_start < STUDY_END_EXCLUSIVE:

        next_month = (
            month_start + pd.offsets.MonthBegin(1)
        )

        # First hour-ending timestamp of the month.
        request_start = (
            month_start + pd.Timedelta(hours=1)
        )

        # Final hour-ending timestamp of the month.
        request_end = next_month

        windows.append(
            {
                "month": month_start.strftime("%Y-%m"),
                "datetime_from": (
                    request_start.strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    )
                    + LOCAL_UTC_OFFSET
                ),
                "datetime_to": (
                    request_end.strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    )
                    + LOCAL_UTC_OFFSET
                ),
            }
        )

        month_start = next_month

    return windows


# ============================================================
# API RETRIEVAL
# ============================================================

def retrieve_month(
    session: requests.Session,
    sensor_id: str,
    window: dict,
) -> dict:
    """
    Retrieve one sensor's hourly observations
    for one calendar month.

    Pagination continues until all available
    results have been retrieved.

    If a request fails, successfully retrieved
    pages are returned as partial results.
    """

    url = (
        f"{API_BASE_URL}/sensors/"
        f"{sensor_id}/hours"
    )

    all_records = []
    page = 1
    total_found = None

    while page <= MAX_PAGES_PER_WINDOW:

        params = {
            "datetime_from": window["datetime_from"],
            "datetime_to": window["datetime_to"],
            "limit": API_LIMIT,
            "page": page,
        }

        try:
            response = session.get(
                url,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            response.raise_for_status()

            payload = response.json()

        except requests.RequestException as error:

            return {
                "status": (
                    "partial"
                    if all_records
                    else "failed"
                ),
                "records": all_records,
                "page_count": page - 1,
                "error": str(error),
            }

        except ValueError as error:

            return {
                "status": (
                    "partial"
                    if all_records
                    else "failed"
                ),
                "records": all_records,
                "page_count": page - 1,
                "error": (
                    f"Invalid JSON response: {error}"
                ),
            }

        results = payload.get("results", [])
        meta = payload.get("meta", {})

        if total_found is None:
            total_found = meta.get("found")

        all_records.extend(results)

        print(
            f"      Page {page}: "
            f"{len(results)} observations"
        )

        # If the API reports the total result count,
        # use it to determine when pagination is done.
        if total_found is not None:

            try:
                total_found = int(total_found)

                expected_pages = max(
                    1,
                    math.ceil(
                        total_found / API_LIMIT
                    ),
                )

                if page >= expected_pages:
                    break

            except (TypeError, ValueError):
                total_found = None

        # Fallback if total count is unavailable.
        if total_found is None:
            if len(results) < API_LIMIT:
                break

        page += 1

        time.sleep(REQUEST_PAUSE_SECONDS)

    else:
        return {
            "status": (
                "partial"
                if all_records
                else "failed"
            ),
            "records": all_records,
            "page_count": page - 1,
            "error": (
                "Maximum page limit reached. "
                "Window may be incomplete."
            ),
        }

    return {
        "status": "complete",
        "records": all_records,
        "page_count": page,
        "error": "",
    }


# ============================================================
# DATA NORMALIZATION AND STORAGE
# ============================================================

def normalize_records(
    records: list[dict],
    sensor: pd.Series,
    window: dict,
) -> pd.DataFrame:
    """
    Flatten OpenAQ API results while preserving
    the original returned fields.
    """

    if records:
        df = pd.json_normalize(records)

    else:
        df = pd.DataFrame()

    df["sensor_id"] = str(sensor["sensor_id"])
    df["location_id"] = str(sensor["location_id"])

    if "location_name" in sensor.index:
        df["location_name"] = sensor["location_name"]

    df["parameter_name"] = sensor["parameter_name"]

    if "parameter_units" in sensor.index:
        df["parameter_units"] = (
            sensor["parameter_units"]
        )

    df["requested_month"] = window["month"]

    df["retrieved_at_utc"] = (
        datetime.now(timezone.utc).isoformat()
    )

    return df


def get_month_paths(
    sensor_id: str,
    month: str,
) -> dict:
    """
    Return the file paths for a sensor-month window.
    """

    sensor_directory = (
        OUTPUT_ROOT / f"sensor_{sensor_id}"
    )

    sensor_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return {
        "csv": (
            sensor_directory / f"{month}.csv"
        ),
        "partial": (
            sensor_directory / f"{month}.partial.csv"
        ),
        "marker": (
            sensor_directory / f"{month}.complete.json"
        ),
    }


def load_completion_marker(
    marker_path: Path,
) -> dict | None:
    """
    Read a successful retrieval marker.
    """

    if not marker_path.exists():
        return None

    try:
        with open(
            marker_path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    except (OSError, json.JSONDecodeError):
        return None


def save_month_result(
    df: pd.DataFrame,
    paths: dict,
    status: str,
    metadata: dict,
) -> None:
    """
    Save monthly observations.

    Complete windows receive a completion marker.
    Partial windows are saved separately and
    will be retried on the next run.
    """

    if status == "complete":

        df.to_csv(
            paths["csv"],
            index=False,
        )

        if paths["partial"].exists():
            paths["partial"].unlink()

        with open(
            paths["marker"],
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                metadata,
                file,
                indent=4,
            )

    elif status == "partial":

        if df.empty:
            return

        df.to_csv(
            paths["partial"],
            index=False,
        )


# ============================================================
# RETRIEVAL LOGGING
# ============================================================

def append_window_log(
    row: dict,
) -> None:
    """
    Append one monthly retrieval result to the
    persistent retrieval log immediately.
    """

    log_path = (
        FEASIBILITY_OUTPUT
        / "pm25_retrieval_window_log.csv"
    )

    log_df = pd.DataFrame([row])

    log_df.to_csv(
        log_path,
        mode="a",
        header=not log_path.exists(),
        index=False,
    )


def save_sensor_summary(
    summary_rows: list[dict],
) -> None:
    """
    Save the current run's sensor-level summary.
    """

    summary_path = (
        FEASIBILITY_OUTPUT
        / "pm25_retrieval_sensor_summary.csv"
    )

    pd.DataFrame(summary_rows).to_csv(
        summary_path,
        index=False,
    )


# ============================================================
# SENSOR RETRIEVAL ORCHESTRATION
# ============================================================

def retrieve_sensor_data(
    session: requests.Session,
    sensor: pd.Series,
    windows: list[dict],
) -> dict:
    """
    Retrieve all 12 monthly windows for one sensor.

    Completed windows are skipped on subsequent runs.
    Partial and failed windows are retried.
    """

    sensor_id = str(sensor["sensor_id"])

    print("\n" + "=" * 60)
    print(
        f"Sensor: {sensor_id} | "
        f"Location: {sensor.get('location_name', 'Unknown')}"
    )
    print("=" * 60)

    counts = {
        "complete": 0,
        "partial": 0,
        "failed": 0,
        "skipped": 0,
        "records": 0,
    }

    for window in windows:

        month = window["month"]

        paths = get_month_paths(
            sensor_id,
            month,
        )

        print(f"\n  Month: {month}")

        existing_marker = load_completion_marker(
            paths["marker"]
        )

        # Skip only if both the data file and its
        # successful completion marker exist.
        if (
            existing_marker is not None
            and paths["csv"].exists()
        ):

            print("    Already complete. Skipping.")

            counts["skipped"] += 1

            records_count = int(
                existing_marker.get(
                    "records_count",
                    0,
                )
            )

            counts["records"] += records_count

            append_window_log(
                {
                    "run_timestamp_utc": (
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    ),
                    "sensor_id": sensor_id,
                    "location_id": sensor["location_id"],
                    "location_name": sensor.get(
                        "location_name",
                        "",
                    ),
                    "month": month,
                    "status": "skipped_complete",
                    "records_count": records_count,
                    "page_count": existing_marker.get(
                        "page_count",
                        0,
                    ),
                    "error": "",
                }
            )

            continue

        print(
            f"    Retrieving "
            f"{window['datetime_from']} "
            f"to {window['datetime_to']}"
        )

        if paths["partial"].exists():
            paths["partial"].unlink()

        result = retrieve_month(
            session=session,
            sensor_id=sensor_id,
            window=window,
        )

        df = normalize_records(
            records=result["records"],
            sensor=sensor,
            window=window,
        )

        metadata = {
            "sensor_id": sensor_id,
            "location_id": str(sensor["location_id"]),
            "month": month,
            "status": result["status"],
            "records_count": len(df),
            "page_count": result["page_count"],
            "datetime_from": window["datetime_from"],
            "datetime_to": window["datetime_to"],
            "retrieved_at_utc": (
                datetime.now(timezone.utc).isoformat()
            ),
        }

        save_month_result(
            df=df,
            paths=paths,
            status=result["status"],
            metadata=metadata,
        )

        status = result["status"]

        counts[status] += 1
        counts["records"] += len(df)

        append_window_log(
            {
                "run_timestamp_utc": (
                    datetime.now(
                        timezone.utc
                    ).isoformat()
                ),
                "sensor_id": sensor_id,
                "location_id": sensor["location_id"],
                "location_name": sensor.get(
                    "location_name",
                    "",
                ),
                "month": month,
                "status": status,
                "records_count": len(df),
                "page_count": result["page_count"],
                "error": result["error"],
            }
        )

        print(
            f"    Status: {status.upper()} | "
            f"Records: {len(df)}"
        )

        if result["error"]:
            print(
                f"    Error: {result['error']}"
            )

    total_completed = (
        counts["complete"] + counts["skipped"]
    )

    if total_completed == len(windows):
        retrieval_status = "Complete"

    elif counts["records"] > 0:
        retrieval_status = "Partial"

    else:
        retrieval_status = "Failed"

    return {
        "sensor_id": sensor_id,
        "location_id": sensor["location_id"],
        "location_name": sensor.get(
            "location_name",
            "",
        ),
        "retrieval_status": retrieval_status,
        "complete_windows": counts["complete"],
        "skipped_windows": counts["skipped"],
        "partial_windows": counts["partial"],
        "failed_windows": counts["failed"],
        "records_retrieved": counts["records"],
    }


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """
    Execute the bounded Jakarta PM2.5 retrieval process.
    """

    print("=" * 60)
    print("JAKARTA PM2.5 DATA RETRIEVAL")
    print("=" * 60)

    print(
        "Study period: "
        "1 November 2025 - 31 October 2026"
    )

    print("Geography: DKI Jakarta only")
    print("Parameter: PM2.5")
    print("Frequency: Hourly")

    create_output_directories()

    api_key = get_api_key()
    session = create_session(api_key)

    # 1. Load existing inventories.
    locations, sensors = load_inventory()

    # 2. Load the DKI Jakarta boundary.
    boundary = retrieve_jakarta_boundary(
        session
    )

    # 3. Identify eligible Jakarta PM2.5 sensors.
    candidates = identify_jakarta_pm25_sensors(
        locations=locations,
        sensors=sensors,
        boundary=boundary,
    )

    if candidates.empty:
        raise ValueError(
            "No eligible Jakarta PM2.5 sensors found. "
            "Review the inventory and boundary."
        )

    # 4. Generate 12 monthly retrieval windows.
    windows = generate_monthly_windows()

    print(
        f"\nMonthly windows: {len(windows)}"
    )

    # 5. Retrieve each candidate sensor.
    summary_rows = []

    for _, sensor in candidates.iterrows():

        summary = retrieve_sensor_data(
            session=session,
            sensor=sensor,
            windows=windows,
        )

        summary_rows.append(summary)

        # Save after each sensor so progress is retained.
        save_sensor_summary(summary_rows)

    # 6. Final summary.
    summary_df = pd.DataFrame(summary_rows)

    print("\n" + "=" * 60)
    print("RETRIEVAL SUMMARY")
    print("=" * 60)

    print(
        summary_df[
            [
                "sensor_id",
                "location_name",
                "retrieval_status",
                "records_retrieved",
            ]
        ].to_string(index=False)
    )

    print("\nRetrieval completed.")

    print(
        "\nSensor summary saved to:"
        "\ndata/processed/feasibility/"
        "pm25_retrieval_sensor_summary.csv"
    )


if __name__ == "__main__":
    main()
