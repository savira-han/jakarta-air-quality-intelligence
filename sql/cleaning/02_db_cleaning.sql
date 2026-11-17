CREATE TABLE processed_pm25_hourly AS 

SELECT 
    "period.datetimeFrom.local" AS local_start_time,
    "period.datetimeTo.local" AS local_end_time,

    -- Date formatting
    CAST("period.datetimeFrom.local" AS DATE) AS local_start_date,
    STRFTIME(CAST("period.datetimeFrom.local" AS TIMESTAMP), '%H:%M:%S') AS local_start_hour,

    CAST("period.datetimeTo.local" AS DATE) AS local_end_date,
    STRFTIME(CAST("period.datetimeTo.local" AS TIMESTAMP), '%H:%M:%S') AS local_end_hour,
    
    -- Core value and location fields
    value,
    master_pm25_hourly.location_name,
    sensor_id,
    location_id,
    latitude,
    longitude,
    "flagInfo.hasFlags" AS has_flags

FROM master_pm25_hourly 
LEFT JOIN location_inventory USING(location_id)

ORDER BY CAST("period.datetimeFrom.local" AS DATE) ASC;