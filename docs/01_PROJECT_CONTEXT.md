# Project Context

## Background

Air quality is an important environmental concern in Jakarta and its surrounding areas. Understanding how PM2.5 concentrations change over time can help identify periods when pollution levels are relatively high, when they tend to occur, and how frequently they happen.

This project started with an attempt to retrieve publicly available PM2.5 data from OpenAQ and investigate whether it could support a meaningful air quality analysis.

The initial plan was to focus on Jakarta, with Tangerang, Bekasi and Bogor included as comparison areas. The idea was to explore temporal patterns in PM2.5 concentrations and see whether the available data could provide useful insights across these locations.

However, the initial data discovery and feasibility assessment revealed significant limitations in the available monitoring data.

## Project Objectives

This project aims to:

1. Explore publicly available PM2.5 monitoring locations and sensors in Jakarta, Tangerang, Bekasi and Bogor.
2. Assess the availability, completeness and continuity of historical PM2.5 observations.
3. Determine whether the available data can support meaningful air quality analysis.
4. Extract limited descriptive insights from the observations that are suitable for analysis.
5. Identify the data limitations and monitoring needs that could affect future air quality analysis.

## Initial Analytical Scope

The original plan was to conduct a temporal analysis of PM2.5 concentrations in Jakarta and use Tangerang, Bekasi and Bogor as comparison areas.

The intended analysis included:

- Overall PM2.5 concentration patterns.
- Hourly and daily concentration changes.
- Typical hours and days with higher concentrations.
- Frequency and duration of elevated PM2.5 episodes.
- Comparisons between Jakarta and surrounding areas, where data availability allowed.

Before proceeding with the analysis, a data feasibility assessment was conducted using OpenAQ data.

The assessment examined candidate monitoring locations, sensor availability, historical data coverage, daily observation completeness and reporting continuity.

## Project Direction and Data Limitations

The feasibility assessment showed that the available data was not sufficiently reliable to support the original analytical scope.

**Jakarta**

PM2.5 data is available from several monitoring locations, but its availability and reporting consistency are limited.

Although multiple sensors were identified, none met the defined usability threshold of at least 70% valid days during the assessment period. Only 24.3% of the 304 study days had at least one valid sensor, and some months had no valid observations.

This means that the available Jakarta data does not provide sufficiently consistent coverage for a reliable analysis across the city.

**Tangerang, Bekasi and Bogor**

Data availability in the surrounding areas is even more limited.

Tangerang and Bekasi had no PM2.5 sensors with observations during the assessment period. Bogor had only one candidate sensor, but its observations were highly intermittent, with only 19.7% of study days having at least one valid sensor.

As a result, these locations cannot provide reliable comparison data for the intended geographical analysis.

**Implications for the analysis**

The original plan to compare PM2.5 patterns across Jakarta and its surrounding areas is therefore not feasible with the currently available observations.

However, the data is not entirely without value. Selected sensors and observation periods may still support limited exploratory analysis, provided that the findings are clearly presented within their actual data coverage and limitations.

## Project Approach

The project is organized into five stages:

1. **Data Discovery** : Explore available PM2.5 monitoring locations, sensors and measurement information from OpenAQ.
2. **Data Retrieval and Feasibility Assessment** : Retrieve historical observations and evaluate sensor availability, completeness and reporting continuity.
3. **Data Limitation Assessment** : Identify geographical and measurement limitations that affect the reliability and scope of the intended analysis.
4. **Exploratory Analysis** : Use the most suitable available observations to examine PM2.5 temporal patterns and identify limited descriptive insights.
5. **Monitoring Solution Rationale** : Translate the identified data availability and reporting issues into requirements for a more reliable air quality monitoring process.

## Project Direction

Rather than forcing a broad air quality analysis with insufficient data, this project will focus on what can reasonably be learned from the available observations.

A selected sensor and observation period may be used to explore typical PM2.5 concentrations, when higher readings tend to occur, and how frequently elevated observations are recorded. These findings will be treated as observations from the selected monitoring source, not as a representation of overall air quality in Jakarta.

The data discovery process also highlights a wider problem: having monitoring locations does not guarantee that usable data will be consistently available.

This creates the rationale for a separate air quality monitoring project. Its focus will be on tracking sensor availability, reporting continuity, data completeness and measurement quality, so that future air quality analysis can be supported by more reliable observations.