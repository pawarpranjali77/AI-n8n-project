# Hourly Weather Data Pipeline for Pune (n8n)

An automated **Hourly Weather Data Pipeline** built using [n8n](https://n8n.io/) that collects real-time weather data for Pune, transforms it into structured records, stores it in Google Sheets, and generates heat alerts when the temperature reaches 35°C or above.

This project demonstrates **ETL (Extract, Transform, Load), workflow automation, API integration, data processing, conditional logic, and error handling** under the *IoT & Hardware Data Pipelines* theme.

## Project Overview

Weather conditions can change rapidly, making manual data collection inefficient and unreliable. This project automates hourly weather monitoring and maintains a historical dataset that can be used for visualization, trend analysis, and future forecasting.

### Key Features

- **Automated Scheduling:** Runs every hour using an n8n Schedule Trigger.
- **Weather Data Extraction:** Fetches weather information from the Open-Meteo API without requiring an API key.
- **Data Transformation:** Converts nested API responses into a clean, structured record.
- **Historical Data Storage:** Appends each record to Google Sheets.
- **Heat Alert Detection:** Flags temperatures greater than or equal to 35°C.
- **Error Handling:** Uses a separate Error Handler workflow to capture workflow failures.
- **Python Reference Implementation:** Includes `pipeline.py` to demonstrate the same pipeline logic independently.
- **Sample Dataset:** Includes `weather_log.csv` as a sample output record.

## Architecture

The pipeline follows an ETL workflow with an additional decision-making stage.

```text
Schedule Trigger (Every Hour)
             |
             v
HTTP Request — Open-Meteo API
             |
             v
Code Node — Transform Weather Data
             |
             v
     Structured Record
             |
       +-----+-----+
       |           |
       v           v
Google Sheets    IF Node
Append Row       Temperature >= 35°C?
                   |
              +----+----+
              |         |
             True      False
              |
              v
         Set Node
      Build Heat Alert
              |
              v
       Alert Message
   (Ready for Integration)

Separate Error Handler Workflow
             |
             v
 Capture Workflow Failure
```

## ETL Pipeline

### 1. Extract — Weather API

The Schedule Trigger initiates the workflow every hour. An HTTP Request node sends a GET request to Open-Meteo using Pune's geographical coordinates.

**API:** [Open-Meteo Forecast API](https://open-meteo.com/en/docs)

The API provides weather parameters such as:

- Temperature (°C)
- Relative humidity (%)
- Wind speed (km/h)
- Precipitation (mm)
- Observation timestamp

No API key is required for standard non-commercial use.

### 2. Transform — Data Processing

The Code node processes the API response and extracts the relevant fields into a flat record.

Example output:

```json
{
  "timestamp": "2026-10-12T04:00",
  "city": "Pune",
  "temperature_c": 36,
  "humidity_pct": 62,
  "wind_kmh": 12,
  "precip_mm": 0,
  "heat_alert": true
}
```

*The values above are illustrative sample data, not a live weather observation.*

The `heat_alert` field is calculated using the following condition:

```javascript
const heatAlert = temperature >= 35;
```

**Note:** The Code node should use JavaScript for compatibility with standard n8n Code node execution. If using Python, verify that the required Python execution environment is configured and supported by your n8n installation.

### 3. Load — Google Sheets

The transformed record is appended to a Google Sheet, creating a historical weather dataset.

Configure the spreadsheet with the following column headers:

| Column | Description |
|---|---|
| `timestamp` | Weather observation time |
| `city` | City name |
| `temperature_c` | Temperature in Celsius |
| `humidity_pct` | Relative humidity percentage |
| `wind_kmh` | Wind speed in km/h |
| `precip_mm` | Precipitation in millimetres |
| `heat_alert` | Boolean heat-alert flag |

Each successful workflow execution should append a new row rather than overwrite previous records.

### 4. Decide — Heat Alert Logic

An IF node checks whether the temperature is greater than or equal to 35°C.

- **True:** A Set node constructs a heat-alert message.
- **False:** The workflow continues without generating a heat alert.

Example alert:

```text
HEAT ALERT | Pune | 36°C | 2026-10-12T04:00
```

The generated message can be connected to a Telegram, email, or other notification node for actual alert delivery.

**Current scope:** Building an alert message does not itself send a notification. A messaging integration must be configured to deliver it.

### 5. Error Handling

A separate Error Handler workflow is designed to capture execution failures, such as API errors or failed node operations.

It can record details such as:

- Workflow name
- Failed node
- Error message
- Execution details, where available

The error workflow must be configured as an error workflow in n8n and assigned to the relevant workflow before failure handling can be demonstrated.

## Technology Stack

| Technology | Purpose |
|---|---|
| n8n | Workflow automation and orchestration |
| Open-Meteo API | Weather data source |
| HTTP Request | API communication |
| JavaScript Code node | Data transformation and alert calculation |
| Google Sheets | Historical data storage |
| Python | Standalone reference implementation |
| CSV | Sample weather dataset |
| Docker / Node.js | Running n8n locally |

## Project Structure

```text
Hourly-Weather-Pipeline/
├── workflow.json
├── pipeline.py
├── weather_log.csv
├── README.md
└── Error Handler Workflow
```

The exact file structure may vary depending on how the workflows and supporting files are stored.

## Installation and Setup

### Prerequisites

- Docker or Node.js/npm
- n8n
- A Google account
- Google Sheets credentials configured in n8n
- Internet access for the weather API

### Step 1: Start n8n

Using Docker:

```bash
docker run -it --rm \
  -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  docker.n8n.io/n8nio/n8n
```

Alternatively, if n8n is installed locally:

```bash
npx n8n
```

Open [http://localhost:5678](http://localhost:5678).

**Important:** The Docker command above uses `--rm`, so the container is removed when stopped. The named volume preserves n8n data, but workflow and credential persistence should be verified before using this configuration for a long-running deployment.

### Step 2: Import the Workflow

1. Open n8n.
2. Navigate to **Workflows**.
3. Select **Import from File**.
4. Import `workflow.json`.
5. Review the imported nodes and their connections.

### Step 3: Configure the Hourly Trigger

1. Open the trigger node.
2. Replace the Manual Trigger with a **Schedule Trigger** if the workflow still uses a manual trigger.
3. Set the interval to every hour.
4. Save the workflow.
5. Activate the workflow.

A manual execution is useful for testing, but it does not establish that the workflow runs automatically every hour.

### Step 4: Configure Google Sheets

1. Open the Google Sheets node.
2. Connect your Google credentials.
3. Select the target spreadsheet and worksheet.
4. Configure the append-row operation.
5. Add the required column headers in the first row.
6. Verify that the node maps each field to the correct column.

### Step 5: Test the Pipeline

1. Execute the workflow manually once.
2. Verify the HTTP Request output.
3. Inspect the transformed record in the Code node.
4. Confirm that a new row appears in Google Sheets.
5. Test both branches of the heat-alert condition using appropriate sample temperatures.
6. Test the Error Handler workflow separately or through a controlled failure.
7. Activate the workflow for scheduled executions.

## Execution Verification

Use the n8n **Executions** tab to demonstrate the pipeline.

Verify the following:

- A successful execution is recorded.
- The HTTP Request node returns weather data.
- The Code node produces a correctly formatted record.
- The Google Sheets node appends the record successfully.
- The IF node evaluates the temperature condition correctly.
- The alert message is generated when the condition is true.
- The Error Handler workflow is configured and responds to a test failure.

For the final demonstration, show the execution details alongside the newly appended Google Sheets row.

## Troubleshooting

| Issue | Suggested Fix |
|---|---|
| Workflow does not run hourly | Configure a Schedule Trigger and activate the workflow. |
| Python runner unavailable | Rewrite the transformation logic in JavaScript or configure a supported Python execution environment. |
| Google Sheets node fails | Verify credentials, spreadsheet access, worksheet selection, and column mappings. |
| API request fails | Check internet connectivity, request parameters, and API response details. |
| No heat alert appears | Test with a temperature of 35°C or higher and inspect the IF node condition. |
| Error Handler does not run | Assign the error workflow in the main workflow's settings and test a controlled failure. |
| Duplicate or missing records | Inspect execution frequency, append configuration, and field mappings. |

## Future Enhancements

- Monitor multiple cities and weather stations.
- Send automatic alerts through Telegram or email.
- Build a live dashboard using historical weather records.
- Analyse temperature and rainfall trends.
- Add retries and more detailed failure logging.
- Integrate weather forecasting and anomaly detection.
- Deploy the workflow on a persistent server for continuous monitoring.

## Conclusion

The Hourly Weather Data Pipeline demonstrates how workflow automation can collect external data, transform it into a structured format, store historical records, and apply threshold-based decision logic.

By combining n8n, Open-Meteo, JavaScript, and Google Sheets, the project provides a modular foundation for automated environmental monitoring and future data-driven applications.

**Project Theme:** IoT & Hardware Data Pipelines  
**Pipeline Type:** Scheduled ETL with conditional alert generation  
**Primary Location:** Pune, Maharashtra, India
