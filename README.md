# Sensor collector (RPi5)

Minimal project to read BME280 (I2C) and three analog probes (pH, TDS, DO) via ADS1115 and save to a local SQL database.

Quick start:

1. Enable I2C on the Raspberry Pi (`raspi-config` -> Interface Options -> I2C).
2. Create and activate venv, then install packages:

```bash
python3 -m venv ~/sensor-venv
source ~/sensor-venv/bin/activate
pip install -r requirements.txt
```

3. Configure DB: use SQLite (default) or run Postgres (Docker example):

```bash
docker run --name sensor-postgres -e POSTGRES_USER=sensor -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=sensordb -p 5432:5432 -d postgres:15
export DATABASE_URL=postgresql://sensor:secret@localhost:5432/sensordb
```

4. Run collector:

```bash
source ~/sensor-venv/bin/activate
python collector.py
```

Files:
- `sensors.py` — sensor reads (uses calibrated functions)
- `calibration.py` — calibration data and functions
- `db.py` — SQLAlchemy model and DB init
- `collector.py` — main loop to persist readings
- `sync.py` — sync local data to Cloudflare via HTTP ingest
- `export_ml.py` — export data to CSV for ML
- `.env.example` — env var examples

Next steps: calibrate probes, sync via Cloudflare tunnel, access dashboard from Vercel, use cloud data for ML.

## Cloud Setup (Cloudflare + Vercel)

1. **Cloudflare Tunnel:**
   - Run: `bash start_tunnel.sh` (starts API + Cloudflare Quick Tunnel)
   - Tunnel URL saved to `logs/tunnel_url.txt` (changes on each run)
   - Public URL accessible from anywhere

2. **Sync local to cloud:**
   - Cloudflare tunnel URL is automatically read from `logs/tunnel_url.txt`
   - Run: `python sync.py` to push local data via HTTP ingest
   - Set `INGEST_TOKEN` env var for authentication (optional)

3. **Dashboard:**
   - Deploy dashboard from `dashboard/` folder to Vercel
   - Dashboard auto-detects tunnel URL from `/api/tunnel-url` endpoint
   - Fallback to localhost (http://localhost:5000) for local dev

## Sync to Cloud

The sync.py script automatically reads the Cloudflare tunnel URL:

```bash
python sync.py
```

Run periodically (e.g., cron) to push local data to cloud.

**Environment variables:**
- `CLOUD_INGEST_URL`: Optional, if not set, tunnel URL is read from logs/tunnel_url.txt
- `INGEST_TOKEN`: Optional token for API authentication

## Export for ML

```bash
python export_ml.py  # Creates sensor_data.csv
```

## Calibration

Calibrate probes using known standards:

1. Measure voltage at known values (e.g., pH 4 and 10).
2. Update `calibration.py`:
   ```python
   from calibration import update_calibration
   update_calibration("ph", [(voltage1, value1), (voltage2, value2)])
   ```
3. Data saves to `calibration.json`.

Example:
```bash
python -c "from calibration import update_calibration; update_calibration('ph', [(1.0, 4.0), (2.0, 10.0)])"
```
