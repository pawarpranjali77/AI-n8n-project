"""Builds workflow.json (importable into n8n) for the hourly weather pipeline."""
import json

CITY, LAT, LON, THRESHOLD = "Pune", 18.5204, 73.8567, 35
URL = (f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}"
       "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"
       "&timezone=Asia%2FKolkata")

PY_CODE = f'''out = []
for item in _input.all():
    c = item.json["current"]
    t = c["temperature_2m"]
    out.append({{"json": {{
        "timestamp": c["time"],
        "city": "{CITY}",
        "temperature_c": t,
        "humidity_pct": c["relative_humidity_2m"],
        "wind_kmh": c["wind_speed_10m"],
        "precip_mm": c["precipitation"],
        "heat_alert": t >= {THRESHOLD},
    }}}})
return out'''

nodes = [
  {"id": "n1", "name": "Every Hour", "type": "n8n-nodes-base.scheduleTrigger", "typeVersion": 1.2,
   "position": [0, 0], "parameters": {"rule": {"interval": [{"field": "hours", "hoursInterval": 1}]}}},
  {"id": "n2", "name": "Fetch Weather (Open-Meteo)", "type": "n8n-nodes-base.httpRequest", "typeVersion": 4.2,
   "position": [220, 0], "parameters": {"method": "GET", "url": URL, "options": {}}},
  {"id": "n3", "name": "Clean & Flag (Python)", "type": "n8n-nodes-base.code", "typeVersion": 2,
   "position": [440, 0], "parameters": {"language": "python", "pythonCode": PY_CODE}},
  {"id": "n4", "name": "Append to Google Sheet", "type": "n8n-nodes-base.googleSheets", "typeVersion": 4.5,
   "position": [680, -100], "parameters": {
     "resource": "sheet", "operation": "append",
     "documentId": {"__rl": True, "mode": "id", "value": "YOUR_GOOGLE_SHEET_ID"},
     "sheetName": {"__rl": True, "mode": "name", "value": "Sheet1"},
     "columns": {"mappingMode": "autoMapInputData", "value": None}, "options": {}}},
  {"id": "n5", "name": f"Temp >= {THRESHOLD}C?", "type": "n8n-nodes-base.if", "typeVersion": 2,
   "position": [680, 100], "parameters": {"conditions": {
     "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
     "conditions": [{"id": "c1", "leftValue": "={{ $json.temperature_c }}", "rightValue": THRESHOLD,
                     "operator": {"type": "number", "operation": "gte"}}],
     "combinator": "and"}, "options": {}}},
  {"id": "n6", "name": "Build Alert Message", "type": "n8n-nodes-base.set", "typeVersion": 3.4,
   "position": [920, 40], "parameters": {"assignments": {"assignments": [
     {"id": "a1", "name": "alert", "type": "string",
      "value": "=HEAT ALERT {{ $json.city }}: {{ $json.temperature_c }}C at {{ $json.timestamp }}"}]},
     "options": {}}},
]
conn = {
  "Every Hour": {"main": [[{"node": "Fetch Weather (Open-Meteo)", "type": "main", "index": 0}]]},
  "Fetch Weather (Open-Meteo)": {"main": [[{"node": "Clean & Flag (Python)", "type": "main", "index": 0}]]},
  "Clean & Flag (Python)": {"main": [[{"node": "Append to Google Sheet", "type": "main", "index": 0},
                                      {"node": f"Temp >= {THRESHOLD}C?", "type": "main", "index": 0}]]},
  f"Temp >= {THRESHOLD}C?": {"main": [[{"node": "Build Alert Message", "type": "main", "index": 0}], []]},
}
wf = {"name": "Hourly Weather Pipeline", "nodes": nodes, "connections": conn,
      "settings": {"executionOrder": "v1"}}
json.dump(wf, open("workflow.json", "w"), indent=2)
print("workflow.json written")
