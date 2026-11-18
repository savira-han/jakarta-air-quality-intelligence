
-- ============================================================
-- ELEVATED OBSERVATION ANALYSIS
-- STEP 2: ELEVATED OBSERVATION FREQUENCY
-- Threshold: Sensor-specific P90
-- Observation Window: October 1-31, 2026
-- ============================================================

WITH sensor_thresholds AS (
    SELECT
        sensor_id,
        QUANTILE_CONT(value, 0.90) AS p90_threshold

    FROM processed_pm25_hourly

    WHERE sensor_id IN ('17766208', '17766346')
      AND local_start_date >= '2026-10-01'
      AND local_start_date < '2026-11-01'
      AND value IS NOT NULL

    GROUP BY sensor_id
),

elevated_observations AS (
    SELECT
        p.sensor_id,
        p.location_name,
        p.value,
        t.p90_threshold,

        CASE
            WHEN p.value > t.p90_threshold THEN 1
            ELSE 0
        END AS is_elevated

    FROM processed_pm25_hourly p

    INNER JOIN sensor_thresholds t
        ON p.sensor_id = t.sensor_id

    WHERE p.local_start_date >= '2026-10-01'
      AND p.local_start_date < '2026-11-01'
      AND p.value IS NOT NULL
)

SELECT
    sensor_id,
    MAX(location_name) AS location_name,

    COUNT(*) AS total_observations,

    SUM(is_elevated) AS elevated_observations,

    ROUND(
        SUM(is_elevated) * 100.0 / COUNT(*),
        2
    ) AS elevated_percentage,

    ROUND(
        MAX(p90_threshold)::NUMERIC, 2
    ) AS p90_threshold,

    ROUND(
        AVG(value) FILTER (WHERE is_elevated = 1)::NUMERIC,
        2
    ) AS elevated_mean,

    ROUND(
        MIN(value) FILTER (WHERE is_elevated = 1)::NUMERIC,
        2
    ) AS elevated_minimum,

    ROUND(
        MAX(value) FILTER (WHERE is_elevated = 1)::NUMERIC,
        2
    ) AS elevated_maximum

FROM elevated_observations

GROUP BY sensor_id

ORDER BY sensor_id;
