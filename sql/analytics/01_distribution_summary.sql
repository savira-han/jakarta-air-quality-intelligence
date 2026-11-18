
-- ============================================================
-- PM2.5 DISTRIBUTION ANALYSIS
-- Observation Window: October 1-31, 2026
-- Sensors: 17766208, 17766346
-- ============================================================

-- ------------------------------------------------------------
-- BASE DATA
-- ------------------------------------------------------------

-- CREATE OR REPLACE TEMP TABLE october_pm25 AS
WITH 

october_pm25
AS (
SELECT
    sensor_id,
    location_name,
    local_start_date,
    local_start_time,
    value
FROM processed_pm25_hourly
WHERE sensor_id IN ('17766208', '17766346')
  AND local_start_date >= '2026-10-01'
  AND local_start_date < '2026-11-01'
  AND value IS NOT NULL
)


-- ------------------------------------------------------------
-- RESULT 1: DISTRIBUTION SUMMARY
-- ------------------------------------------------------------

-- SELECT
--     sensor_id,
--     MAX(location_name) AS location_name,
--     COUNT(value) AS total_records,

--     ROUND(MIN(value), 2) AS min_value,
--     ROUND(MAX(value), 2) AS max_value,

--     ROUND(AVG(value), 2) AS avg_value,
--     ROUND(MEDIAN(value), 2) AS median_value,
--     ROUND(STDDEV(value), 2) AS stddev_value,

--     ROUND(MAX(value) - MIN(value), 2) AS value_range,
--     ROUND(
--         quantile_cont(value, 0.75)
--         - quantile_cont(value, 0.25), 2
--     ) AS interquartile_range

-- FROM october_pm25
-- GROUP BY sensor_id
-- ORDER BY sensor_id;


-- ------------------------------------------------------------
-- RESULT 2: PERCENTILE ANALYSIS
-- ------------------------------------------------------------

-- SELECT
--     sensor_id,
--     MAX(location_name) AS location_name,
--     COUNT(value) AS total_records,

--     ROUND(quantile_cont(value, 0.10), 2) AS p10,
--     ROUND(quantile_cont(value, 0.25), 2) AS p25,
--     ROUND(quantile_cont(value, 0.50), 2) AS p50,
--     ROUND(quantile_cont(value, 0.75), 2) AS p75,
--     ROUND(quantile_cont(value, 0.90), 2) AS p90,
--     ROUND(quantile_cont(value, 0.95), 2) AS p95,
--     ROUND(quantile_cont(value, 0.99), 2) AS p99

-- FROM october_pm25
-- GROUP BY sensor_id
-- ORDER BY sensor_id;


-- -- ------------------------------------------------------------
-- -- RESULT 3: VALUE FREQUENCY DISTRIBUTION
-- -- ------------------------------------------------------------

, value_buckets AS (
    SELECT
        sensor_id,
        location_name,
        CASE
            WHEN value < 20 THEN '< 20'
            WHEN value < 40 THEN '20 - <40'
            WHEN value < 60 THEN '40 - <60'
            WHEN value < 80 THEN '60 - <80'
            WHEN value < 100 THEN '80 - <100'
            WHEN value < 120 THEN '100 - <120'
            ELSE '>= 120'
        END AS value_range,

        CASE
            WHEN value < 20 THEN 1
            WHEN value < 40 THEN 2
            WHEN value < 60 THEN 3
            WHEN value < 80 THEN 4
            WHEN value < 100 THEN 5
            WHEN value < 120 THEN 6
            ELSE 7
        END AS bucket_order

    FROM october_pm25
),

frequency AS (
    SELECT
        sensor_id,
        MAX(location_name) AS location_name,
        value_range,
        bucket_order,
        COUNT(*) AS observation_count

    FROM value_buckets
    GROUP BY sensor_id, value_range, bucket_order
)

SELECT
    sensor_id,
    location_name,
    value_range,
    observation_count,

    ROUND(
        observation_count * 100.0 /
        SUM(observation_count) OVER (PARTITION BY sensor_id),
        2
    ) AS observation_percentage

FROM frequency
ORDER BY sensor_id, bucket_order;
