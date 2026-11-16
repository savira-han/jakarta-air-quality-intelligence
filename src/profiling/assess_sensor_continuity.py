
import os
import time
import requests
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ============================================================
# 1. CONFIGURATION
# ============================================================

load_dotenv()

API_KEY = os.getenv("OPENAQ_API_KEY")

BASE_URL = "https://api.openaq.org/v3"

HEADERS = {
    "X-API-Key": API_KEY
}

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SENSOR_FILE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "openaq"
    / "sensor_inventory.csv"
)

RAW_OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "openaq"
    / "pm25_hours"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "feasibility"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "sensor_continuity_assessment.csv"
)

PAGE_LIMIT = 1000

# Short pause between requests to avoid unnecessarily
# sending requests in rapid succession.
REQUEST_DELAY_SECONDS = 0.2

# Safety limit against unexpected pagination behavior.
MAX_PAGES_PER_WINDOW = 10000


# ============================================================
# 2. API SESSION
# ============================================================

def create_session():
    """Create an HTTP session with retry handling."""

    session = requests.Session()

    retry_strategy = Retry(
        total=5,
        connect=5,
        read=5,
        status=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        respect_retry_after_header=True,
    )

    adapter = HTTPAdapter(
        max_retries=retry_strategy
    )

    session.mount("https://", adapter)

    session.headers.update(HEADERS)

    return session


# ============================================================
# 3. LOAD PM2.5 SENSOR INVENTORY
# ============================================================

def load_pm25_sensors():
    """Load and validate the PM2.5 sensor inventory."""

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

    sensors["normalized_parameter_name"] = (
        sensors["parameter_name"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    pm25 = sensors[
        sensors["normalized_parameter_name"] == "pm25"
    ].copy()

    if pm25.empty:
        raise ValueError(
            "No PM2.5 sensors found in sensor inventory."
        )

    pm25["sensor_id"] = pd.to_numeric(
        pm25["sensor_id"],
        errors="coerce",
    )

    pm25 = pm25.dropna(
        subset=["sensor_id"]
    )

    pm25["sensor_id"] = (
        pm25["sensor_id"].astype("int64")
    )

    if pm25["sensor_id"].duplicated().any():
        raise ValueError(
            "Duplicate PM2.5 sensor IDs found. "
            "Resolve the inventory before continuing."
        )

    pm25["first_observation"] = pd.to_datetime(
        pm25["first_observation"],
        errors="coerce",
        utc=True,
    )

    pm25["last_observation"] = pd.to_datetime(
        pm25["last_observation"],
        errors="coerce",
        utc=True,
    )

    return pm25


# ============================================================
# 4. GET SENSOR DATE RANGE
# ============================================================

def get_sensor_metadata(session, sensor_id):
    """Retrieve individual sensor metadata from OpenAQ."""

    url = f"{BASE_URL}/sensors/{sensor_id}"

    response = session.get(
        url,
        timeout=60,
    )

    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        return None

    return results[0]


def resolve_sensor_date_range(session, sensor):
    """
    Resolve the historical date range.

    Prefer the existing sensor inventory.
    If dates are missing, retrieve individual sensor metadata.
    """

    first_date = sensor["first_observation"]
    last_date = sensor["last_observation"]

    if pd.notna(first_date) and pd.notna(last_date):
        if last_date >= first_date:
            return first_date, last_date, "Inventory metadata"

    sensor_id = int(sensor["sensor_id"])

    print(
        f"  Retrieving missing date metadata "
        f"for sensor {sensor_id}"
    )

    try:
        metadata = get_sensor_metadata(
            session,
            sensor_id,
        )

        if metadata is None:
            return pd.NaT, pd.NaT, "Metadata unavailable"

        first = metadata.get("datetimeFirst") or {}
        last = metadata.get("datetimeLast") or {}

        first_date = pd.to_datetime(
            first.get("utc"),
            errors="coerce",
            utc=True,
        )

        last_date = pd.to_datetime(
            last.get("utc"),
            errors="coerce",
            utc=True,
        )

        if (
            pd.notna(first_date)
            and pd.notna(last_date)
            and last_date >= first_date
        ):
            return (
                first_date,
                last_date,
                "Sensor endpoint metadata",
            )

        return (
            pd.NaT,
            pd.NaT,
            "Metadata unavailable",
        )

    except requests.RequestException as error:

        print(
            f"  Metadata request failed: {error}"
        )

        return (
            pd.NaT,
            pd.NaT,
            "Metadata request failed",
        )


# ============================================================
# 5. GENERATE RETRIEVAL WINDOWS
# ============================================================

def generate_year_windows(first_date, last_date):
    """
    Split a historical date range into calendar-year windows.

    Each window is limited to one calendar year to avoid
    unnecessarily large API queries.
    """

    first_year = first_date.year
    last_year = last_date.year

    windows = []

    for year in range(first_year, last_year + 1):

        window_start = pd.Timestamp(
            f"{year}-01-01",
            tz="UTC",
        )

        window_end = pd.Timestamp(
            f"{year + 1}-01-01",
            tz="UTC",
        )

        # Clip the first and final windows to the
        # sensor's reported observation range.
        start = max(
            window_start,
            first_date,
        )

        end = min(
            window_end,
            last_date,
        )

        if start <= end:
            windows.append((start, end))

    return windows


# ============================================================
# 6. RETRIEVE PAGINATED HOURLY OBSERVATIONS
# ============================================================

def retrieve_hourly_window(
    session,
    sensor_id,
    start_date=None,
    end_date=None,
):
    """
    Retrieve all available hourly observations for one
    sensor and one date window.

    If dates are unavailable, retrieve without date filters.
    """

    url = f"{BASE_URL}/sensors/{sensor_id}/hours"

    all_results = []

    page = 1

    while page <= MAX_PAGES_PER_WINDOW:

        params = {
            "limit": PAGE_LIMIT,
            "page": page,
        }

        if start_date is not None:
            params["datetime_from"] = (
                start_date.isoformat()
            )

        if end_date is not None:
            params["datetime_to"] = (
                end_date.isoformat()
            )

        response = session.get(
            url,
            params=params,
            timeout=120,
        )

        response.raise_for_status()

        payload = response.json()

        results = payload.get("results", [])

        if not results:
            break

        all_results.extend(results)

        meta = payload.get("meta") or {}

        found = meta.get("found")

        print(
            f"    Page {page}: "
            f"{len(results)} observations"
        )

        # If the API provides a total result count,
        # use it to determine whether more pages remain.
        if found is not None:

            try:
                total_pages = (
                    int(found) + PAGE_LIMIT - 1
                ) // PAGE_LIMIT

                if page >= total_pages:
                    break

            except (TypeError, ValueError):
                pass

        # Fallback when total result count is unavailable.
        elif len(results) < PAGE_LIMIT:
            break

        page += 1

        time.sleep(REQUEST_DELAY_SECONDS)

    else:
        raise RuntimeError(
            f"Pagination safety limit reached "
            f"for sensor {sensor_id}"
        )

    return all_results


# ============================================================
# 7. RETRIEVE ALL SENSOR OBSERVATIONS
# ============================================================

def retrieve_sensor_observations(
    session,
    sensor,
):
    """Retrieve historical hourly observations for one sensor."""

    sensor_id = int(sensor["sensor_id"])

    location_id = sensor["location_id"]

    location_name = sensor["location_name"]

    print("\n" + "-" * 65)

    print(
        f"Sensor: {sensor_id} | "
        f"Location: {location_name}"
    )

    first_date, last_date, date_source = (
        resolve_sensor_date_range(
            session,
            sensor,
        )
    )

    print(f"Date source: {date_source}")

    all_results = []

    if pd.notna(first_date) and pd.notna(last_date):

        windows = generate_year_windows(
            first_date,
            last_date,
        )

        print(
            f"Retrieval windows: {len(windows)}"
        )

        for start_date, end_date in windows:

            print(
                f"  Retrieving "
                f"{start_date.date()} to "
                f"{end_date.date()}"
            )

            results = retrieve_hourly_window(
                session,
                sensor_id,
                start_date,
                end_date,
            )

            all_results.extend(results)

            time.sleep(REQUEST_DELAY_SECONDS)

    else:

        # No reliable date range is available.
        # Attempt a paginated retrieval without date filters.
        print(
            "  No usable date range. "
            "Attempting unbounded paginated retrieval."
        )

        all_results = retrieve_hourly_window(
            session,
            sensor_id,
        )

    if not all_results:
        return pd.DataFrame(), date_source

    # Preserve the API fields as flattened columns.
    observations = pd.json_normalize(
        all_results,
        sep="_",
    )

    observations["sensor_id"] = sensor_id

    observations["location_id"] = location_id

    observations["location_name"] = location_name

    observations["inventory_first_observation"] = (
        sensor["first_observation"]
    )

    observations["inventory_last_observation"] = (
        sensor["last_observation"]
    )

    observations["date_metadata_source"] = date_source

    return observations, date_source


# ============================================================
# 8. SAVE RAW SENSOR OBSERVATIONS
# ============================================================

def save_sensor_observations(
    observations,
    sensor_id,
):
    """Save retrieved observations for one sensor."""

    RAW_OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        RAW_OUTPUT_DIR
        / f"sensor_{sensor_id}.csv"
    )

    observations.to_csv(
        output_file,
        index=False,
    )

    print(
        f"  Saved {len(observations)} records: "
        f"{output_file}"
    )


# ============================================================
# 9. PREPARE TIMESTAMP DATA
# ============================================================

def prepare_timestamps(observations):
    """
    Prepare a consistent timestamp column.

    Prefer period.datetimeTo.utc because OpenAQ timestamps
    represent the end of the measurement period.

    Fall back to period.datetimeFrom.utc when unavailable.
    """

    observations = observations.copy()

    if "period_datetimeTo_utc" not in observations.columns:
        observations["period_datetimeTo_utc"] = pd.NA

    if "period_datetimeFrom_utc" not in observations.columns:
        observations["period_datetimeFrom_utc"] = pd.NA

    observations["observation_timestamp"] = (
        observations["period_datetimeTo_utc"]
        .combine_first(
            observations["period_datetimeFrom_utc"]
        )
    )

    observations["observation_timestamp"] = (
        pd.to_datetime(
            observations["observation_timestamp"],
            errors="coerce",
            utc=True,
        )
    )

    return observations


# ============================================================
# 10. ANALYZE REPORTING CONTINUITY
# ============================================================

def analyze_continuity(observations):
    """
    Analyze actual observation timestamps.

    Cadence is inferred from the most frequent positive
    interval between unique consecutive timestamps.
    """

    observations = prepare_timestamps(
        observations
    )

    total_records = len(observations)

    valid_timestamps = observations[
        observations["observation_timestamp"].notna()
    ].copy()

    invalid_timestamp_count = (
        total_records - len(valid_timestamps)
    )

    if valid_timestamps.empty:

        return {
            "total_api_records": total_records,
            "valid_timestamp_count": 0,
            "invalid_timestamp_count": invalid_timestamp_count,
            "unique_timestamp_count": 0,
            "duplicate_timestamp_count": 0,
            "first_retrieved_observation": pd.NaT,
            "last_retrieved_observation": pd.NaT,
            "retrieved_span_days": None,
            "observed_calendar_days": 0,
            "calendar_days_in_span": 0,
            "calendar_days_without_observation": 0,
            "modal_interval_minutes": None,
            "median_interval_minutes": None,
            "max_gap_hours": None,
            "gap_count_over_1_5x_modal_interval": None,
            "estimated_missing_intervals": None,
            "regular_interval_share_pct": None,
            "null_value_count": None,
            "flagged_observation_count": None,
        }

    # Count duplicate timestamps before deduplication.
    duplicate_count = (
        valid_timestamps["observation_timestamp"]
        .duplicated()
        .sum()
    )

    # One timestamp should represent one hourly observation
    # for this sensor. Keep the first occurrence for interval
    # analysis, but preserve all records in the raw CSV.
    unique_observations = (
        valid_timestamps
        .drop_duplicates(
            subset=["observation_timestamp"]
        )
        .sort_values("observation_timestamp")
    )

    timestamps = (
        unique_observations["observation_timestamp"]
    )

    first_timestamp = timestamps.min()

    last_timestamp = timestamps.max()

    retrieved_span_days = (
        last_timestamp - first_timestamp
    ).total_seconds() / 86400

    # Calculate intervals between consecutive observations.
    intervals = (
        timestamps.diff()
        .dropna()
        .dt.total_seconds()
        .div(60)
    )

    intervals = intervals[
        intervals > 0
    ]

    if intervals.empty:

        modal_interval = None
        median_interval = None
        max_gap_hours = None
        gap_count = None
        estimated_missing_intervals = None
        regular_interval_share = None

    else:

        # Round to the nearest minute before finding
        # the most frequent observed interval.
        rounded_intervals = (
            intervals.round().astype("int64")
        )

        interval_counts = (
            rounded_intervals.value_counts()
        )

        modal_interval = int(
            interval_counts.index[0]
        )

        median_interval = float(
            intervals.median()
        )

        max_gap_hours = (
            intervals.max() / 60
        )

        # A gap is flagged when it exceeds 1.5 times
        # the inferred modal interval.
        gap_threshold = modal_interval * 1.5

        gap_mask = (
            intervals > gap_threshold
        )

        gap_count = int(
            gap_mask.sum()
        )

        # Estimate missing intervals relative to the
        # inferred cadence. This is an estimate, not a
        # verified count of missing measurements.
        estimated_missing_intervals = int(
            (
                intervals[gap_mask] / modal_interval
            ).round().sub(1).clip(lower=0).sum()
        )

        regular_interval_share = (
            (~gap_mask).sum()
            / len(intervals)
            * 100
        )

    # Calendar-day coverage is descriptive only.
    # It does not establish expected daily reporting.
    observed_calendar_days = (
        timestamps.dt.floor("D").nunique()
    )

    calendar_days_in_span = (
        (last_timestamp.normalize()
         - first_timestamp.normalize()).days
        + 1
    )

    calendar_days_without_observation = (
        calendar_days_in_span
        - observed_calendar_days
    )

    # These fields are supplementary indicators.
    null_value_count = None

    if "value" in valid_timestamps.columns:
        null_value_count = int(
            valid_timestamps["value"].isna().sum()
        )

    flagged_observation_count = None

    if "flagInfo_hasFlags" in valid_timestamps.columns:
        flagged_observation_count = int(
            valid_timestamps["flagInfo_hasFlags"]
            .fillna(False)
            .astype(bool)
            .sum()
        )

    return {
        "total_api_records": total_records,
        "valid_timestamp_count": len(valid_timestamps),
        "invalid_timestamp_count": invalid_timestamp_count,
        "unique_timestamp_count": len(unique_observations),
        "duplicate_timestamp_count": int(duplicate_count),
        "first_retrieved_observation": first_timestamp,
        "last_retrieved_observation": last_timestamp,
        "retrieved_span_days": retrieved_span_days,
        "observed_calendar_days": observed_calendar_days,
        "calendar_days_in_span": calendar_days_in_span,
        "calendar_days_without_observation": calendar_days_without_observation,
        "modal_interval_minutes": modal_interval,
        "median_interval_minutes": median_interval,
        "max_gap_hours": max_gap_hours,
        "gap_count_over_1_5x_modal_interval": gap_count,
        "estimated_missing_intervals": estimated_missing_intervals,
        "regular_interval_share_pct": regular_interval_share,
        "null_value_count": null_value_count,
        "flagged_observation_count": flagged_observation_count,
    }


# ============================================================
# 11. BUILD SENSOR ASSESSMENT
# ============================================================

def build_sensor_assessment(
    sensor,
    observations,
    date_source,
    retrieval_status,
    retrieval_error=None,
):
    """Build one continuity assessment record."""

    sensor_id = int(sensor["sensor_id"])

    assessment = {
        "location_id": sensor["location_id"],
        "location_name": sensor["location_name"],
        "sensor_id": sensor_id,
        "parameter_units": sensor["parameter_units"],
        "inventory_first_observation": sensor["first_observation"],
        "inventory_last_observation": sensor["last_observation"],
        "date_metadata_source": date_source,
        "retrieval_status": retrieval_status,
        "retrieval_error": retrieval_error,
    }

    if observations.empty:

        metrics = analyze_continuity(
            pd.DataFrame()
        )

    else:

        metrics = analyze_continuity(
            observations
        )

    assessment.update(metrics)

    # Compare actual retrieved boundaries with inventory
    # boundaries when both are available.
    actual_first = metrics[
        "first_retrieved_observation"
    ]

    actual_last = metrics[
        "last_retrieved_observation"
    ]

    inventory_first = sensor["first_observation"]

    inventory_last = sensor["last_observation"]

    assessment["first_date_matches_inventory"] = (
        actual_first == inventory_first
        if pd.notna(actual_first)
        and pd.notna(inventory_first)
        else None
    )

    assessment["last_date_matches_inventory"] = (
        actual_last == inventory_last
        if pd.notna(actual_last)
        and pd.notna(inventory_last)
        else None
    )

    return assessment


# ============================================================
# 12. GENERATE ASSESSMENT NOTES
# ============================================================

def generate_assessment_notes(assessment):
    """Generate descriptive notes for manual review."""

    notes = []

    if assessment["retrieval_status"] != "Success":
        notes.append(
            "Observation retrieval unsuccessful"
        )

    if assessment["valid_timestamp_count"] == 0:
        notes.append(
            "No valid observation timestamps retrieved"
        )

    if assessment["duplicate_timestamp_count"] > 0:
        notes.append(
            "Duplicate observation timestamps found"
        )

    if assessment["invalid_timestamp_count"] > 0:
        notes.append(
            "Records with invalid timestamps found"
        )

    if (
        assessment["gap_count_over_1_5x_modal_interval"]
        is not None
        and assessment["gap_count_over_1_5x_modal_interval"] > 0
    ):
        notes.append(
            "Intervals longer than inferred cadence found"
        )

    if assessment["date_metadata_source"] == "Metadata unavailable":
        notes.append(
            "Sensor date metadata unavailable"
        )

    if (
        assessment["first_date_matches_inventory"] is False
        or assessment["last_date_matches_inventory"] is False
    ):
        notes.append(
            "Retrieved date boundaries differ from inventory"
        )

    if not notes:
        notes.append(
            "No initial timestamp continuity issue identified"
        )

    return "; ".join(notes)


# ============================================================
# 13. SAVE CONSOLIDATED ASSESSMENT
# ============================================================

def save_assessment(assessment_records):
    """Save the consolidated continuity assessment."""

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    assessment = pd.DataFrame(
        assessment_records
    )

    assessment.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print("\nContinuity assessment saved:")
    print(OUTPUT_FILE)

    return assessment


# ============================================================
# 14. PRINT ASSESSMENT SUMMARY
# ============================================================

def print_summary(assessment):
    """Print a high-level summary of continuity results."""

    print("\n" + "=" * 65)
    print("PM2.5 SENSOR CONTINUITY ASSESSMENT")
    print("=" * 65)

    print(
        f"Total PM2.5 sensors: {len(assessment)}"
    )

    print(
        "Successful retrievals:",
        (assessment["retrieval_status"] == "Success").sum(),
    )

    print(
        "Sensors with valid timestamps:",
        (assessment["valid_timestamp_count"] > 0).sum(),
    )

    print(
        "Sensors with duplicate timestamps:",
        (assessment["duplicate_timestamp_count"] > 0).sum(),
    )

    print(
        "Sensors with detected reporting gaps:",
        (
            assessment[
                "gap_count_over_1_5x_modal_interval"
            ].fillna(0) > 0
        ).sum(),
    )

    print("\nRetrieval status:")

    print(
        assessment["retrieval_status"]
        .value_counts(dropna=False)
        .to_string()
    )

    print("\nSensor comparison:")

    display_columns = [
        "sensor_id",
        "location_name",
        "total_api_records",
        "unique_timestamp_count",
        "first_retrieved_observation",
        "last_retrieved_observation",
        "modal_interval_minutes",
        "max_gap_hours",
        "gap_count_over_1_5x_modal_interval",
        "estimated_missing_intervals",
        "assessment_notes",
    ]

    print(
        assessment[display_columns]
        .to_string(index=False)
    )


# ============================================================
# 15. MAIN EXECUTION
# ============================================================

def main():

    if not API_KEY:
        raise ValueError(
            "OPENAQ_API_KEY not found. "
            "Check your .env configuration."
        )

    print(
        "Starting PM2.5 sensor continuity assessment..."
    )

    sensors = load_pm25_sensors()

    print(
        f"\nPM2.5 sensors to assess: {len(sensors)}"
    )

    session = create_session()

    assessment_records = []

    for _, sensor in sensors.iterrows():

        sensor_id = int(sensor["sensor_id"])

        try:

            observations, date_source = (
                retrieve_sensor_observations(
                    session,
                    sensor,
                )
            )

            if not observations.empty:

                save_sensor_observations(
                    observations,
                    sensor_id,
                )

            retrieval_status = "Success"

            retrieval_error = None

        except Exception as error:

            print(
                f"\nERROR retrieving sensor {sensor_id}: "
                f"{error}"
            )

            observations = pd.DataFrame()

            date_source = "Retrieval failed"

            retrieval_status = "Failed"

            retrieval_error = str(error)

        assessment = build_sensor_assessment(
            sensor,
            observations,
            date_source,
            retrieval_status,
            retrieval_error,
        )

        assessment["assessment_notes"] = (
            generate_assessment_notes(
                assessment
            )
        )

        assessment_records.append(assessment)

    session.close()

    final_assessment = save_assessment(
        assessment_records
    )

    print_summary(final_assessment)

    print(
        "\nSensor continuity assessment completed."
    )


if __name__ == "__main__":
    main()
