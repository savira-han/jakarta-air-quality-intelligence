
-- ============================================================
-- ELEVATED OBSERVATION ANALYSIS
-- STEP 1: SENSOR-SPECIFIC P90 THRESHOLD
-- Observation Window: October 1-31, 2026
-- ============================================================

SELECT
    sensor_id,
    MAX(location_name) AS location_name,

    COUNT(value) AS observation_count,

    ROUND(
        QUANTILE_CONT(value, 0.90)::NUMERIC, 2
    ) AS p90_threshold,

    ROUND(
        MIN(value)::NUMERIC, 2
    ) AS minimum_value,

    ROUND(
        MAX(value)::NUMERIC, 2
    ) AS maximum_value

FROM processed_pm25_hourly

WHERE sensor_id IN ('17766208', '17766346')
  AND local_start_date >= '2026-10-01'
  AND local_start_date < '2026-11-01'
  AND value IS NOT NULL

GROUP BY sensor_id

ORDER BY sensor_id;
