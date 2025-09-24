# Yangon Bus Service – YBS Data

YBS Data is forked from [YBS-Data](https://github.com/chitgyi/YBS-Data).

### ./data

- **./routes/** are json files that contain bus line information by ID, name, bus route as line shape and bus stop IDs in sequence.
  - Bus stop IDs are equals to ID in `stops.tsv`
  - `shape.geometry` is in geojson LineString format.
  - separated into respective json file for easier git versioning
- **stops.tsv** is in tsv format contains stop ID along with name, road, township.

### ./tools

- python scripts for importing/exporting to/from mongo

#### Export to SQLite DB

```bash
$ cd tools
$ python import_stops.py
$ python import_routes.py

# or

$ cd tools
$ ./export_db.sh
```

_DB Output - data/ybs.db_

---


#### Export to .geojson format
```
python tools/tsv_to_geojson.py data/stops.tsv data/stops.geojson \ 
  --lat lat \
  --lon lng \
  --id id
```