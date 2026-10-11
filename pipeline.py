"""Plain-Python equivalent of the n8n workflow (fallback / logic check).
Run once:  python pipeline.py        Run hourly: python pipeline.py --loop
"""
import csv, os, sys, time, requests

CITY, LAT, LON, THRESHOLD = "Pune", 18.5204, 73.8567, 35
URL = "https://api.open-meteo.com/v1/forecast"
PARAMS = {"latitude": LAT, "longitude": LON, "timezone": "Asia/Kolkata",
          "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation"}
CSV_FILE = "weather_log.csv"

def fetch():                      # == HTTP Request node
    r = requests.get(URL, params=PARAMS, timeout=15)
    r.raise_for_status()
    return r.json()["current"]

def transform(c):                 # == Code node
    return {"timestamp": c["time"], "city": CITY, "temperature_c": c["temperature_2m"],
            "humidity_pct": c["relative_humidity_2m"], "wind_kmh": c["wind_speed_10m"],
            "precip_mm": c["precipitation"], "heat_alert": c["temperature_2m"] >= THRESHOLD}

def store(row):                   # == Google Sheets node
    new = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        if new: w.writeheader()
        w.writerow(row)

def run():
    row = transform(fetch())
    store(row)
    print(row)
    if row["heat_alert"]:         # == IF + Set nodes
        print(f"HEAT ALERT {row['city']}: {row['temperature_c']}C at {row['timestamp']}")

if __name__ == "__main__":
    while True:
        run()
        if "--loop" not in sys.argv: break
        time.sleep(3600)
