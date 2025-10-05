#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_PATH="$SCRIPT_DIR/../data/ybs.db"

rm -f "$DB_PATH"

python "$SCRIPT_DIR/import_stops.py"
python "$SCRIPT_DIR/import_routes.py"

echo "✅ ybs.db generated at $DB_PATH"