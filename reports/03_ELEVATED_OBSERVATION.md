# Elevated Observation Analysis

## 1. Analysis Overview

This analysis examines elevated PM2.5 observations recorded by two monitoring sensors in Jakarta during October 1-31, 2026.

The purpose is to understand how frequently elevated readings occurred, when they were observed, whether they appeared as isolated observations or sustained episodes, and whether both sensors recorded elevated readings at the same time.

The analysis covers:

- Sensor-specific elevated observation thresholds.
- Frequency and magnitude of elevated observations.
- Hourly distribution of elevated observations.
- Consecutive elevated episodes for each sensor.
- Simultaneous elevated observations and episodes across both sensors.

All findings are descriptive and limited to the available observations from these two sensors.

## 2. Benchmark Definition

### 2.1 Threshold Selection

A sensor-specific 90th percentile (P90) threshold was used to identify elevated hourly observations.

P90 represents the value at or below which 90% of a sensor's observations fall. Readings above this threshold represent approximately the highest 10% of observations for that sensor during the analysis period.

A separate threshold was calculated for each sensor because their observed PM2.5 distributions differ.

| Sensor | Location | Observations | P90 Threshold |
|---|---|---:|---:|
| 17766208 | Lab. Lingkungan | 743 | 84.64 µg/m³ |
| 17766346 | Lab. Lingkungan 3 | 689 | 95.52 µg/m³ |

### 2.2 Interpretation

The P90 threshold is a dataset-relative benchmark. It identifies unusually high observations compared with the distribution recorded by each sensor during October 2026.

It is not a health-based air quality guideline or a regulatory threshold.

Using separate thresholds also means that an observation can be classified as elevated for one sensor but not the other, even when both sensors record similar absolute concentrations.

For this analysis, an observation is classified as elevated when:

`PM2.5 value > sensor-specific P90 threshold`

The threshold comparison uses a strict greater-than condition.

## 3. Elevated Observation Frequency

### 3.1 Frequency Summary

The number and proportion of observations above each sensor's P90 threshold were calculated.

| Metric | Lab. Lingkungan | Lab. Lingkungan 3 |
|---|---:|---:|
| Total observations | 743 | 689 |
| Elevated observations | 75 | 69 |
| Elevated proportion | 10.09% | 10.01% |
| P90 threshold | 84.64 | 95.52 |
| Mean of elevated observations | 96.19 | 110.68 |
| Minimum elevated value | 84.70 | 95.60 |
| Maximum elevated value | 131.00 | 149.00 |

*Concentrations are in µg/m³.*

### 3.2 Findings

Both sensors recorded elevated observations at approximately 10% of their available hourly observations. This is consistent with the use of a P90 threshold.

However, the magnitude of elevated observations differed between the sensors.

Lab. Lingkungan 3 recorded a higher mean elevated concentration of 110.68 µg/m³, compared with 96.19 µg/m³ at Lab. Lingkungan.

It also recorded the highest individual observation in this analysis, at 149.00 µg/m³. The maximum at Lab. Lingkungan was 131.00 µg/m³.

This indicates that although the proportion of elevated observations was similar, the absolute concentrations recorded during those observations were generally higher at Lab. Lingkungan 3.

The similar elevated proportions should not be interpreted as evidence that both sensors experienced the same elevated events.

## 4. Hourly Distribution of Elevated Observations

### 4.1 Distribution Summary

Elevated observations were grouped by hour of day to identify when they were most frequently recorded.

The percentage below represents each hour's share of all elevated observations for that sensor. It does not represent the probability of an elevated reading occurring during that hour.

**Lab. Lingkungan**

| Hour | Elevated Observations | Share of Elevated Observations |
|---|---:|---:|
| 00:00 | 1 | 1.33% |
| 01:00 | 5 | 6.67% |
| 02:00 | 6 | 8.00% |
| 03:00 | 6 | 8.00% |
| 04:00 | 9 | 12.00% |
| 05:00 | 8 | 10.67% |
| 06:00 | 9 | 12.00% |
| 07:00 | 11 | 14.67% |
| 08:00 | 6 | 8.00% |
| 09:00 | 4 | 5.33% |
| 10:00 | 5 | 6.67% |
| 11:00 | 2 | 2.67% |
| 12:00 | 1 | 1.33% |
| 21:00 | 1 | 1.33% |
| 23:00 | 1 | 1.33% |

The highest number of elevated observations occurred at 07:00, with 11 observations (14.67%). The next highest counts were at 04:00 and 06:00, with 9 observations each.

**Lab. Lingkungan 3**

| Hour | Elevated Observations | Share of Elevated Observations |
|---|---:|---:|
| 00:00 | 1 | 1.45% |
| 01:00 | 5 | 7.25% |
| 02:00 | 8 | 11.59% |
| 03:00 | 5 | 7.25% |
| 04:00 | 8 | 11.59% |
| 05:00 | 9 | 13.04% |
| 06:00 | 9 | 13.04% |
| 07:00 | 7 | 10.14% |
| 08:00 | 3 | 4.35% |
| 09:00 | 4 | 5.80% |
| 10:00 | 3 | 4.35% |
| 11:00 | 1 | 1.45% |
| 18:00 | 1 | 1.45% |
| 19:00 | 1 | 1.45% |
| 21:00 | 3 | 4.35% |
| 23:00 | 1 | 1.45% |

The highest counts occurred at 05:00 and 06:00, with 9 observations each (13.04%). The next highest counts were at 02:00 and 04:00, with 8 observations each.

### 4.2 Findings

Both sensors show a concentration of elevated observations during the early morning hours.

At Lab. Lingkungan, elevated observations were most frequently recorded between 04:00 and 08:00, with the highest count at 07:00.

At Lab. Lingkungan 3, the highest counts occurred between 02:00 and 06:00, particularly at 05:00 and 06:00.

Lab. Lingkungan 3 also recorded a small number of elevated observations during the evening, at 18:00, 19:00, and 21:00.

Overall, the hourly distribution suggests that elevated observations were more frequently recorded during the early morning period at both monitoring locations. This describes the timing of the recorded observations and does not establish why these patterns occurred.

## 5. Consecutive Elevated Episodes

### 5.1 Method

Elevated observations were grouped into episodes when consecutive hourly observations remained above the sensor-specific P90 threshold.

A new episode was started when:

- The current observation was not preceded by another elevated observation.
- The previous observation was not exactly one hour earlier.
- The previous observation was missing or was not above the threshold.

An episode containing one elevated hourly observation was classified as **isolated**. An episode containing two or more consecutive elevated observations was classified as **sustained**.

Missing observations and gaps in timestamps therefore break an episode.

### 5.2 Episode Summary

| Metric | Lab. Lingkungan | Lab. Lingkungan 3 |
|---|---:|---:|
| Total episodes | 30 | 31 |
| Sustained episodes | 22 | 18 |
| Isolated episodes | 8 | 13 |
| Longest episode | 6 hours | 6 hours |
| Highest observed value within an episode | 131.00 | 149.00 |

*Concentrations are in µg/m³.*

### 5.3 Findings

Lab. Lingkungan recorded 30 elevated episodes, of which 22 were sustained and 8 were isolated. Sustained episodes accounted for 73.33% of its episodes.

Lab. Lingkungan 3 recorded 31 elevated episodes, consisting of 18 sustained and 13 isolated episodes. Sustained episodes accounted for 58.06%.

Both sensors recorded a longest episode duration of six consecutive hours.

Two six-hour periods were observed at both sensors:

| Episode Period | Duration |
|---|---:|
| October 17, 01:00-06:00 | 6 hours |
| October 27, 23:00 - October 28, 04:00 | 6 hours |

During the October 17 episode, Lab. Lingkungan recorded a mean of 103.45 µg/m³ and a peak of 126.00 µg/m³. Lab. Lingkungan 3 recorded a mean of 120.83 µg/m³ and a peak of 145.00 µg/m³.

During the October 27-28 episode, Lab. Lingkungan recorded a mean of 94.80 µg/m³ and a peak of 114.00 µg/m³. Lab. Lingkungan 3 recorded a mean of 111.52 µg/m³ and a peak of 140.00 µg/m³.

The findings show that both sensors recorded sustained elevated periods, but their episode patterns differed. Lab. Lingkungan had a higher proportion of sustained episodes, while Lab. Lingkungan 3 had more isolated episodes.

The two sensors also recorded the same two longest episode periods. This provides a basis for examining whether elevated observations occurred simultaneously across the monitoring locations.

## 6. Simultaneous Elevated Observations and Episodes

### 6.1 Method

To examine whether both sensors recorded elevated observations at the same time, their hourly observations were matched using the exact local observation timestamp.

A timestamp was classified as a simultaneous elevated observation only when:

- Lab. Lingkungan was above its own P90 threshold.
- Lab. Lingkungan 3 was above its own P90 threshold.
- Both observations had the same timestamp.

Consecutive simultaneous elevated timestamps were grouped into simultaneous episodes. A gap of more than one hour separated two episodes.

### 6.2 Overall Summary

| Metric | Result |
|---|---:|
| Simultaneous elevated timestamps | 57 |
| Sustained simultaneous episodes | 16 |
| Isolated simultaneous episodes | 7 |
| Longest simultaneous episode | 6 hours |

The 16 sustained episodes contained 50 hourly observations in total. The remaining 7 observations occurred as isolated simultaneous timestamps.

### 6.3 Simultaneous Episode Details

The following table summarizes all simultaneous elevated episodes recorded during October 2026.

| No. | Episode Start | Episode End | Duration | Lab. Lingkungan Mean | Lab. Lingkungan Peak | Lab. Lingkungan 3 Mean | Lab. Lingkungan 3 Peak |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | Oct 2, 05:00 | Oct 2, 07:00 | 3h | 97.37 | 99.50 | 109.67 | 112.00 |
| 2 | Oct 4, 06:00 | Oct 4, 07:00 | 2h | 109.45 | 120.00 | 129.00 | 143.00 |
| 3 | Oct 5, 05:00 | Oct 5, 06:00 | 2h | 92.45 | 92.80 | 106.50 | 108.00 |
| 4 | Oct 7, 04:00 | Oct 7, 07:00 | 4h | 100.55 | 123.00 | 115.23 | 149.00 |
| 5 | Oct 10, 04:00 | Oct 10, 04:00 | 1h | 86.20 | 86.20 | 98.10 | 98.10 |
| 6 | Oct 11, 06:00 | Oct 11, 07:00 | 2h | 87.30 | 89.10 | 105.00 | 106.00 |
| 7 | Oct 12, 08:00 | Oct 12, 08:00 | 1h | 93.20 | 93.20 | 96.00 | 96.00 |
| 8 | Oct 13, 05:00 | Oct 13, 05:00 | 1h | 85.50 | 85.50 | 97.90 | 97.90 |
| 9 | Oct 14, 09:00 | Oct 14, 09:00 | 1h | 95.80 | 95.80 | 103.00 | 103.00 |
| 10 | Oct 15, 02:00 | Oct 15, 04:00 | 3h | 107.00 | 110.00 | 126.33 | 135.00 |
| 11 | Oct 15, 08:00 | Oct 15, 08:00 | 1h | 86.10 | 86.10 | 101.00 | 101.00 |
| 12 | Oct 16, 05:00 | Oct 16, 07:00 | 3h | 104.00 | 107.00 | 123.33 | 128.00 |
| 13 | Oct 17, 01:00 | Oct 17, 06:00 | 6h | 103.45 | 126.00 | 120.83 | 145.00 |
| 14 | Oct 17, 21:00 | Oct 17, 21:00 | 1h | 89.80 | 89.80 | 99.80 | 99.80 |
| 15 | Oct 18, 05:00 | Oct 18, 07:00 | 3h | 102.27 | 109.00 | 120.33 | 130.00 |
| 16 | Oct 20, 01:00 | Oct 20, 03:00 | 3h | 95.63 | 103.00 | 113.67 | 122.00 |
| 17 | Oct 21, 01:00 | Oct 21, 02:00 | 2h | 88.85 | 89.50 | 99.95 | 101.00 |
| 18 | Oct 21, 04:00 | Oct 21, 05:00 | 2h | 98.00 | 102.00 | 115.50 | 124.00 |
| 19 | Oct 21, 09:00 | Oct 21, 11:00 | 3h | 111.40 | 131.00 | 114.33 | 131.00 |
| 20 | Oct 22, 01:00 | Oct 22, 02:00 | 2h | 90.80 | 91.10 | 106.50 | 107.00 |
| 21 | Oct 22, 07:00 | Oct 22, 10:00 | 4h | 99.18 | 112.00 | 104.08 | 113.00 |
| 22 | Oct 27, 23:00 | Oct 28, 04:00 | 6h | 94.80 | 114.00 | 111.52 | 140.00 |
| 23 | Oct 30, 03:00 | Oct 30, 03:00 | 1h | 91.80 | 91.80 | 112.00 | 112.00 |

*All concentrations are in µg/m³. All timestamps use local time (UTC+7). Duration is the number of consecutive hourly observations in the episode.*

### 6.4 Findings

A total of 57 timestamps were identified where both sensors recorded elevated observations simultaneously.

These observations formed 23 simultaneous episodes: 16 sustained episodes and 7 isolated observations.

The longest simultaneous episodes lasted six hours:

- October 17, 01:00-06:00.
- October 27, 23:00 - October 28, 04:00.

These periods were also the two longest individual elevated episodes identified in the sensor-level analysis.

Lab. Lingkungan 3 recorded a higher episode mean in most of the simultaneous episodes. However, this was not true for every episode. For example, during October 21, 09:00-11:00, both sensors recorded the same peak value of 131.00 µg/m³.

The highest simultaneous episode peak was 149.00 µg/m³ at Lab. Lingkungan 3 during October 7, 04:00-07:00.

The simultaneous observations show that elevated readings at the two monitoring locations sometimes occurred during the same hourly periods, including several sustained periods.

However, simultaneous readings alone do not establish that both sensors were affected by the same physical pollution event. The analysis does not establish the direction, source, or cause of the observed concentrations.

## 7. Overall Findings

The elevated observation analysis identified several patterns across the two monitoring sensors:

1. **Elevated observations occurred at a similar frequency.** Both sensors recorded approximately 10% of their available hourly observations above their respective P90 thresholds.

2. **The absolute concentrations differed.** Lab. Lingkungan 3 recorded a higher mean elevated concentration and a higher maximum observation than Lab. Lingkungan.

3. **Elevated observations were concentrated in the early morning.** Both sensors recorded their highest hourly counts during the early morning period, although the exact peak hours differed.

4. **Elevated readings were often sustained.** Both sensors recorded consecutive elevated episodes lasting up to six hours. Lab. Lingkungan had a higher proportion of sustained episodes, while Lab. Lingkungan 3 recorded more isolated episodes.

5. **Some elevated observations occurred simultaneously.** There were 57 timestamps when both sensors exceeded their respective P90 thresholds, forming 16 sustained episodes and 7 isolated observations.

6. **Two six-hour periods were recorded by both sensors.** These occurred on October 17 and October 27-28, indicating matching periods of sustained elevated observations at the two monitoring locations.

### Scope and Limitations

These findings describe the observations recorded by the two selected sensors during October 2026. They should not be interpreted as a complete representation of Jakarta's air quality.

The P90 threshold is specific to this dataset and analysis period. It is useful for identifying relatively high observations but does not indicate whether a reading meets or exceeds a health-based or regulatory air quality standard.

The analysis also does not establish pollution sources, causes, or relationships between the two monitoring locations. Simultaneous elevated readings indicate that both sensors recorded values above their respective thresholds at matching timestamps, but do not prove that the readings resulted from the same event.

The results are therefore best used to describe sensor-level patterns, identify periods of elevated observations, and support monitoring and dashboard development.