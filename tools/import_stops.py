# import_stops.py
import csv
import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "../data/ybs.db"
stops_tsv_path = Path(__file__).parent / "../data/stops.tsv"

con = sqlite3.connect(db_path)
con.execute("PRAGMA foreign_keys = ON;")
cur = con.cursor()

cur.execute("BEGIN;")
try:
    cur.execute("DROP TABLE IF EXISTS stops;")
    cur.execute("""
        CREATE TABLE stops (
            id            INTEGER PRIMARY KEY NOT NULL,
            lat           REAL    NOT NULL,
            lng           REAL    NOT NULL,
            name_en       TEXT    NOT NULL,
            name_mm       TEXT    NOT NULL,
            road_en       TEXT    NOT NULL,
            road_mm       TEXT    NOT NULL,
            township_en   TEXT    NOT NULL,
            township_mm   TEXT    NOT NULL
        );
    """)

    with open(stops_tsv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader, None)  # skip header
        rows = []
        for r in reader:
            # Ensure correct types: id:int, lat/lng:float
            rid = int(r[0])
            lat = float(r[1])
            lng = float(r[2])
            rows.append((
                rid, lat, lng,
                r[3], r[4],  # name_en, name_mm
                r[5], r[6],  # road_en, road_mm
                r[7], r[8],  # township_en, township_mm
            ))

    cur.executemany("""
        INSERT INTO stops (id, lat, lng, name_en, name_mm, road_en, road_mm, township_en, township_mm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, rows)

    # Optional: an index to speed up name searches (not required for Room)
    # cur.execute("CREATE INDEX IF NOT EXISTS idx_stops_name_en ON stops(name_en);")

    con.commit()
finally:
    if con.in_transaction:
        con.rollback()
    con.close()