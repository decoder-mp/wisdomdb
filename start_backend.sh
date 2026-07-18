#!/usr/bin/env bash
set -euo pipefail

echo "Inspecting effective DATABASE_URL target..."
python - <<'PY'
import os
import re
from urllib.parse import urlparse

raw = os.getenv("DATABASE_URL", "")
if not raw:
	print("DATABASE_URL is missing at runtime")
else:
	try:
		parsed = urlparse(raw)
		host = parsed.hostname or "unknown-host"
		db_name = (parsed.path or "").lstrip("/") or "unknown-db"
		scheme = parsed.scheme or "unknown-scheme"
		print(f"DATABASE_URL target: scheme={scheme} host={host} db={db_name}")

		required_host_regex = os.getenv("DATABASE_HOST_REGEX", "").strip()
		if required_host_regex:
			if not re.search(required_host_regex, host):
				print(
					"DATABASE_URL host validation failed: "
					f"host '{host}' does not match DATABASE_HOST_REGEX='{required_host_regex}'"
				)
				raise SystemExit(1)
			print("DATABASE_URL host validation passed")
	except Exception as exc:
		print(f"DATABASE_URL parse error: {exc}")
		raise
PY

if [[ "${DATABASE_URL:-}" == sqlite* ]]; then
	echo "SQLite detected: skipping Alembic migrations and initializing schema directly..."
	python -c "from core.init_db import init_db; init_db()"
else
	echo "Running Alembic migrations..."
	python -m alembic upgrade head
fi

echo "Checking whether demo data should be seeded..."
python - <<'PY'
from core.database import SessionLocal
from models.lore import Lore

db = SessionLocal()
try:
	should_seed = db.query(Lore).count() == 0
finally:
	db.close()

if should_seed:
	print("No lore found. Seeding demo dataset...")
	from scripts.seed_data import seed, _reset
	db = SessionLocal()
	try:
		_reset(db)
	finally:
		db.close()
	seed()
else:
	print("Existing lore found. Skipping seed.")
PY

echo "Starting FastAPI server..."
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}"
