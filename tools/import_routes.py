# import_routes.py
import json
import os
import sqlite3
from pathlib import Path

BASE = Path(__file__).parent
db_path = BASE / "../data/ybs.db"
route_directory = BASE / "../data/routes/"

con = sqlite3.connect(db_path)
cur = con.cursor()

# Keep FKs ON for the final DB
cur.execute("PRAGMA foreign_keys = ON;")
cur.execute("BEGIN;")
try:
    # Drop in dependency-safe order
    cur.execute("DROP TABLE IF EXISTS route_stops;")
    cur.execute("DROP TABLE IF EXISTS coordinates;")
    cur.execute("DROP TABLE IF EXISTS routes;")

    # routes
    cur.execute("""
        CREATE TABLE routes (
            id             INTEGER PRIMARY KEY NOT NULL,
            route_id_name  TEXT    NOT NULL,
            color          TEXT    NOT NULL,
            name           TEXT    NOT NULL
        );
    """)

    # coordinates (NO ACTION on FK to match Room's default)
    cur.execute("""
        CREATE TABLE coordinates (
            id        INTEGER PRIMARY KEY NOT NULL,
            route_id  INTEGER NOT NULL,
            lat       REAL    NOT NULL,
            lng       REAL    NOT NULL,
            FOREIGN KEY (route_id) REFERENCES routes(id)
        );
    """)

    # route_stops (NO ACTION on both FKs, only the two expected index names)
    cur.execute("""
        CREATE TABLE route_stops (
            id        INTEGER PRIMARY KEY NOT NULL,
            route_id  INTEGER NOT NULL,
            stop_id   INTEGER NOT NULL,
            FOREIGN KEY (route_id) REFERENCES routes(id),
            FOREIGN KEY (stop_id)  REFERENCES stops(id)
        );
    """)
    # Create EXACT index names Room expects
    cur.execute("CREATE INDEX IF NOT EXISTS index_route_stops_route_id ON route_stops(route_id);")
    cur.execute("CREATE INDEX IF NOT EXISTS index_route_stops_stop_id  ON route_stops(stop_id);")

    # Load route JSON files
    for filename in os.listdir(route_directory):
        if not filename.endswith(".json"):
            continue

        with open(route_directory / filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Insert route
        cur.execute(
            "INSERT INTO routes (route_id_name, color, name) VALUES (?, ?, ?);",
            (data["route_id"], data["color"], data["name"])
        )
        route_id = cur.lastrowid

        # GeoJSON coords are commonly [lng, lat]—flip to (lat, lng)
        coords_rows = []
        for coord in data["shape"]["geometry"]["coordinates"]:
            lng = float(coord[0])
            lat = float(coord[1])
            coords_rows.append((route_id, lat, lng))

        cur.executemany(
            "INSERT INTO coordinates (route_id, lat, lng) VALUES (?, ?, ?);",
            coords_rows
        )

        # Insert route_stops (JSON contains stop IDs)
        route_stop_rows = [(route_id, int(stop_id)) for stop_id in data["stops"]]
        cur.executemany(
            "INSERT INTO route_stops (route_id, stop_id) VALUES (?, ?);",
            route_stop_rows
        )

    cur.execute("COMMIT;")
finally:
    cur.execute("PRAGMA foreign_keys = ON;")
    con.close()