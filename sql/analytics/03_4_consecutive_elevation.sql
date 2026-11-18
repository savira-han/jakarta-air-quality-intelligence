
-- ============================================================
-- ELEVATED OBSERVATION ANALYSIS
-- STEP 4: CONSECUTIVE ELEVATED OBSERVATIONS
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

observation_sequence AS (
    SELECT
        p.sensor_id,
        p.location_name,
        p.local_start_time,
        p.value,
        t.p90_threshold,

        LAG(p.local_start_time) OVER (
            PARTITION BY p.sensor_id
            ORDER BY p.local_start_time
        ) AS previous_time,

        LAG(p.value) OVER (
            PARTITION BY p.sensor_id
            ORDER BY p.local_start_time
        ) AS previous_value

    FROM processed_pm25_hourly p

    INNER JOIN sensor_thresholds t
        ON p.sensor_id = t.sensor_id

    WHERE p.local_start_date >= '2026-10-01'
      AND p.local_start_date < '2026-11-01'
),

episode_flags AS (
    SELECT
        *,

        CASE
            WHEN value > p90_threshold
             AND (
                    previous_time IS NULL
                    OR previous_time <> local_start_time - INTERVAL '1 hour'
                    OR previous_value IS NULL
                    OR previous_value <= p90_threshold
                 )
            THEN 1
            ELSE 0
        END AS episode_start_flag

    FROM observation_sequence
),

episode_groups AS (
    SELECT
        *,

        SUM(episode_start_flag) OVER (
            PARTITION BY sensor_id
            ORDER BY local_start_time
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS episode_id

    FROM episode_flags
),

episode_summary AS (
    SELECT
        sensor_id,
        MAX(location_name) AS location_name,
        episode_id,

        MIN(local_start_time) AS episode_start,
        MAX(local_start_time) AS episode_end,

        COUNT(*) AS episode_observations,

        ROUND(
            COUNT(*)::NUMERIC,
            0
        ) AS episode_duration_hours,

        ROUND(
            AVG(value)::NUMERIC,
            2
        ) AS episode_mean,

        ROUND(
            MAX(value)::NUMERIC,
            2
        ) AS episode_peak,

        ROUND(
            MIN(value)::NUMERIC,
            2
        ) AS episode_minimum,

        ROUND(
            MAX(p90_threshold)::NUMERIC,
            2
        ) AS p90_threshold

    FROM episode_groups

    WHERE value > p90_threshold

    GROUP BY
        sensor_id,
        episode_id
)

SELECT
    *,

    CASE
        WHEN episode_observations = 1 THEN 'Isolated'
        ELSE 'Sustained'
    END AS episode_type

FROM episode_summary

ORDER BY
    sensor_id,
    episode_start;
