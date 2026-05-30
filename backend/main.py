from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import sqlite3
import threading
import time
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

db_lock = threading.Lock()


def get_conn():
    return sqlite3.connect("earth_risk.db", check_same_thread=False, timeout=20)


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS earthquakes (
            id TEXT PRIMARY KEY,
            place TEXT,
            mag REAL,
            time INTEGER
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            message TEXT,
            severity TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def create_alert(type, message, severity):
    with db_lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute(
            "INSERT INTO alerts (type, message, severity, created_at) VALUES (?,?,?,?)",
            (type, message, severity, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()


def fetch_earthquakes():
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    data = requests.get(url).json()

    with db_lock:
        conn = get_conn()
        c = conn.cursor()
        for e in data["features"][:50]:
            eq_id = e["id"]
            place = e["properties"]["place"]
            mag = e["properties"]["mag"]
            t = e["properties"]["time"]
            c.execute(
                "INSERT OR IGNORE INTO earthquakes VALUES (?,?,?,?)",
                (eq_id, place, mag, t)
            )
        conn.commit()
        conn.close()

    for e in data["features"][:50]:
        mag = e["properties"]["mag"]
        place = e["properties"]["place"]
        if mag and mag > 2:
            create_alert(
                "earthquake",
                f"Terremoto M{mag} en {place}",
                "high" if mag > 6 else "medium"
            )


def worker():
    while True:
        try:
            fetch_earthquakes()
        except Exception as ex:
            print(f"[worker error] {ex}")
        time.sleep(60)


@app.on_event("startup")
def startup():
    init_db()
    t = threading.Thread(target=worker, daemon=True)
    t.start()


@app.get("/earthquakes")
def earthquakes():
    with db_lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute(
            "SELECT place, mag, time FROM earthquakes ORDER BY time DESC LIMIT 30")
        rows = c.fetchall()
        conn.close()
    return {"earthquakes": [
        {"place": r[0], "mag": r[1], "time": r[2]} for r in rows
    ]}


@app.get("/alerts")
def alerts():
    with db_lock:
        conn = get_conn()
        c = conn.cursor()
        c.execute(
            "SELECT type, message, severity, created_at FROM alerts ORDER BY id DESC LIMIT 20")
        rows = c.fetchall()
        conn.close()
    return {"alerts": [
        {"type": r[0], "message": r[1], "severity": r[2], "created_at": r[3]} for r in rows
    ]}


@app.get("/health")
def health():
    return {"status": "ok"}
