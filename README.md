# iRail Data Engineering Pipeline

[![forthebadge made-with-python](https://forthebadge.com/api/badges/generate?panels=2&primaryLabel=Made+with&secondaryLabel=SQL&primaryBGColor=%2331C4F3&primaryTextColor=%23FFFFFF&secondaryBGColor=%23389AD5&secondaryTextColor=%23FFFFFF&primaryFontSize=11&primaryFontWeight=400&primaryLetterSpacing=2&primaryFontFamily=Roboto&primaryTextTransform=uppercase&secondaryFontSize=12&secondaryFontWeight=900&secondaryLetterSpacing=2&secondaryFontFamily=Montserrat&secondaryTextTransform=uppercase&secondaryIcon=sqlite&secondaryIconColor=%23FFFFFF&secondaryIconSize=16&secondaryIconPosition=left)](https://forthebadge.com/generator)
[![forthebadge made-with-python](https://forthebadge.com/api/badges/generate?panels=2&primaryLabel=visualised+with&secondaryLabel=Power+BI&primaryBGColor=%23ff52b7&primaryTextColor=%23FFFFFF&secondaryBGColor=%23b530f3&secondaryTextColor=%23FFFFFF&primaryFontSize=11&primaryFontWeight=400&primaryLetterSpacing=2&primaryFontFamily=Roboto&primaryTextTransform=uppercase&secondaryFontSize=12&secondaryFontWeight=900&secondaryLetterSpacing=2&secondaryFontFamily=Montserrat&secondaryTextTransform=uppercase)](https://forthebadge.com/generator)
[![forthebadge made-with-python](https://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)


[![Wallpaper](https://www.luetze-transportation.com/fileadmin/luetze-transportation.com/media/en/blog/ai-in-the-railway-ecosystem/ai-in-the-railway-ecosystem-luetze-transportation-gmbh.jpg)](https://www.luetze-transportation.com/blog/ai-in-the-railway-ecosystem)  
*Image source: [Luetze Transportation](https://www.luetze-transportation.com/blog/ai-in-the-railway-ecosystem)*

## Description
The Belgian railway network is a complex web of real-time movements, delays, and connections. This project focuses on building a robust, cloud-native data pipeline to capture this motion. By fetching live data from the [iRail API](https://docs.irail.be/), processing it through Azure Functions, and storing it in an Azure SQL Database, this project transforms raw transport streams into structured insights for delay monitoring and operational analysis.

## Process & Methodology
The development of this pipeline followed a structured approach to ensure data integrity and cloud compatibility.

I. **Data Source & Analysis**
I analyzed the iRail API structure, specifically the **liveboard** endpoint. Since the API returns deeply nested JSON, I identified the following key fields required for meaningful insights:

- ```vehicle & vehicleinfo```: For train identification and type.

- ```time```: Unix timestamp requiring conversion to SQL-friendly DATETIME.

- ```delay```: Integer values to track punctuality.

II. **Normalization Strategy**
Instead of importing a heavy library like Pandas, I opted for a lightweight manual normalization approach within the Azure Function.

- **Flattening**: I iterated through the departures list to extract nested values (like train_number from inside vehicleinfo).  
Code:  ```train.get("vehicleinfo", {}).get("number")```

- **Data Typing**: I ensured integers (delays/canceled status) and strings (destinations) were correctly typed before the SQL insertion.  
Code: ``` int(train.get("delay", 0))```, ```int(train.get("canceled", 0))``` and ```train.get("station")```

- **Transformation**: 
    - *Parsing*: I converted raw Unix timestamps (seconds since epoch) into Python datetime objects using ```datetime.fromtimestamp(ts)```.

    - *Serialization*: I then used ```dt.isoformat()``` to generate ISO 8601 strings. This is a critical step because while Python objects exist in memory, Azure SQL requires a standardized string format to correctly interpret and store data into DATETIME columns.

III. **Cloud Infrastructure Setup**  
The infrastructure was provisioned via the Azure Portal:
- **Azure SQL Database**: Created a serverless database and configured the Server-level Firewall to allow the Function App's IP address.

- **Function App**: Configured a Python 3.10 environment.

- **Security**: To avoid hardcoding credentials, I utilized Azure App Settings (Environment Variables) to store the SQL_AZURE_CONNECTION string.

IV. **Database Integration**  
I used the pyodbc driver to establish a connection. To optimize performance, I implemented ```cursor.executemany()```. This allows the function to send all train departures in a single batch to the database, reducing "chattiness" and improving execution speed.

## SQL Schema
To support the data being fetched, I created the following table in Azure SQL:

```sql
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
);
```

## Repo Structure

```
CHALLENGE-AZURE
├── database/                   
│   └── takeaway.db
├── reports/                
│   └── power_BI_analysis.pbip
├── results/                 
│   ├── ER_schema_takeaway.png
│   ├── Q1.png
│   └── ...                 
├── README.md
└── sql_analysis.sql
```

## Installation

1. **Clone the project:**

```
git clone https://github.com/butkutez/delivery-market-analysis.git
```
2. **SQL Analysis:**

- Open sql_analysis.sql in SQLite extension in VS Code (Extention ID: *alexcvzz.vscode-sqlite*).

- Connect to database/takeaway.db to execute queries in VS code.

3. **Power BI Report:**

- Ensure you have the latest version of Power BI Desktop.
- To access the database via Power BI or external tools, please ensure the SQLite ODBC Driver is installed. Detailed setup instructions can be found
[here](https://www.thebricks.com/resources/guide-can-power-bi-connect-to-sqlite-database).

## Summary

This project aimed to uncover market dynamics and consumer value drivers within the food delivery sector. To achieve this, I conducted a structured analysis centered around 10 key business questions:

1. What is the price distribution of menu items?
2. What is the distribution of restaurants per location?
3. Which are the top 10 pizza restaurants by rating?
4. Map locations offering kapsalons (or your favorite dish) and their average price.
5. Which restaurants have the best price-to-rating ratio?
6. Where are the delivery ‘dead zones’—areas with minimal restaurant coverage?
7. How does the availability of vegetarian and vegan dishes vary by area?
8. Identify the World Hummus Order (WHO); top 3 hummus serving restaurants.
9. Identify top 10 vegan restaurants in Ghent by rating.
10. Do restaurants that support delivery charge more for their food than restaurants that only support pickup?

**The Result:** By answering these questions, I successfully visualized complex market trends and extracted actionable insights using SQL and Power BI. The analysis provides a clear map of market saturation and consumer value, identifying specific opportunities for expansion in underserved "dead zones."

**Future Improvements:**  
- Schema Optimization: Improve database normalization for faster query performance.

- Cross-Platform Benchmarking: Compare delivery fee variations across Uber Eats and Deliveroo.

## **Timeline**
This project was completed over 4 days.

## **Personal Situation**
This project was completed as part of the AI & Data Science Bootcamp at BeCode.org.

**Connect** with me on [LinkedIn](https://www.linkedin.com/in/zivile-butkute/).