from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"


@app.get("/earthquakes")
def earthquakes():
    data = requests.get(USGS_URL).json()

    earthquakes = []

    for e in data["features"][:50]:
        props = e["properties"]
        coords = e["geometry"]["coordinates"]

        earthquakes.append({
            "place": props["place"],
            "mag": props["mag"],
            "time": props["time"],
            "lat": coords[1],
            "lon": coords[0]
        })

    return {"earthquakes": earthquakes}


@app.get("/alerts")
def alerts():
    data = requests.get(USGS_URL).json()

    alerts = []

    for e in data["features"][:50]:
        mag = e["properties"]["mag"]
        place = e["properties"]["place"]

        if mag and mag > 4:
            alerts.append({
                "type": "earthquake",
                "message": f"Terremoto M{mag} en {place}",
                "severity": "high" if mag > 6 else "medium",
                "created_at": datetime.now().isoformat()
            })

    return {"alerts": alerts}


@app.get("/health")
def health():
    return {"status": "ok"}
