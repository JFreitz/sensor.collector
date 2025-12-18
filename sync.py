#!/usr/bin/env python3
"""
Sync local SQLite data to cloud PostgreSQL (Railway).
Run periodically to keep cloud DB updated.
"""

import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db import SensorReading, init_db as init_local_db

load_dotenv()  # Load .env file

# Local SQLite
LOCAL_DB_URL = "sqlite:///sensors.db"
local_engine = create_engine(LOCAL_DB_URL, echo=False)
LocalSession = sessionmaker(bind=local_engine)

# Cloud PostgreSQL (set in .env or env var)
CLOUD_DB_URL = os.getenv("CLOUD_DATABASE_URL", "postgresql://user:pass@host:5432/dbname")

def sync_to_cloud():
    """Copy new readings from local to cloud."""
    print(f"CLOUD_DB_URL: {CLOUD_DB_URL}")
    if not CLOUD_DB_URL or CLOUD_DB_URL == "postgresql://user:pass@host:5432/dbname":
        print("CLOUD_DATABASE_URL not set. Skipping sync.")
        return

    cloud_engine = create_engine(CLOUD_DB_URL, echo=False)
    
    # Create table if not exists
    from db import Base
    Base.metadata.create_all(bind=cloud_engine)
    
    CloudSession = sessionmaker(bind=cloud_engine)

    # Get latest timestamp from cloud
    with CloudSession() as cloud_session:
        result = cloud_session.execute(text("SELECT MAX(timestamp) FROM sensor_readings")).scalar()
        last_sync = result if result else None

    # Get new readings from local
    with LocalSession() as local_session:
        query = local_session.query(SensorReading)
        if last_sync:
            query = query.filter(SensorReading.timestamp > last_sync)
        new_readings = query.all()

    if not new_readings:
        print("No new data to sync.")
        return

    # Insert into cloud
    with CloudSession() as cloud_session:
        for reading in new_readings:
            # Check if exists (avoid duplicates)
            exists = cloud_session.execute(
                text("SELECT 1 FROM sensor_readings WHERE timestamp = :ts AND sensor = :s"),
                {"ts": reading.timestamp, "s": reading.sensor}
            ).fetchone()
            if not exists:
                cloud_session.execute(
                    text("""
                        INSERT INTO sensor_readings (timestamp, sensor, value, unit, meta)
                        VALUES (:ts, :s, :v, :u, :m)
                    """),
                    {
                        "ts": reading.timestamp,
                        "s": reading.sensor,
                        "v": reading.value,
                        "u": reading.unit,
                        "m": json.dumps(reading.meta) if reading.meta else None
                    }
                )
        cloud_session.commit()

    print(f"Synced {len(new_readings)} readings to cloud.")

import time

import time

if __name__ == "__main__":
    try:
        while True:
            sync_to_cloud()
            time.sleep(1)  # 1 second interval for near real-time sync
    except KeyboardInterrupt:
        print("\nAuto-sync stopped by user.")