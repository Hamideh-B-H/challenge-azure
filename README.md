# Azure Train Data Project with iRail API (HTTP Function)
## Project Overview

This project fetches live train departure data from the iRail API
 and stores it in an Azure SQL Database using a Python Azure Function.

Current implementation:

-HTTP Function: fetches train data on demand and inserts it into Azure SQL

-Retry logic for SQL connections to ensure reliability

-This setup forms the foundation for future automation and dashboard features.

## Project Structure

`````
challenge-azure/
│
├── function_app.py           
├── .venv/                   
├── host.json                
├── local.settings.json      
├── requirements.txt           
├── README.md
`````
## How to Run Locally

1. Create your own local.settings.json in the project root. Example template:

`````
{
  "IsEncrypted": false,
  "Values": {
    "SQL_CONNECTION_STRING": "DRIVER={ODBC Driver 18 for SQL Server};SERVER=<your-server>;DATABASE=<your-db>;UID=<your-user>;PWD=<your-password>;Encrypt=yes;",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "<your-storage-connection-string>"
  }
}

`````
2. Activate the virtual environment (PowerShell):
`````
. .venv\Scripts\Activate.ps1
`````

3. Install dependencies:
`````
ython -m pip install -r requirements.txt
`````
4. Start the Functions host:
`````
func start
`````

5. Test the HTTP function:
The console will print a URL, for example:
`````
http://localhost:7071/api/scraping_function
`````
**Note**: Each request fetches the latest train departures for the station defined in the code (Gent-Sint-Pieters) and inserts them into the SQL database. You must have a valid SQL connection string in local.settings.json for this to work.

## Features Implemented
`````
HTTP function to fetch data	✅ Completed
SQL insert with retry logic	✅ Completed
Logging	                    ✅ Basic
Deployment to Azure	        ✅ Completed
`````

## Project Highlights
During development, the following steps and techniques were applied:

**Azure Functions (HTTP Trigger):** Implemented a serverless Python function to fetch train data on demand.

**API Integration:** Connected to the iRail API and handled JSON responses to extract relevant departure information.

**Data Normalization & Validation:** Converted timestamps, handled missing fields, and structured data to fit SQL tables.

**SQL Database Integration:** Used pyodbc with retry logic to ensure stable insertion of batches of data.

**Environment Management:** Stored sensitive connection strings in local.settings.json (excluded from Git) and used environment variables in code.

**Testing & Debugging:** Verified local execution via the Azure Functions Core Tools and logged detailed information for troubleshooting.

This project demonstrates a practical workflow for serverless data ingestion and cloud-based data management, laying the foundation for future automation and live dashboards.


## Timeline 

This project was completed over 5 days, focusing on creating a cloud-based pipeline to fetch live train departure data from the iRail API and store it in an Azure SQL Database. This project was created as part of the AI Boocamp at BeCode.org.

Connect with me on LinkedIn: https://www.linkedin.com/in/hamideh-be/

