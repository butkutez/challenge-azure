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
-- SELECT * FROM [dbo].[GhentDepartures];