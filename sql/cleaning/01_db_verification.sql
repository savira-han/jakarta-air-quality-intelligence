
-- -- 1. Confirm the total number of records
-- SELECT COUNT(*) AS total_records
-- FROM master_pm25_hourly;


-- -- 2. Inspect a sample of records
-- SELECT *
-- FROM master_pm25_hourly
-- LIMIT 2;


-- 3. Check the sensors and their observation periods
SELECT
    sensor_id,
    location_id,
    location_name,
    COUNT(*) AS total_records,
    MIN("period.datetimeFrom.local") AS first_observation,
    MAX("period.datetimeFrom.local") AS last_observation
FROM master_pm25_hourly
GROUP BY
    sensor_id,
    location_id,
    location_name
ORDER BY sensor_id;


-- -- 4. Check parameter names and measurement units
-- SELECT
--     parameter_name,
--     parameter_units,
--     COUNT(*) AS total_records
-- FROM master_pm25_hourly
-- GROUP BY parameter_name, parameter_units;


-- -- 5. Check null values in important columns
-- SELECT
--     COUNT(*) AS total_records,
--     COUNT(*) FILTER (WHERE value IS NULL) AS null_values,
--     COUNT(*) FILTER (
--         WHERE "period.datetimeFrom.local" IS NULL
--     ) AS null_timestamps,
--     COUNT(*) FILTER (WHERE sensor_id IS NULL) AS null_sensor_ids
-- FROM master_pm25_hourly;

-- -- 6. Check if the parameter unit and name is uniform
-- SELECT parameter_name, parameter_units, count(*) countrows
-- FROM master_pm25_hourly
-- GROUP BY parameter_name, parameter_units

-- -- 7. Check location_inventory table
-- select *
-- from location_inventory