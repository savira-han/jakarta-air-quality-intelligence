
-- ============================================================
-- ELEVATED OBSERVATION ANALYSIS
-- STEP 6: SIMULTANEOUS EPISODE SUMMARY
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
        b.value AS lab_lingkungan_3_value

    FROM sensor_observations a

    INNER JOIN sensor_observations b
        ON a.local_start_time = b.local_start_time

    WHERE a.sensor_id = '17766208'
      AND b.sensor_id = '17766346'

      AND a.value > a.p90_threshold
      AND b.value > b.p90_threshold
),

episode_flags AS (
    SELECT
        *,

        CASE
            WHEN LAG(local_start_time) OVER (
                ORDER BY local_start_time
            ) IS NULL
            OR local_start_time <>
                LAG(local_start_time) OVER (
                    ORDER BY local_start_time
                ) + INTERVAL '1 hour'
            THEN 1
            ELSE 0
        END AS episode_start_flag

    FROM paired_observations
),

episode_groups AS (
    SELECT
        *,

        SUM(episode_start_flag) OVER (
            ORDER BY local_start_time
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS episode_id

    FROM episode_flags
)

SELECT
    episode_id,

    MIN(local_start_time) AS episode_start,
    MAX(local_start_time) AS episode_end,

    COUNT(*) AS simultaneous_observations,

    COUNT(*) AS duration_hours,

    ROUND(
        AVG(lab_lingkungan_value)::NUMERIC, 2
    ) AS lab_lingkungan_mean,

    ROUND(
        MAX(lab_lingkungan_value)::NUMERIC, 2
    ) AS lab_lingkungan_peak,

    ROUND(
        AVG(lab_lingkungan_3_value)::NUMERIC, 2
    ) AS lab_lingkungan_3_mean,

    ROUND(
        MAX(lab_lingkungan_3_value)::NUMERIC, 2
    ) AS lab_lingkungan_3_peak

FROM episode_groups

GROUP BY episode_id

ORDER BY episode_start;
