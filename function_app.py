import azure.functions as func
import logging
import requests
import json
import pyodbc
from datetime import datetime
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="fetch_ghent_departures")

def fetch_ghent_departures(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('iRail liveboard function started')

    # API setup / fetching data
    url = "https://api.irail.be/liveboard/"
    params = {"station": "Ghent-Sint-Pieters", "format": "json", "lang": "en"}
    headers = {"User-Agent": "Azure-project-irail/1.0 (becode.be; {my_email})"}
        
    # Calling the API
    try: 
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.error(f"Error calling iRail API: {e}")
        return func.HttpResponse(f"Error calling iRail API: {e}", status_code=500)

    # Creating a list of departures
    processed_departures = []
    raw_list = data.get("departures", {}).get("departure", [])
    for train in raw_list:
        ts = int(train.get("time"))
        dt = datetime.fromtimestamp(ts)
        processed_departures.append({
            "vehicle": train.get("vehicle"),
            "train_number":train.get("vehicleinfo", {}).get("number"),
            "train_type": train.get("vehicleinfo", {}).get("type"),
            "departure_time": dt.isoformat(),
            "platform": train.get("platform"),
            "delay_in_seconds": int(train.get("delay", 0)),
            "canceled": int(train.get("canceled", 0)),
            "destination": train.get("station")  
        })
    
    # saving to Azure SQL Database
    if processed_departures:
        try:
            connection_string = os.getenv("SQL_AZURE_CONNECTION")
            if not connection_string:
                return func.HttpResponse("Error: SQL_AZURE_CONNECTION is missing from environment variables.", status_code=500)
            
            with pyodbc.connect(connection_string) as conn:
                
                with conn.cursor() as cursor:
                    sql = """
                            INSERT INTO GhentDepartures (vehicle, train_number, train_type, departure_time, platform, delay_in_seconds, canceled, destination)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """
                    params = [(d['vehicle'], d['train_number'], d['train_type'], d['departure_time'],
                               d['platform'], d['delay_in_seconds'], d['canceled'], d['destination']) 
                              for d in processed_departures]
                    
                    cursor.executemany(sql, params)
                    conn.commit() # keeps the changes

            return func.HttpResponse(json.dumps(processed_departures, indent=2), mimetype="application/json", status_code=200)
        except Exception as e:
            logging.error(f"Error saving to database: {e}")
            return func.HttpResponse(f"Data was scraped, but there is an error saving to database: {e}", status_code=500)
    else:
        return func.HttpResponse(json.dumps({"error": "No departures found or station name is invalid"}), mimetype="application/json", status_code=400)

