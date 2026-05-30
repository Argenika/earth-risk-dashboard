from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"


@app.get("/earthquakes")
def earthquakes():
    data = requests.get(USGS_URL).json()

    result = []

    for e in data["features"][:30]:
        result.append({
            "place": e["properties"]["place"],
            "mag": e["properties"]["mag"],
            "time": e["properties"]["time"]
        })

    return {"earthquakes": result}
