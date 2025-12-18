#!/usr/bin/env python3
"""
Export sensor data to CSV for ML training.
Run locally or on cloud DB.
"""

import csv
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DB_URL = os.getenv("DATABASE_URL", "sqlite:///sensors.db")  # Local or cloud
engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)

def export_to_csv(filename="sensor_data.csv"):
    """Export all readings to CSV."""
    with Session() as session:
        readings = session.execute(text("""
            SELECT timestamp, sensor, value, unit, meta
            FROM sensor_readings
            ORDER BY timestamp
        """)).fetchall()

    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "sensor", "value", "unit", "meta"])
        for row in readings:
            writer.writerow(row)

    print(f"Exported {len(readings)} rows to {filename}.")

if __name__ == "__main__":
    export_to_csv()