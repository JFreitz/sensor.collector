#!/usr/bin/env python3
"""
Calibration module for pH, TDS, DO probes.
Load/save calibration data from JSON.
"""

import json
import os
from typing import Dict, Tuple

CALIBRATION_FILE = "calibration.json"

def load_calibration() -> Dict[str, Dict[str, float]]:
    """Load calibration data from JSON file."""
    if os.path.exists(CALIBRATION_FILE):
        with open(CALIBRATION_FILE, "r") as f:
            return json.load(f)
    return {
        "ph": {"slope": 14.0 / 3.3, "offset": 0.0},  # Default linear
        "tds": {"slope": 2000.0 / 3.3, "offset": 0.0},
        "do": {"slope": 14.0 / 3.3, "offset": 0.0}
    }

def save_calibration(cal_data: Dict[str, Dict[str, float]]):
    """Save calibration data to JSON."""
    with open(CALIBRATION_FILE, "w") as f:
        json.dump(cal_data, f, indent=2)

def calibrate_ph(voltage: float) -> float:
    """Calibrate pH from voltage using linear model: pH = slope * voltage + offset."""
    cal = load_calibration()["ph"]
    return max(0.0, cal["slope"] * voltage + cal["offset"])

def calibrate_tds(voltage: float) -> float:
    """Calibrate TDS (ppm) from voltage."""
    cal = load_calibration()["tds"]
    return max(0.0, cal["slope"] * voltage + cal["offset"])

def calibrate_do(voltage: float) -> float:
    """Calibrate DO (mg/L) from voltage."""
    cal = load_calibration()["do"]
    return max(0.0, cal["slope"] * voltage + cal["offset"])

# Example calibration points (replace with real measurements)
# pH: voltage 1.0V = pH 4, voltage 2.0V = pH 10
# TDS: voltage 0.5V = 0 ppm, voltage 2.5V = 1000 ppm
# DO: voltage 0.0V = 0 mg/L, voltage 3.3V = 14 mg/L

def update_calibration(sensor: str, points: list[Tuple[float, float]]):
    """Update calibration for a sensor using linear regression on points (voltage, value)."""
    if len(points) < 2:
        raise ValueError("Need at least 2 calibration points")
    
    voltages = [p[0] for p in points]
    values = [p[1] for p in points]
    
    # Linear fit: value = slope * voltage + offset
    n = len(points)
    sum_v = sum(voltages)
    sum_val = sum(values)
    sum_v_val = sum(v * val for v, val in points)
    sum_v2 = sum(v**2 for v in voltages)
    
    slope = (n * sum_v_val - sum_v * sum_val) / (n * sum_v2 - sum_v**2)
    offset = (sum_val - slope * sum_v) / n
    
    cal_data = load_calibration()
    cal_data[sensor] = {"slope": slope, "offset": offset}
    save_calibration(cal_data)
    print(f"Updated {sensor} calibration: slope={slope:.4f}, offset={offset:.4f}")

if __name__ == "__main__":
    # Example: Calibrate pH with points (1.0V, 4.0 pH), (2.0V, 10.0 pH)
    update_calibration("ph", [(1.0, 4.0), (2.0, 10.0)])
    print("Calibration updated.")