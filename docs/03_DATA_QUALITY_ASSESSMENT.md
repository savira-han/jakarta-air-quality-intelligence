# Data Quality Assessment

## 1. Overview

After retrieving PM2.5 data from OpenAQ, 2 (two) validation processes were done to check whether the available data could support the planned air quality analysis.

1. **Initial validator**, checked the historical availability of sensor data, the number of observations and the time gaps between records.

2. **Full validator**, checked daily data completeness, measurement validity, reporting gaps and overall sensor reliability.

Purpose: understand the available data quality, whther can support a PM2.5 analysis across Jakarta and the surrounding areas: Tangerang, Bekasi and Bogor.

## 2. Initial Validator: Historical Data Availability

The initial validator checked the observation history of each sensor. It checked the number of records, distinct observation dates, observation period, time gaps between records and duplicate timestamps.

Six sensors returned observations during the retrieval process.

| Sensor | Location | Records | Distinct dates | Observation period |
|---|---|---:|---:|---|
| 17000275 | BMKG 1 | 1,270 | 57 | 22 Jul - 7 Oct 2026 |
| 17766208 | Lab. Lingkungan | 778 | 33 | 29 Sep - 31 Oct 2026 |
| 17766346 | Lab. Lingkungan 3 | 689 | 31 | 1 Oct - 31 Oct 2026 |
| 17767065 | Warga Sini Hobi Bakar Sampah | 455 | 20 | 12 Oct - 31 Oct 2026 |
| 7748548 | Jakarta | 193 | 95 | 4 Nov 2025 - 31 Aug 2026 |
| 5077558 | Jakarta South | 99 | 5 | 1 Nov - 5 Nov 2025 |

### Findings

**Lab. Lingkungan (sensor 17766208)** had the most consistent time intervals.

- 778 records across 33 distinct dates.
- avg interval between observations approx one hour.
- the longest interval was 2 hours.
- no duplicate timestamps or missing timestamps.

**Lab. Lingkungan 3 (sensor 17766346)** also relatively consistent.

- 689 records across 31 distinct dates.
- avg interval approx one hour.
- the longest interval between consecutive observations was eight hours.
- no duplicate timestamps or missing timestamps.

**BMKG 1 (sensor 17000275)** = highest number of records, but less consistent.

- 1,270 records across 57 distinct dates.
- avg interval approx 1.46 hrs.
- the longest interval between consecutive observations was 337 hours, or approx 14 days.

Other sensors had more limited data. Jakarta South only had observations across 5 dates, while the Jakarta sensor had long gaps between observations.

### Initial assessment

Sensors that might be suitable for further analysis:

Lab. Lingkungan and Lab. Lingkungan 3 appeared to be the strongest candidates because their observations had relatively consistent hourly intervals during October. However, consistent reporting intervals do not automatically mean that the data is complete or reliable. A sensor may report regularly but still have too few observations within a day, invalid measurements or repeated values. For this reason, a more detailed validation was needed.

## 3. Full Validator: Data Reliability and Feasibility

The full validator checked whether the available observations were reliable enough for daily air quality analysis. The assessment timeframe: 1 January to 31 October 2026 (total 304 days).

### 3.1 Data availability

The location search identified:

- 20 fixed monitoring locations.
- 5 locations with historical data overlapping the assessment period.
- 12 PM2.5 sensors selected for further validation.

The sensors were distributed as follows:

| City | Sensors checked |
|---|---:|
| Jakarta | 11 |
| Tangerang | 0 |
| Bekasi | 0 |
| Bogor | 1 |
| **Total** | **12** |

Jakarta had the most sensors, but did not provide reliable daily coverage.

### 3.2 Daily data quality criteria

The validator checked these three conditions for each sensor's daily observations to be considered VALID:

1. At least 75% of the expected hourly observations were available, meaning at least 18 out of 24 hours.
2. The daily value was above zero and below 500 µg/m³.
3. The sensor did not report identical readings throughout the day, which could indicate that the sensor was stuck.

A sensor was USABLE when at least 70% of its assessed days were valid.
These criteria helped distinguish sensors that simply had recorded data vs sensors that provided sufficiently complete and reliable observations.

### 3.3 City-level assessment results

The validator assigned a PASS, PARTIAL or FAIL result to each city based on its available sensor coverage.

| City | Usable sensors / locations | Days with at least one valid sensor | Verdict |
|---|---:|---:|---|
| Jakarta | 0 / 0 | 24.3% | FAIL |
| Tangerang | 0 / 0 | 0.0% | FAIL |
| Bekasi | 0 / 0 | 0.0% | FAIL |
| Bogor | 0 / 0 | 19.7% | FAIL |

The city-level requirements were:
- **PASS:** At least 90% of study days have one or more valid sensors, with no month below 75% coverage.
- **PARTIAL:** At least 60% of study days have one or more valid sensors.
- **FAIL:** Coverage is below 60%.

### Findings

**Jakarta**
- Jakarta had 11 sensors checked, but none met the minimum requirement.
- Only 24.3% of the 304 study days had at least one valid sensor. The worst performing month had no valid observations.
Meaning, despite having several sensors, the available data was not consistent.

**Tangerang**
- No PM2.5 sensors with observations were available during the timeframe.
As a result, there was no data available for analysis or comparison.

**Bekasi**
- Similar to Tangerang, no PM2.5 sensors with observations were available during the timeframe.
This means Bekasi could not be included in the planned geographical comparison.

**Bogor**
- Only one sensor was checked, and it did not meet the minimum requirement.
- Only 19.7% of data days with at least one valid sensor, showing that the data was highly intermittent.

### Full validator conclusion

All four cities received a **FAIL** verdict. The results show that the available monitoring data does not meet the requirements for the original geographical and temporal analysis.

## 4. Why the Original Analysis Is Not Feasible

The original plan was to analyze PM2.5 patterns across Jakarta, with Tangerang, Bekasi and Bogor as comparison areas.
The planned analysis included hourly and daily concentration patterns, periods with higher PM2.5 concentrations, and the frequency and duration of elevated concentration episodes.

However, the validation results revealed several problems listed below:

**1. Not enough daily observations**
Jakarta had at least one valid sensor on only 24.3% of the study days. This is not enough to describe PM2.5 patterns consistently throughout the assessment period.

**2. No sensors met the usability requirement**
None of the 12 sensors passed the minimum requirement of 70% valid days.

**3. Limited geographical coverage**
Tangerang and Bekasi had no available PM2.5 observations, while Bogor had only one sensor with highly intermittent data.
This makes it difficult to compare PM2.5 patterns across the selected areas.

**4. Inconsistent reporting**
Some sensors had relatively regular observation intervals, while others had long gaps or only recorded data for a short period.
A high number of records does not necessarily mean that a sensor provides consistent coverage.

**5. Measurement quality is not guaranteed**
Even when a sensor reports regularly, its measurements still need to be checked for completeness, validity and possible measurement problems.
Because of these limitations, the original analysis cannot provide a reliable comparison of PM2.5 patterns across the selected cities.

## 5. A Limited Exploratory Analysis Is Still Possible

Although the original analysis is not feasible, the available data can still be used for a smaller exploratory analysis. The initial validator identified two sensors at Lab. Lingkungan with relatively consistent hourly observation intervals during October. These sensors provide a **possible starting point** for a more focused analysis.

The proposed sample analysis will use:

**Selected data:** Lab. Lingkungan (sensor 17766208), subject to further checks of its October data quality and daily completeness.

**Observation period:** October 2026.

**Source granularity:** Hourly PM2.5 observations.

**Analysis granularity:** Hourly observations for time-based analysis, with daily summaries where data coverage is sufficient.

The analysis will focus on:

- Overall PM2.5 concentration distribution.
- Hours when higher PM2.5 concentrations tend to occur.
- Differences in observed concentrations across days of the week.
- How often relatively high PM2.5 readings occur.
- The duration and timing of elevated concentration episodes.

The analysis will only describe the observations from the **selected sensor and period**. It will **NOT** be used to describe the overall air quality of Jakarta.

### Limitations of the sample analysis

The findings must be understood within the following limitations:

1. **Single monitoring location:** The analysis uses data from one sensor and does not represent the overall air quality of Jakarta.
2. **Short observation period:** One month is not enough to identify long-term or seasonal patterns.
3. **Limited historical coverage:** The selected sensor does not provide a complete year of observations.
4. **Sensor measurement limitations:** The sensor's measurement technology, calibration and accuracy may affect the recorded values.
5. **Missing observations:** Gaps in hourly data may affect daily averages and the identification of elevated episodes.
6. **Limited geographical representation:** The results cannot show whether similar patterns occur in other locations.
7. **No source identification:** The analysis cannot explain what causes PM2.5 concentrations to increase.

The purpose is to understand what can be learned from the available data, without making conclusions that the data cannot support.

## 6. Conclusion and Project Direction

The two validation processes provide a clearer picture of the available OpenAQ data.

The initial validator identified sensors with potentially useful observation histories. However, the full validator showed that none of the evaluated sensors met the defined reliability requirements for the original city-level analysis. Jakarta had some available observations, but daily coverage was not sufficient. Tangerang and Bekasi had no PM2.5 observations during the assessment period, while Bogor had only one sensor with highly intermittent data.

As a result, the original analysis comparing PM2.5 patterns across Jakarta and its surrounding areas cannot be conducted reliably using the available dataset. Instead, this project will use the Lab. Lingkungan sensor to conduct a limited exploratory analysis of hourly and daily PM2.5 patterns during October 2026, subject to further data quality checks. The findings will be presented with clear limitations based on the selected sensor and observation period.

More importantly, the assessment highlights a problem beyond the analysis itself: the availability and reliability of monitoring data cannot be assumed. Future air quality analysis requires more consistent observations, better visibility into sensor reporting and a way to identify missing or potentially unreliable measurements.

This provides the reason for a separate air quality monitoring project, focused on tracking sensor availability, observation completeness, reporting continuity and data quality over time.