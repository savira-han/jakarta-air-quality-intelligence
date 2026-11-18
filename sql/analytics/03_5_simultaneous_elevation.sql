
-- ============================================================
-- ELEVATED OBSERVATION ANALYSIS
-- STEP 5: SIMULTANEOUS ELEVATED OBSERVATIONS
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

sensor_observations AS (
    SELECT
        p.sensor_id,
        p.local_start_time,
        p.value,
        t.p90_threshold

    FROM processed_pm25_hourly p

    INNER JOIN sensor_thresholds t
        ON p.sensor_id = t.sensor_id

    WHERE p.local_start_date >= '2026-10-01'
      AND p.local_start_date < '2026-11-01'
      AND p.value IS NOT NULL
),

paired_observations AS (
    SELECT
        a.local_start_time,

        a.value AS lab_lingkungan_value,
        a.p90_threshold AS lab_lingkungan_p90,

        b.value AS lab_lingkungan_3_value,
        b.p90_threshold AS lab_lingkungan_3_p90,

        CASE
            WHEN a.value > a.p90_threshold
             AND b.value > b.p90_threshold
            THEN 1
            ELSE 0
        END AS both_elevated

    FROM sensor_observations a

    INNER JOIN sensor_observations b
        ON a.local_start_time = b.local_start_time

    WHERE a.sensor_id = '17766208'
      AND b.sensor_id = '17766346'
)

SELECT
    local_start_time,

    ROUND(lab_lingkungan_value::NUMERIC, 2)
        AS lab_lingkungan_value,

    ROUND(lab_lingkungan_3_value::NUMERIC, 2)
        AS lab_lingkungan_3_value,

    ROUND(lab_lingkungan_p90::NUMERIC, 2)
        AS lab_lingkungan_p90,

    ROUND(lab_lingkungan_3_p90::NUMERIC, 2)
        AS lab_lingkungan_3_p90

FROM paired_observations

WHERE both_elevated = 1

ORDER BY local_start_time;
