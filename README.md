# Jakarta Air Quality Analysis

An exploratory analysis and data quality evaluation of hourly PM2.5 observations retrieved from **OpenAQ** for Jakarta and, ideally from its surrounding areas (Tangerang, Bekasi, and Bogor) for comparison, but the details will be explaine later below. 

Originally intended as a multicities, YTD comparison (January 1 - October 31, 2026), systematic data validation revealed severe coverage and reliability gaps across the region. Consequently, the project scope was narrowed to a descriptive, sensor-level study of two relatively consistent stations in Jakarta-**Lab. Lingkungan** (`17766208`) and **Lab. Lingkungan 3** (`17766346`)-during **October 1-31, 2026** (UTC+7).

---

# Background & Scope Pivot Explanation

Before conducting any statistical analysis, all retrieved OpenAQ data underwent a two-stage validation pipeline to determine whether it could support a regional air quality study.

### Stage 1: Initial Validator (Historical Availability)
The initial validator evaluated raw record counts, distinct observation dates, timestamp duplicates, and reporting intervals across all sensors returning data. Six sensors yielded historical records:

| Sensor ID | Location | Total Records | Distinct Dates | Observation Window | Max Reporting Gap |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **`17000275`** | BMKG 1 | 1,270 | 57 | Jul 22 - Oct 7, 2026 | ~337 hours (14 days) |
| **`17766208`** | **Lab. Lingkungan** | **778** | **33** | **Sep 29 - Oct 31, 2026** | **2 hours** |
| **`17766346`** | **Lab. Lingkungan 3** | **689** | **31** | **Oct 1 - Oct 31, 2026** | **8 hours** |
| **`17767065`** | Warga Sini Hobi Bakar Sampah | 455 | 20 | Oct 12 - Oct 31, 2026 | - |
| **`7748548`** | Jakarta | 193 | 95 | Nov 4, 2025 - Aug 31, 2026 | Multi-day gaps |
| **`5077558`** | Jakarta South | 99 | 5 | Nov 1 - Nov 5, 2025 | - |

### Stage 2: Full Validator (Reliability & City-Level Feasibility)
The full validator assessed 12 active PM2.5 sensors across 5 locations against strict daily reliability criteria over a **304-day window (Jan 1 - Oct 31, 2026)**:
1. **Completeness:** At least 75% of hourly readings present ($\ge 18$ of 24 hours).
2. **Range Validity:** Daily values strictly between $> 0$ and $< 500\text{ µg/m}^3$.
3. **Sensor Health:** Non-constant readings across the day (filtering out "stuck" sensors).

A sensor was deemed **USABLE** if $\ge 70\%$ of its assessed days were valid, and a city required $\ge 90\%$ valid study days (with no month below 75%) to **PASS**:

| City | Sensors Checked | Usable Sensors | Days with $\ge 1$ Valid Sensor | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| **Jakarta** | 11 | 0 | 24.3% | **FAIL** |
| **Tangerang** | 0 | 0 | 0.0% | **FAIL** |
| **Bekasi** | 0 | 0 | 0.0% | **FAIL** |
| **Bogor** | 1 | 0 | 19.7% | **FAIL** |

### Why the Scope Changed
* **Regional Comparison Infeasible:** Tangerang and Bekasi had zero PM2.5 observations during the study window, Bogor had only one highly intermittent sensor (19.7% valid days), and Jakarta achieved valid coverage on less than a quarter of study days (with at least one month having zero valid days).
* **Pivot to Focused Exploratory Study:** Because **Lab. Lingkungan (`17766208`)** and **Lab. Lingkungan 3 (`17766346`)** maintained consistent hourly logging without duplicate timestamps throughout October 2026, the analysis was scoped down to examine their October data in detail.

---

# October Air Quality Analysis - Selected Sensors (Jakarta Selatan)

## Selected Sensor Overview (October 2026)

For the October 1-31, 2026 observation window, both selected sensors captured data across all 31 calendar days, though recording continuity differed slightly:

| Metric | Lab. Lingkungan (`17766208`) | Lab. Lingkungan 3 (`17766346`) |
| :--- | :---: | :---: |
| **Observation Window** | Oct 1 - Oct 31, 2026 | Oct 1 - Oct 31, 2026 |
| **Unique Days Covered** | 31 | 31 |
| **Total Records** | 743 | 689 |
| **Median Interval** | 1.00 hour | 1.00 hour |
| **Average Interval** | 1.00 hour | 1.06 hours |
| **Maximum Gap (October)** | 1 hour | 8 hours |

* **Completeness Note:** Lab. Lingkungan logged 743 out of 744 possible hours. Lab. Lingkungan 3 recorded 54 fewer observations, with missing hours occurring mostly in the first week and final days of October.

---

## PM2.5 Distribution Summary

While both sensors recorded the majority of their readings between **40 and 80 µg/m³** (80.89% at Lab. Lingkungan; 70.39% at Lab. Lingkungan 3), Lab. Lingkungan 3 consistently recorded higher concentrations and greater spread.

### Descriptive & Percentile Statistics (µg/m³)

| Metric | Lab. Lingkungan | Lab. Lingkungan 3 |
| :--- | :---: | :---: |
| **Minimum** | 20.90 | 18.40 |
| **10th Percentile (P10)** | 44.52 | 46.08 |
| **25th Percentile (P25)** | 48.90 | 51.00 |
| **Median (P50)** | 58.60 | 64.50 |
| **Mean** | 61.23 | 67.57 |
| **75th Percentile (P75)** | 71.30 | 80.30 |
| **90th Percentile (P90)** | 84.64 | 95.52 |
| **95th Percentile (P95)** | 92.80 | 106.00 |
| **99th Percentile (P99)** | 110.00 | 131.36 |
| **Maximum** | 131.00 | 149.00 |
| **Standard Deviation** | 16.90 | 21.18 |
| **Interquartile Range (IQR)** | 22.40 | 29.30 |

### Concentration Frequency Breakdown

| Value Range (µg/m³) | Lab. Lingkungan | Lab. Lingkungan 3 |
| :--- | :---: | :---: |
| **< 20** | 0 (0.00%) | 1 (0.15%) |
| **20 - < 40** | 39 (5.25%) | 28 (4.06%) |
| **40 - < 60** | 360 (48.45%) | 273 (39.62%) |
| **60 - < 80** | 241 (32.44%) | 212 (30.77%) |
| **80 - < 100** | 83 (11.17%) | 124 (18.00%) |
| **100 - < 120** | 16 (2.15%) | 36 (5.22%) |
| **≥ 120** | 4 (0.54%) | 15 (2.18%) |

* **Upper-Tail Frequency:** Readings of **100 µg/m³ or higher** occurred nearly three times as often at Lab. Lingkungan 3 (7.40% of records) as at Lab. Lingkungan (2.69%).

---

## Temporal Trends (Daily & Diurnal)

### Daily Progression
Both sensors moved in tandem throughout October, sharing identical highest- and lowest-average dates:
* **Early October (Oct 1-14):** Moderate daily averages overall, interrupted by high intraday spikes at Lab. Lingkungan 3 on **Oct 4** (max: 143.0 µg/m³) and **Oct 7** (monthly peak: 149.0 µg/m³).
* **Mid-Month Surge (Oct 15-22):** Sustained elevated daily means across both stations, peaking on **October 17** (78.48 µg/m³ at Lab. Lingkungan; 87.30 µg/m³ at Lab. Lingkungan 3).
* **Late-Month Drop & Rebound:** Averages fell sharply during **October 24-26** (41.89-53.35 µg/m³), rebounded briefly on **October 27-28** (71.82 and 85.65 µg/m³), and settled to monthly lows on **October 31** (39.68 µg/m³ at Lab. Lingkungan; 42.73 µg/m³ at Lab. Lingkungan 3).

### Diurnal (Hourly) Cycle
Both stations exhibited a strong day-night cycle, with higher concentrations and greater standard deviations during overnight and early morning hours:
* **Early Morning Peaks:** Lab. Lingkungan 3 peaked earlier at **02:00** (mean: 80.78 µg/m³; SD: 24-31 between 01:00 and 07:00), whereas Lab. Lingkungan climbed steadily to peak at **08:00** (mean: 72.66 µg/m³).
* **Afternoon Trough:** Both sensors declined through late morning and reached their lowest hourly averages at **16:00** (49.43 µg/m³ at Lab. Lingkungan; 53.20 µg/m³ at Lab. Lingkungan 3).
* **Evening Climb:** Concentrations began rising again after 18:00, increasing more sharply at Lab. Lingkungan 3 (reaching 68.03 µg/m³ by 21:00).

---

## Elevated Observation & Episode Analysis

To evaluate high-concentration events relative to each sensor's baseline, hourly observations strictly exceeding each sensor's **90th percentile (P90)** were classified as elevated (`> 84.64 µg/m³` for Lab. Lingkungan; `> 95.52 µg/m³` for Lab. Lingkungan 3). Consecutive elevated hours without timestamp gaps were grouped into **sustained episodes** ($\ge 2$ hours), while single-hour spikes were labeled **isolated**.

### Sensor-Level Elevated Summary

| Metric | Lab. Lingkungan | Lab. Lingkungan 3 |
| :--- | :---: | :---: |
| **Elevated Threshold (P90)** | > 84.64 µg/m³ | > 95.52 µg/m³ |
| **Elevated Observations** | 75 (10.09%) | 69 (10.01%) |
| **Mean Elevated Value** | 96.19 µg/m³ | 110.68 µg/m³ |
| **Total Episodes** | 30 | 31 |
| **Sustained Episodes ($\ge 2$h)** | 22 (73.33%) | 18 (58.06%) |
| **Isolated Episodes (1h)** | 8 (26.67%) | 13 (41.94%) |
| **Longest Episode Duration** | 6 hours | 6 hours |

* **Early-Morning Clustering:** At Lab. Lingkungan, 57.34% of elevated readings occurred between **04:00 and 08:00** (peaking at 07:00). At Lab. Lingkungan 3, 60.86% occurred between **02:00 and 07:00** (peaking at 05:00-06:00).

### Simultaneous Cross-Sensor Episodes
Matching exact timestamps revealed **57 hours** where both sensors exceeded their respective P90 thresholds simultaneously, forming **23 simultaneous episodes** (16 sustained episodes totaling 50 hours, and 7 isolated 1-hour events).

| Episode Window (UTC+7) | Duration | Lab. Lingkungan Mean / Peak | Lab. Lingkungan 3 Mean / Peak |
| :--- | :---: | :---: | :---: |
| **Oct 2, 05:00 - 07:00** | 3h | 97.37 / 99.50 | 109.67 / 112.00 |
| **Oct 4, 06:00 - 07:00** | 2h | 109.45 / 120.00 | 129.00 / 143.00 |
| **Oct 5, 05:00 - 06:00** | 2h | 92.45 / 92.80 | 106.50 / 108.00 |
| **Oct 7, 04:00 - 07:00** | 4h | 100.55 / 123.00 | 115.23 / **149.00** |
| **Oct 11, 06:00 - 07:00** | 2h | 87.30 / 89.10 | 105.00 / 106.00 |
| **Oct 15, 02:00 - 04:00** | 3h | 107.00 / 110.00 | 126.33 / 135.00 |
| **Oct 16, 05:00 - 07:00** | 3h | 104.00 / 107.00 | 123.33 / 128.00 |
| **Oct 17, 01:00 - 06:00** | **6h** | 103.45 / 126.00 | 120.83 / 145.00 |
| **Oct 18, 05:00 - 07:00** | 3h | 102.27 / 109.00 | 120.33 / 130.00 |
| **Oct 20, 01:00 - 03:00** | 3h | 95.63 / 103.00 | 113.67 / 122.00 |
| **Oct 21, 01:00 - 02:00** | 2h | 88.85 / 89.50 | 99.95 / 101.00 |
| **Oct 21, 04:00 - 05:00** | 2h | 98.00 / 102.00 | 115.50 / 124.00 |
| **Oct 21, 09:00 - 11:00** | 3h | **111.40 / 131.00** | 114.33 / 131.00 |
| **Oct 22, 01:00 - 02:00** | 2h | 90.80 / 91.10 | 106.50 / 107.00 |
| **Oct 22, 07:00 - 10:00** | 4h | 99.18 / 112.00 | 104.08 / 113.00 |
| **Oct 27, 23:00 - Oct 28, 04:00** | **6h** | 94.80 / 114.00 | 111.52 / 140.00 |

*(Note: 7 isolated 1-hour simultaneous events also occurred on Oct 10 at 04:00, Oct 12 at 08:00, Oct 13 at 05:00, Oct 14 at 09:00, Oct 15 at 08:00, Oct 17 at 21:00, and Oct 30 at 03:00.)*

---

## Limitations & Future Direction

### Analytical Limitations
* **Localized & Short-Term Scope:** Findings reflect two sensors over a single month (October 2026) and do not represent city-wide air quality or seasonal trends across Jakarta.
* **Dataset-Relative Thresholds:** P90 thresholds are statistical benchmarks derived from each sensor's October distribution-they are not health-based or regulatory air quality standards.
* **No Source Attribution or Calibration Verification:** Simultaneous elevated readings show temporal alignment between the two locations, but do not establish pollution sources, wind transport, or physical causality. Hardware calibration and sensor accuracy are unverified in the raw OpenAQ feed.

### Update
This project was originally planned to have a dashboard, but due to data limitation, we will develop a sample dashboard from available data instead (which puts in less priority since the informations needed is already gathered in this document).

# The Next Project Spoiler
This analysis end up to be a background study for the next project. From this analysis, we get more understanding of a broader infrastructure challenge: **public air quality data availability and reporting continuity cannot be taken for granted**. These results motivate a dedicated **sensor reliability monitoring initiative** focused on continuously tracking uptime, completeness, stuck-sensor anomalies, and reporting gaps across regional monitoring networks.