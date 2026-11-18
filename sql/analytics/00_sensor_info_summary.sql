WITH time_gaps AS (
    SELECT 
        *,
        -- Calculate time difference in hours between consecutive local_start_time per sensor
        EXTRACT(EPOCH FROM (
            local_start_time - LAG(local_start_time) OVER (PARTITION BY sensor_id ORDER BY local_start_time)
        )) / 3600.0 AS start_time_diff_hours
    FROM
        processed_pm25_hourly
    WHERE 
        sensor_id IN ('17766208','17766346') 
        and local_start_date >= '2026-10-01' and local_start_date < '2026-11-01'
)
SELECT 
    sensor_id,
    MAX(location_name) AS location_name,
    -- Value Distribution Statistics
    COUNT(value) AS total_records,
    MIN(local_start_date) start_observation,
    max(local_start_date) end_observation,
    count(distinct local_start_date) unique_observation_date, 
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    
    ROUND(quantile_cont(value, 0.25)::NUMERIC, 2) AS p25_value,
    ROUND(AVG(value)::NUMERIC, 2) AS avg_value,
    ROUND(quantile_cont(value, 0.50)::NUMERIC, 2) AS median_value,
    ROUND(quantile_cont(value, 0.75)::NUMERIC, 2) AS p75_value,

    ROUND(STDDEV(value)::NUMERIC, 2) AS stddev_value,
    
    -- Time Difference Statistics (in hours)
    ROUND(AVG(start_time_diff_hours)::NUMERIC, 2) AS avg_observation_interval,
    ROUND(quantile_cont(start_time_diff_hours, 0.50)::NUMERIC, 2) AS median_observation_interval,
    ROUND(MAX(start_time_diff_hours)::NUMERIC, 2) AS max_observation_gap, 
FROM time_gaps
GROUP BY sensor_id;