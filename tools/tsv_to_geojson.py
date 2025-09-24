#!/usr/bin/env python3
import csv, json, argparse, sys
from typing import List, Dict, Any

def to_float(s: str):
    try:
        return float(s.strip())
    except Exception:
        return None

def feature_bbox(lon: float, lat: float):
    # For points, bbox collapses to the same coordinate repeated
    return [lon, lat, lon, lat]

def convert_tsv_to_geojson(
    input_path: str,
    output_path: str,
    lat_field: str = "lat",
    lon_field: str = "lng",
    id_field: str = "id",
    keep_fields: List[str] = None
) -> None:
    """
    Convert TSV rows to a GeoJSON FeatureCollection of Points.

    - input_path: path to .tsv
    - output_path: path to .geojson
    - lat_field, lon_field: column names for latitude/longitude
    - id_field: column that becomes Feature 'id' (optional if not present)
    - keep_fields: which columns to copy into properties (default: all except lat/lon/id)
    """
    with open(input_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        fieldnames = reader.fieldnames or []

        if lat_field not in fieldnames or lon_field not in fieldnames:
            raise SystemExit(f"Missing required lat/lon fields: '{lat_field}', '{lon_field}'. Found: {fieldnames}")

        # Decide which fields to keep as properties
        if keep_fields is None:
            ignore = {lat_field, lon_field}
            if id_field in fieldnames:
                ignore.add(id_field)
            keep_fields = [c for c in fieldnames if c not in ignore]

        features: List[Dict[str, Any]] = []
        minx = miny = float("inf")
        maxx = maxy = float("-inf")

        for row in reader:
            lat = to_float(row.get(lat_field, ""))
            lon = to_float(row.get(lon_field, ""))
            if lat is None or lon is None:
                # skip rows without valid coordinates
                continue

            # properties
            props = {k: row.get(k, None) for k in keep_fields}

            # id (optional)
            fid = None
            if id_field in row and row[id_field] != "":
                try:
                    fid = int(row[id_field])
                except Exception:
                    # keep as string if not an int
                    fid = row[id_field]

            feat_bbox = [lon, lat, lon, lat]
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat],
                    "bbox": feat_bbox
                },
                "properties": props,
                **({"id": fid} if fid is not None else {}),
                "bbox": feat_bbox
            })

            # update collection bbox
            minx = min(minx, lon)
            miny = min(miny, lat)
            maxx = max(maxx, lon)
            maxy = max(maxy, lat)

        collection: Dict[str, Any] = {
            "type": "FeatureCollection",
            "features": features
        }
        if features:
            collection["bbox"] = [minx, miny, maxx, maxy]

    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(collection, out, ensure_ascii=False, indent=2)

def main():
    p = argparse.ArgumentParser(description="Convert a TSV with lat/lng columns to a GeoJSON FeatureCollection of Points.")
    p.add_argument("input", help="Input .tsv path")
    p.add_argument("output", help="Output .geojson path")
    p.add_argument("--lat", default="lat", help="Latitude column name (default: lat)")
    p.add_argument("--lon", default="lng", help="Longitude column name (default: lng)")
    p.add_argument("--id", dest="id_field", default="id", help="ID column name used for Feature.id (default: id)")
    p.add_argument("--keep", nargs="*", default=None, help="List of columns to keep as properties (default: auto)")
    args = p.parse_args()

    convert_tsv_to_geojson(
        input_path=args.input,
        output_path=args.output,
        lat_field=args.lat,
        lon_field=args.lon,
        id_field=args.id_field,
        keep_fields=args.keep
    )

if __name__ == "__main__":
    main()
