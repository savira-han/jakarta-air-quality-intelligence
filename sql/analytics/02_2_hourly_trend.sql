-- ============================================================
-- HOURLY PM2.5 PATTERN ANALYSIS
-- Observation Window: October 1-31, 2026
-- Sensors: 17766208, 17766346
-- ============================================================

SELECT
    sensor_id,
    MAX(location_name) AS location_name,

    EXTRACT(HOUR FROM local_start_time) AS observation_hour,

    COUNT(value) AS observation_count,

    ROUND(AVG(value)::NUMERIC, 2) AS hourly_mean,
    ROUND(MEDIAN(value)::NUMERIC, 2) AS hourly_median,

    ROUND(MIN(value)::NUMERIC, 2) AS hourly_min,
    ROUND(MAX(value)::NUMERIC, 2) AS hourly_max,

    ROUND(STDDEV(value)::NUMERIC, 2) AS hourly_stddev

FROM processed_pm25_hourly

WHERE sensor_id IN ('17766208', '17766346')
  AND local_start_date >= '2026-10-01'
  AND local_start_date < '2026-11-01'
  AND value IS NOT NULL

GROUP BY
    sensor_id,
    observation_hour

ORDER BY
    sensor_id,
    observation_hour;