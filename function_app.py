import azure.functions as func
import logging
import requests
import json
import pyodbc
from datetime import datetime
import os

app = func.FunctionApp()

def fetch_ghent_departures():
    logging.info('iRail liveboard function started')

    # API setup / fetching data
    url = "https://api.irail.be/liveboard/"
    params = {"station": "Ghent-Sint-Pieters", "format": "json", "lang": "en"}
    headers = {"User-Agent": "Azure-project-irail/1.0 (becode.be; {my_email})"}
        
    # Calling the API
    try: 
        response = requests.get(url, params=params, headers=headers, timeout=60)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        logging.error(f"Error calling iRail API: {e}")
        return {"status": 500, "body": f"Error calling iRail API: {e}", "mimetype": "text/plain"}

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

    # Saving to Azure SQL Database + removing duplicates
    if processed_departures:
        try:
            connection_string = os.getenv("SQL_AZURE_CONNECTION")
            if not connection_string:
                return {"status": 500, "body": "Error: SQL_AZURE_CONNECTION missing.", "mimetype": "text/plain"}
            
            with pyodbc.connect(connection_string) as conn:
                with conn.cursor() as cursor:
                    # The SQL now handles both Updating and Inserting
                    sql = """
                        MERGE INTO GhentDepartures AS target
                        USING (SELECT ? AS vehicle, CAST(? AS DATETIME) AS departure_time) AS source
                        ON (target.vehicle = source.vehicle AND target.departure_time = source.departure_time)
                        
                        WHEN MATCHED THEN
                            UPDATE SET 
                                target.delay_in_seconds = ?, 
                                target.platform = ?, 
                                target.canceled = ?

                        WHEN NOT MATCHED THEN
                            INSERT (vehicle, train_number, train_type, departure_time, platform, delay_in_seconds, canceled, destination)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """
                    
                    for d in processed_departures:
                        # We strip microseconds to ensure SQL matches the time perfectly
                        clean_time = datetime.fromisoformat(d['departure_time']).replace(microsecond=0).isoformat()

                        params = (
                            # ON clause (Source selection)
                            d['vehicle'], clean_time,
                            
                            # WHEN MATCHED (Updates)
                            d['delay_in_seconds'], d['platform'], d['canceled'],
                            
                            # WHEN NOT MATCHED (Inserts)
                            d['vehicle'], d['train_number'], d['train_type'], 
                            clean_time, d['platform'], d['delay_in_seconds'], 
                            d['canceled'], d['destination']
                        )
                        cursor.execute(sql, params)
                    conn.commit()
            return {"status": 200, "body": json.dumps(processed_departures, indent=2), "mimetype": "application/json"}
                    
        except Exception as e:
            logging.error(f"Error saving to database: {e}")
            return {"status": 500, "body": f"Data scraped, but DB error: {e}", "mimetype": "text/plain"}
    else:
        return {
                "status": 404, 
                "body": json.dumps({"error": "No departures found for this station"}), 
                "mimetype": "application/json"
                }
    
# --- TRIGGER 1: HTTP (Manual) ---
@app.route(route="fetch_ghent_departures", auth_level=func.AuthLevel.ANONYMOUS)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    result = fetch_ghent_departures()
    # We return the HTTP response just like before
    return func.HttpResponse(
        result["body"], 
        status_code=result["status"],
        mimetype=result.get("mimetype")
    )

# --- TRIGGER 2: TIMER (Automatic) ---
# Runs every 10 minutes: "0 */10 * * * *"
@app.timer_trigger(schedule="0 */10 * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=False) 
def timer_ghent_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is running late!')
    
    # We call the same logic, but we don't return an HTTP response (timers don't have browsers)
    result = fetch_ghent_departures()
    logging.info(f"Timer run finished with status: {result['status']}")