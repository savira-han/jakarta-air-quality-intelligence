"""
Check if OpenAQ has usable PM2.5 data for Jakarta, Tangerang, Bekasi and Bogor
between 2026-01-01 and 2026-10-31.

Run it first, before downloading the hourly data.

Setup:
    pip install requests pandas
    set the key:  export OPENAQ_API_KEY="your key"
    python openaq_pm25_check_simple.py
"""

import calendar
import math
import os
import sys
import time
from datetime import date, timedelta

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()


# ---------- settings ----------

API_KEY = os.getenv("OPENAQ_API_KEY")

BASE_URL = "https://api.openaq.org/v3"

HEADERS = {
    "X-API-Key": API_KEY
}

PM25_ID = 2

START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 10, 31)

# city centre and search radius in metres (the API max is 25000)
cities = {
    "Jakarta": {"lat": -6.2088, "lon": 106.8456, "radius": 15000},
    "Tangerang": {"lat": -6.1783, "lon": 106.6319, "radius": 12000},
    "Bekasi": {"lat": -6.2383, "lon": 106.9756, "radius": 12000},
    "Bogor": {"lat": -6.5950, "lon": 106.8166, "radius": 12000},
}

# quality rules
MIN_DAILY_COMPLETENESS = 75    # % of hourly readings needed for a day to count
MAX_DAILY_PM25 = 500           # daily average above this is treated as an error
MIN_SENSOR_COVERAGE = 70       # % of valid days for a sensor to be "usable"
CITY_PASS = 90                 # % of days covered for a PASS
CITY_PARTIAL = 60              # % of days covered for a PARTIAL
MIN_MONTH_COVERAGE = 75        # worst month must reach this for a PASS
MIN_CORRELATION = 0.6          # sensors in the same city should roughly agree

OUTPUT_FOLDER = "openaq_check_output"

all_days = pd.date_range(START_DATE, END_DATE, freq="D")
headers = {"X-API-Key": API_KEY}


# ---------- API helpers ----------

def call_api(path, params):
    """Call the OpenAQ API and return the json. Waits and retries if needed."""
    url = BASE_URL + path

    for attempt in range(5):
        response = requests.get(url, headers=headers, params=params, timeout=60)

        if response.status_code == 200:
            time.sleep(1.1)  # stay under the rate limit (about 60 calls/min)
            return response.json()

        if response.status_code in (401, 403):
            sys.exit("API key was rejected. Check your OPENAQ_API_KEY.")

        if response.status_code == 429:
            print("  rate limit hit, waiting 30 seconds...")
            time.sleep(30)
        else:
            print("  got status", response.status_code, "- trying again in 5 seconds")
            time.sleep(5)

    sys.exit("Failed to get data from " + url)


def get_all_results(path, params):
    """Go through all pages of a list endpoint."""
    results = []
    page = 1

    while True:
        params["limit"] = 1000
        params["page"] = page
        data = call_api(path, params)
        rows = data.get("results", [])
        results = results + rows

        if len(rows) < 1000:
            break
        page = page + 1

    return results


def distance_km(lat1, lon1, lat2, lon2):
    """Straight line distance between two points (haversine)."""
    radius_earth = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    return 2 * radius_earth * math.asin(math.sqrt(a))


# ---------- step 1: find locations ----------

def find_locations():
    """Search around each city. If a location shows up for 2 cities, keep the closer one."""
    found = {}

    for city_name, city in cities.items():
        print("Searching PM2.5 locations near", city_name, "...")

        params = {
            "coordinates": str(city["lat"]) + "," + str(city["lon"]),
            "radius": city["radius"],
            "parameters_id": PM25_ID,
        }
        results = get_all_results("/locations", params)

        count = 0
        for loc in results:
            if loc.get("isMobile"):
                continue  # skip mobile sensors

            coords = loc.get("coordinates") or {}
            lat = coords.get("latitude")
            lon = coords.get("longitude")
            if lat is None or lon is None:
                continue

            dist = distance_km(city["lat"], city["lon"], lat, lon)
            if dist > city["radius"] / 1000 * 1.05:
                continue  # outside the radius, ignore

            count = count + 1
            loc_id = loc["id"]
            if loc_id not in found or dist < found[loc_id]["distance"]:
                found[loc_id] = {"city": city_name, "distance": round(dist, 2), "info": loc}

        print("  found", count, "fixed locations")

    return found


def get_utc(date_obj):
    """OpenAQ dates look like {'utc': '...', 'local': '...'}. Return the utc part."""
    if date_obj is None:
        return None
    return date_obj.get("utc")


def is_pm25_sensor(sensor):
    parameter = sensor.get("parameter") or {}
    return parameter.get("id") == PM25_ID or parameter.get("name") == "pm25"


def make_inventory(found):
    """Table of all the locations we found."""
    rows = []

    for loc_id, item in found.items():
        loc = item["info"]
        first = get_utc(loc.get("datetimeFirst"))
        last = get_utc(loc.get("datetimeLast"))

        overlaps = False
        if first and last:
            if first[:10] <= str(END_DATE) and last[:10] >= str(START_DATE):
                overlaps = True

        sensor_ids = []
        for sensor in loc.get("sensors") or []:
            if is_pm25_sensor(sensor):
                sensor_ids.append(str(sensor["id"]))

        if loc.get("isMonitor"):
            station_type = "reference monitor"
        else:
            station_type = "low-cost sensor"

        provider = loc.get("provider") or {}
        coords = loc.get("coordinates") or {}

        rows.append({
            "city": item["city"],
            "distance_to_centre_km": item["distance"],
            "location_id": loc_id,
            "name": loc.get("name"),
            "locality": loc.get("locality"),
            "provider": provider.get("name"),
            "station_type": station_type,
            "latitude": coords.get("latitude"),
            "longitude": coords.get("longitude"),
            "first_data_utc": first,
            "last_data_utc": last,
            "overlaps_period": overlaps,
            "pm25_sensor_ids": ",".join(sensor_ids),
        })

    return pd.DataFrame(rows)


# ---------- step 2: daily data per sensor ----------

def get_daily_data(sensor_id):
    """Daily PM2.5 for one sensor. Only 1 API call, much lighter than hourly data."""
    params = {
        "datetime_from": str(START_DATE) + "T00:00:00Z",
        "datetime_to": str(END_DATE + timedelta(days=1)) + "T00:00:00Z",
    }
    results = get_all_results("/sensors/" + str(sensor_id) + "/days", params)

    rows = []
    for r in results:
        period = r.get("period") or {}
        date_from = period.get("datetimeFrom") or {}
        day = (date_from.get("local") or "")[:10]
        if day == "":
            continue

        coverage = r.get("coverage") or {}
        expected = coverage.get("expectedCount")
        observed = coverage.get("observedCount")
        completeness = coverage.get("percentComplete")
        if completeness is None and expected:
            completeness = 100 * (observed or 0) / expected

        summary = r.get("summary") or {}

        rows.append({
            "day": pd.Timestamp(day),
            "value": r.get("value"),
            "completeness": completeness,
            "observed": observed,
            "sd": summary.get("sd"),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df = df.drop_duplicates("day")
    df = df.set_index("day")
    df = df[(df.index >= pd.Timestamp(START_DATE)) & (df.index <= pd.Timestamp(END_DATE))]
    return df


def longest_gap(valid_days):
    """Longest run of days in a row without a valid reading."""
    longest = 0
    current = 0
    for is_valid in valid_days:
        if is_valid:
            current = 0
        else:
            current = current + 1
            if current > longest:
                longest = current
    return longest


def check_sensor(daily):
    """Score one sensor. Returns the stats, a True/False series of valid days, and the values."""
    total_days = len(all_days)

    # sensor has no data at all in the period
    if daily.empty:
        stats = {
            "days_with_data": 0,
            "valid_days": 0,
            "valid_day_pct": 0.0,
            "avg_completeness_pct": None,
            "longest_gap_days": total_days,
            "days_low_completeness": 0,
            "days_zero_or_negative": 0,
            "days_too_high": 0,
            "days_flatline": 0,
            "mean_pm25": None,
            "p95_pm25": None,
        }
        no_valid = pd.Series(False, index=all_days)
        no_values = pd.Series(float("nan"), index=all_days)
        return stats, no_valid, no_values

    # make sure every day of the period is in the table
    daily = daily.reindex(all_days)

    has_data = daily["value"].notna()
    low_completeness = has_data & (daily["completeness"].fillna(0) < MIN_DAILY_COMPLETENESS)
    zero_or_negative = has_data & (daily["value"] <= 0)
    too_high = has_data & (daily["value"] > MAX_DAILY_PM25)
    # sd of 0 means the sensor gave the same number all day (probably stuck)
    flatline = has_data & (daily["sd"].fillna(1) == 0) & (daily["observed"].fillna(0) >= 12)

    valid = has_data & ~low_completeness & ~zero_or_negative & ~too_high & ~flatline
    values = daily["value"].where(valid)

    good_values = values.dropna()
    if len(good_values) > 0:
        mean_pm25 = round(good_values.mean(), 1)
        p95_pm25 = round(good_values.quantile(0.95), 1)
    else:
        mean_pm25 = None
        p95_pm25 = None

    stats = {
        "days_with_data": int(has_data.sum()),
        "valid_days": int(valid.sum()),
        "valid_day_pct": round(100 * valid.sum() / total_days, 1),
        "avg_completeness_pct": round(daily.loc[has_data, "completeness"].mean(), 1),
        "longest_gap_days": longest_gap(valid),
        "days_low_completeness": int(low_completeness.sum()),
        "days_zero_or_negative": int(zero_or_negative.sum()),
        "days_too_high": int(too_high.sum()),
        "days_flatline": int(flatline.sum()),
        "mean_pm25": mean_pm25,
        "p95_pm25": p95_pm25,
    }
    return stats, valid, values


# ---------- step 3: check each city ----------

def average_correlation(values_table, sensor_ids):
    """Average correlation between the sensors of one city (needs 2 or more)."""
    if len(sensor_ids) < 2:
        return None

    corr_table = values_table[sensor_ids].corr(min_periods=30)

    total = 0
    count = 0
    for i in range(len(sensor_ids)):
        for j in range(i + 1, len(sensor_ids)):
            c = corr_table.iloc[i, j]
            if not pd.isna(c):
                total = total + c
                count = count + 1

    if count == 0:
        return None
    return total / count


def check_city(city_name, sensor_rows, valid_table, values_table):
    """Give a PASS / PARTIAL / FAIL for one city. Returns (summary, monthly table)."""
    if len(sensor_rows) == 0:
        summary = {
            "city": city_name,
            "verdict": "FAIL",
            "sensors_checked": 0,
            "usable_sensors": 0,
            "usable_locations": 0,
            "day_coverage_pct": 0.0,
            "worst_month_pct": 0.0,
            "median_sensors_per_day": 0,
            "avg_correlation": None,
            "notes": "no PM2.5 sensor with data in the period",
        }
        return summary, pd.DataFrame()

    sensors = pd.DataFrame(sensor_rows)
    usable = sensors[sensors["usable"]]

    # a day is covered if at least one sensor has a valid reading
    day_covered = valid_table.any(axis=1)
    day_coverage = 100 * day_covered.mean()

    # coverage per month
    monthly = day_covered.groupby(day_covered.index.month).mean() * 100
    worst_month = monthly.min()
    worst_month_name = calendar.month_abbr[monthly.idxmin()]

    sensors_per_day = valid_table.sum(axis=1)
    correlation = average_correlation(values_table, list(usable["sensor_id"]))
    usable_locations = usable["location_id"].nunique()

    # verdict
    if len(usable) == 0:
        verdict = "FAIL"
    elif day_coverage >= CITY_PASS and worst_month >= MIN_MONTH_COVERAGE:
        verdict = "PASS"
    elif day_coverage >= CITY_PARTIAL:
        verdict = "PARTIAL"
    else:
        verdict = "FAIL"

    # notes about reliability
    notes = []
    if len(usable) == 0:
        notes.append("no sensor reaches the coverage limit")
    if len(usable) > 0 and usable_locations == 1:
        notes.append("only 1 usable location, weak representation of the city")
    if len(usable) > 0 and "reference monitor" not in list(usable["station_type"]):
        notes.append("no reference monitor, only low-cost sensors")
    if correlation is not None and correlation < MIN_CORRELATION:
        notes.append("sensors disagree with each other (corr " + str(round(correlation, 2)) + ")")
    if worst_month < MIN_MONTH_COVERAGE:
        notes.append("weak month: " + worst_month_name + " (" + str(round(worst_month)) + "%)")
    if (sensors["days_flatline"] > 5).any() or (sensors["days_too_high"] > 5).any():
        notes.append("some sensors have many flatline or extreme days")
    for unit in sensors["units"].dropna().unique():
        if "g/m" not in unit:
            notes.append("unit is " + unit + ", not ug/m3")

    if correlation is not None:
        correlation = round(correlation, 2)

    summary = {
        "city": city_name,
        "verdict": verdict,
        "sensors_checked": len(sensors),
        "usable_sensors": len(usable),
        "usable_locations": usable_locations,
        "day_coverage_pct": round(day_coverage, 1),
        "worst_month_pct": round(worst_month, 1),
        "median_sensors_per_day": float(sensors_per_day.median()),
        "avg_correlation": correlation,
        "notes": "; ".join(notes),
    }

    monthly_table = pd.DataFrame({
        "city": city_name,
        "month": [calendar.month_abbr[m] for m in monthly.index],
        "day_coverage_pct": monthly.round(1).values,
    })

    return summary, monthly_table


# ---------- main ----------

def main():
    if not API_KEY:
        sys.exit("Please set OPENAQ_API_KEY first (free key at https://explore.openaq.org/register)")

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # 1. find the locations
    found = find_locations()
    if len(found) == 0:
        sys.exit("No PM2.5 locations found. Try a bigger radius.")

    inventory = make_inventory(found)
    inventory = inventory.sort_values(["city", "distance_to_centre_km"])
    inventory.to_csv(OUTPUT_FOLDER + "/locations_inventory.csv", index=False)
    print()
    print(len(inventory), "locations found,", int(inventory["overlaps_period"].sum()),
          "have data in the period")

    # 2. list the sensors we need to check
    sensor_list = []
    for loc_id, item in found.items():
        loc = item["info"]
        first = get_utc(loc.get("datetimeFirst"))
        last = get_utc(loc.get("datetimeLast"))

        # skip locations that stopped before or started after our period
        if first and last:
            if last[:10] < str(START_DATE) or first[:10] > str(END_DATE):
                continue

        for sensor in loc.get("sensors") or []:
            if is_pm25_sensor(sensor):
                sensor_list.append((item["city"], loc, sensor))

    print("Checking", len(sensor_list), "PM2.5 sensors...")
    print()

    # 3. get and score the daily data of each sensor
    sensor_rows = {}
    valid_tables = {}
    value_tables = {}
    for city_name in cities:
        sensor_rows[city_name] = []
        valid_tables[city_name] = {}
        value_tables[city_name] = {}

    number = 0
    for city_name, loc, sensor in sensor_list:
        number = number + 1
        sensor_id = sensor["id"]
        print("[" + str(number) + "/" + str(len(sensor_list)) + "]", city_name, "-",
              loc.get("name"), "(sensor " + str(sensor_id) + ")")

        daily = get_daily_data(sensor_id)
        stats, valid, values = check_sensor(daily)

        if loc.get("isMonitor"):
            station_type = "reference monitor"
        else:
            station_type = "low-cost sensor"

        row = {
            "city": city_name,
            "location_id": loc["id"],
            "location_name": loc.get("name"),
            "sensor_id": sensor_id,
            "provider": (loc.get("provider") or {}).get("name"),
            "station_type": station_type,
            "units": (sensor.get("parameter") or {}).get("units"),
        }
        row.update(stats)
        row["usable"] = stats["valid_day_pct"] >= MIN_SENSOR_COVERAGE

        sensor_rows[city_name].append(row)
        valid_tables[city_name][sensor_id] = valid
        value_tables[city_name][sensor_id] = values

    # 4. check each city
    summaries = []
    monthly_tables = []
    for city_name in cities:
        valid_table = pd.DataFrame(valid_tables[city_name])
        values_table = pd.DataFrame(value_tables[city_name])
        summary, monthly_table = check_city(city_name, sensor_rows[city_name],
                                            valid_table, values_table)
        summaries.append(summary)
        if not monthly_table.empty:
            monthly_tables.append(monthly_table)

    # 5. save the results
    all_sensor_rows = []
    for city_name in cities:
        all_sensor_rows = all_sensor_rows + sensor_rows[city_name]

    if len(all_sensor_rows) > 0:
        sensor_table = pd.DataFrame(all_sensor_rows)
        sensor_table = sensor_table.sort_values(["city", "valid_day_pct"], ascending=[True, False])
        sensor_table.to_csv(OUTPUT_FOLDER + "/sensor_quality_summary.csv", index=False)

    pd.DataFrame(summaries).to_csv(OUTPUT_FOLDER + "/city_verdict.csv", index=False)

    if len(monthly_tables) > 0:
        pd.concat(monthly_tables).to_csv(OUTPUT_FOLDER + "/city_monthly_coverage.csv", index=False)

    # 6. print the report
    print()
    print("PM2.5 data check:", START_DATE, "to", END_DATE, "(" + str(len(all_days)) + " days)")
    print("-" * 60)

    for s in summaries:
        print()
        print(s["city"].upper(), "->", s["verdict"])
        print("  usable sensors / locations:", s["usable_sensors"], "/", s["usable_locations"],
              "(checked", s["sensors_checked"], "sensors)")
        print("  days with at least 1 valid sensor:", s["day_coverage_pct"], "%",
              "(worst month:", s["worst_month_pct"], "%)")
        print("  median sensors reporting per day:", s["median_sensors_per_day"])
        print("  average correlation between sensors:", s["avg_correlation"])
        if s["notes"] != "":
            print("  notes:", s["notes"])

    print()
    print("Files saved in the folder:", OUTPUT_FOLDER)
    print("PASS = ok for hourly download, PARTIAL = has gaps, FAIL = not enough data")


if __name__ == "__main__":
    main()