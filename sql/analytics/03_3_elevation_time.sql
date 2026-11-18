
-- ============================================================
-- ELEVATED OBSERVATION ANALYSIS
-- STEP 3: TIME-OF-DAY DISTRIBUTION
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

        EXTRACT(HOUR FROM p.local_start_time) AS observation_hour,

        p.value

    FROM processed_pm25_hourly p

    INNER JOIN sensor_thresholds t
        ON p.sensor_id = t.sensor_id

    WHERE p.local_start_date >= '2026-10-01'
      AND p.local_start_date < '2026-11-01'
      AND p.value IS NOT NULL
      AND p.value > t.p90_threshold
)

SELECT
    sensor_id,
    MAX(location_name) AS location_name,

    observation_hour,

    COUNT(*) AS elevated_observations,

    ROUND(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (PARTITION BY sensor_id),
        2
    ) AS elevated_hour_percentage,

    ROUND(AVG(value)::NUMERIC, 2) AS elevated_mean,

    ROUND(MAX(value)::NUMERIC, 2) AS elevated_maximum

FROM elevated_observations

GROUP BY
    sensor_id,
    observation_hour

ORDER BY
    sensor_id,
    observation_hour;
