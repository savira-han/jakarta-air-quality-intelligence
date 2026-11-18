-- ============================================================
-- DAILY PM2.5 TREND ANALYSIS
-- Observation Window: October 1-31, 2026
-- Sensors: 17766208, 17766346
-- ============================================================

SELECT
    sensor_id,
    MAX(location_name) AS location_name,
    local_start_date AS observation_date,

    COUNT(value) AS observation_count,

    ROUND(AVG(value)::NUMERIC, 2) AS daily_mean,
    ROUND(MEDIAN(value)::NUMERIC, 2) AS daily_median,

    ROUND(MIN(value)::NUMERIC, 2) AS daily_min,
    ROUND(MAX(value)::NUMERIC, 2) AS daily_max,

    ROUND(STDDEV(value)::NUMERIC, 2) AS daily_stddev,

    ROUND(
        (MAX(value) - MIN(value))::NUMERIC,
        2
    ) AS daily_range

FROM processed_pm25_hourly

WHERE sensor_id IN ('17766208', '17766346')
  AND local_start_date >= '2026-10-01'
  AND local_start_date < '2026-11-01'
  AND value IS NOT NULL

GROUP BY
    sensor_id,
    local_start_date

ORDER BY
    sensor_id,
    observation_date;