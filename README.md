# Hourly Weather Pipeline (n8n)

## Run n8n
docker run -it --rm -p 5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n
(or: npx n8n)  -> open http://localhost:5678

## Import
Workflows -> Import from File -> workflow.json
Open "Append to Google Sheet": attach Google credentials, set Sheet ID, add header row:
timestamp | city | temperature_c | humidity_pct | wind_kmh | precip_mm | heat_alert
Click "Execute Workflow" once, then toggle Active for hourly runs.

## Demo script (architecture)
1. Trigger: Schedule, every hour
2. Extract: HTTP GET Open-Meteo (no API key)
3. Transform: Python Code node -> flat record + heat_alert flag
4. Load: Google Sheets append (parallel branch)
5. Decision: IF temp >= 35 -> Set alert message (swap for Telegram/Email node)

## Execution proof
Executions tab -> show green run -> click each node to show input/output JSON; show new Sheet row.
