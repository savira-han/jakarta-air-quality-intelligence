# Jakarta Air Quality Intelligence

# Data Discovery Report

## 1. Discovery Overview

This report summarizes the initial data discovery outputs collected from OpenAQ and Open-Meteo. It documents the available data, its structure, and preliminary coverage before full historical ingestion and data quality assessment.

The figures in this report are generated directly from the available CSV files. Missing files or unavailable fields are not interpreted as zero or as evidence that the data does not exist.

### Location Inventory

- Rows: 30
- Columns: 10
- Duplicate rows: 0
- Missing cells: 30
- Missing-cell percentage: 10.00%

**Columns:**

`location_id`, `location_name`, `locality`, `latitude`, `longitude`, `timezone`, `provider`, `owner`, `is_mobile`, `is_monitor`

### Sensor Inventory

- Rows: 108
- Columns: 12
- Duplicate rows: 0
- Missing cells: 285
- Missing-cell percentage: 21.99%

**Columns:**

`location_id`, `location_name`, `sensor_id`, `parameter_id`, `parameter_name`, `parameter_units`, `sensor_name`, `first_observation`, `last_observation`, `percent_complete`, `observed_count`, `expected_count`

### PM2.5 History Sample

- Rows: 4,000
- Columns: 34
- Duplicate rows: 0
- Missing cells: 20,406
- Missing-cell percentage: 15.00%

**Columns:**

`sensor_id`, `location_id`, `value`, `coordinates`, `flagInfo_hasFlags`, `parameter_id`, `parameter_name`, `parameter_units`, `parameter_displayName`, `period_label`, `period_interval`, `period_datetimeFrom_utc`, `period_datetimeFrom_local`, `period_datetimeTo_utc`, `period_datetimeTo_local`, `summary_min`, `summary_q02`, `summary_q25`, `summary_median`, `summary_q75`, `summary_q98`, `summary_max`, `summary_avg`, `summary_sd`, `coverage_expectedCount`, `coverage_expectedInterval`, `coverage_observedCount`, `coverage_observedInterval`, `coverage_percentComplete`, `coverage_percentCoverage`, `coverage_datetimeFrom_utc`, `coverage_datetimeFrom_local`, `coverage_datetimeTo_utc`, `coverage_datetimeTo_local`

## 2. Location Inventory

- Total location records: 30
- Unique locations: 30

- Unique location names: 28

- Localities represented: 0
- Locality values: Not available

- Locations marked as mobile: 0

- Locations marked as monitors: 7

**Location examples:**

| location_id | location_name | locality |
| --- | --- | --- |
| 2537 | US Diplomatic Post: Jakarta South | Not available |
| 2538 | US Diplomatic Post: Jakarta Central | Not available |
| 8320 | Jakarta South | Not available |
| 8637 | Jakarta Central | Not available |
| 223262 | Cilandek | Not available |
| 223824 | Cilandek | Not available |
| 1489107 | Cipete | Not available |
| 1563313 | Qoryah Darussalam | Not available |
| 1776543 | Jihan Fauziah Hamdi  | Not available |
| 1894639 | Jakarta | Not available |

## 3. Sensor Inventory

- Total sensor records: 108
- Unique sensors: 108

- Locations represented by sensors: 30

**Sensor distribution by parameter:**

| Parameter | Sensor count |
| --- | --- |
| pm25 | 26 |
| temperature | 16 |
| pm1 | 15 |
| relativehumidity | 14 |
| um003 | 11 |
| pm10 | 9 |
| bc_370 | 5 |
| bc_880 | 5 |
| wind_direction | 3 |
| wind_speed | 3 |
| o3 | 1 |

- PM2.5 sensor records: 26

## 4. PM2.5 Historical Data Inspection

- Total observations retrieved: 4,000

- Sensors represented: 4

- Locations represented: 4

- Earliest observation: 2016-01-30 00:00:00+00:00
- Latest observation: 2023-06-17 12:00:00+00:00
- Rows with invalid timestamps: 0

**PM2.5 measurement summary:**

| Metric | Value |
| --- | --- |
| Valid measurements | 3,066 |
| Missing / invalid measurements | 934 |
| Minimum | 0.0 |
| Median | 29.0 |
| Mean | 34.240443574690154 |
| Maximum | 985.0 |

**Observations by sensor:**

| sensor_id | Observation count |
| --- | --- |
| 5047 | 1000 |
| 5048 | 1000 |
| 25072 | 1000 |
| 5077558 | 1000 |

**Interpretation note:**

This file represents a limited historical-data inspection sample. It should not be treated as the complete historical dataset or as evidence of continuous monitoring.

## 5. Weather Data Availability

No weather CSV files were found in `data/raw/open_meteo/`.

The Open-Meteo API connection test should be completed before weather data availability can be assessed.

## 6. Preliminary Data Scope Assessment

- The location inventory contains 30 location records.
- The sensor inventory contains 108 sensor records, including 26 PM2.5 sensor records.
- The PM2.5 sample contains 4,000 observations from 4 sensors.

### Preliminary interpretation

The discovery outputs establish the initial availability of monitoring locations, sensor metadata, and a sample of historical PM2.5 observations.

The final geographical scope and analysis period should not be decided from inventory counts alone. Sensor-level historical coverage, reporting continuity, missing intervals, and data quality must be examined before selecting the monitoring locations for the analytical dataset.

Weather data availability and its temporal alignment with air-quality observations must also be verified before conducting the combined analysis.
