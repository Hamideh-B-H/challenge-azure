import azure.functions as func
import logging
import requests
import json
import pyodbc
import time
from datetime import datetime
import os


# Create Function App
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@app.route(route="scraping_function")
def scraping_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("iRail liveboard function started")

    # -------------------------------
    # Step 1: Call iRail API
    # -------------------------------
    url = "https://api.irail.be/liveboard/"
    params = {
        "station": "Gent-Sint-Pieters",
        "format": "json"
    }
    headers = {
        "User-Agent": "Azure-project-irail/1.0 (becode.be; Hamideh@becode.education)"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error calling iRail API: {e}")
        return func.HttpResponse(f"API error: {e}", status_code=500)

    data = response.json()
    departures = data.get("departures", {}).get("departure", [])

    if not departures:
        return func.HttpResponse("No departures found.", status_code=200)

    # -------------------------------
    # Step 2: Prepare rows
    # -------------------------------
    station_name = "Gent-Sint-Pieters"
    fetched_at = datetime.utcnow()

    departure_rows = []
    for train in departures:
        departure_rows.append((
            station_name,
            train.get("station"),
            train.get("vehicle"),
            datetime.fromtimestamp(int(train.get("time"))),
            int(train.get("delay", 0)),
            train.get("platform"),
            fetched_at
        ))

    # -------------------------------
    # Step 3: Connect to Azure SQL (with retry logic)
    # -------------------------------
    
    max_retries = 5
    retry_delay = 10  # seconds
    conn = None
    cursor = None

    # Read SQL connection string from environment variable
    sql_connection_string = os.environ.get("SQL_CONNECTION_STRING")

    if not sql_connection_string:
        logging.error("SQL_CONNECTION_STRING environment variable is not set")
        return func.HttpResponse(
            "Server misconfigured: missing SQL connection string.",
            status_code=500
        )
    for attempt in range(1, max_retries + 1):
        try:
            logging.info(f"SQL connection attempt {attempt}/{max_retries}")

            # Connect to SQL securely via environment variable
            conn = pyodbc.connect(sql_connection_string)
            cursor = conn.cursor()
            logging.info("SQL connection established")
            break

        except pyodbc.Error as e:
            logging.warning(f"SQL connection failed: {e}")
            if attempt == max_retries:
                return func.HttpResponse(
                    "SQL database unavailable after retries.",
                    status_code=500
                )
            time.sleep(retry_delay)


    # -------------------------------
    # Step 4: Insert data in chunks
    # -------------------------------
    insert_query = """
        INSERT INTO train_departures (
            station,
            destination,
            vehicle,
            departure_time,
            delay_seconds,
            platform,
            fetched_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    batch_size = 20
    try:
        for batch in chunks(departure_rows, batch_size):
            cursor.executemany(insert_query, batch)
            conn.commit()
            logging.info(f"Inserted batch of {len(batch)} rows")

    except Exception as e:
        logging.error(f"Insert failed: {e}")
        return func.HttpResponse(f"Insert error: {e}", status_code=500)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    # -------------------------------
    # Step 5: Return response
    # -------------------------------
    return func.HttpResponse(
        json.dumps({
            "status": "success",
            "rows_inserted": len(departure_rows)
        }),
        mimetype="application/json",
        status_code=200
    )
