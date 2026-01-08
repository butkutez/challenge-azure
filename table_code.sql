-- IF OBJECT_ID('dbo.GhentDepartures', 'U') IS NOT NULL
    -- DROP TABLE dbo.GhentDepartures;

CREATE TABLE GhentDepartures (
    id INT IDENTITY(1,1) PRIMARY KEY,
    vehicle NVARCHAR(100),
    train_number NVARCHAR(50),
    train_type NVARCHAR(50),
    departure_time DATETIMEOFFSET,
    platform NVARCHAR(10),
    delay_in_seconds INT,
    canceled INT,
    destination NVARCHAR(255),
    created_at DATETIME DEFAULT GETDATE()
)
-- SELECT 
--     vehicle,
--     destination,
--     FORMAT(CAST(departure_time AS DATETIME), 'dd/MM/yyyy HH:mm') AS [Departure],
--     delay_in_seconds / 60 AS [Delay (Min)],
--     CASE WHEN canceled = 1 THEN 'YES' ELSE 'NO' END AS [Is Canceled]
-- FROM GhentDepartures
-- ORDER BY departure_time DESC;