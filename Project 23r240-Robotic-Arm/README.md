# Robotic Arm Joint Health Monitoring System

Individual implementation for the System Automation bonus challenge.

## Contents
- `main.py` — deterministic safety stop, Random Forest wear model, technician-note analysis, sensor-spoofing checks, and four demo outcomes.
- `data/historical_joint_readings.csv` — 120 synthetic labeled historical readings.
- `logs/maintenance_notes.txt` — 10 sample technician notes, including relevant and irrelevant entries.
- `docs/design_explanation.md` — thresholds, decision logic, spoofing defense, and limitations.
- `test_main.py` — automated decision tests.

## Run on Windows
1. Install Python 3.10 or newer.
2. Open Command Prompt in this folder.
3. Install dependencies: `python -m pip install -r requirements.txt`
4. Run the program: `python main.py`
5. Run tests: `python -m unittest -v`

## Decision priority
1. Hard-limit crossing or invalid critical reading → `EMERGENCY_STOP`.
2. Sensor inconsistency / suspected spoofing → `SCHEDULE_MAINTENANCE`.
3. High-risk note or predicted wear probability ≥ 0.75 → `SCHEDULE_MAINTENANCE`.
4. Medium-risk note or predicted wear probability ≥ 0.40 → `MONITOR`.
5. Otherwise → `SAFE`.

All thresholds and historical readings are illustrative synthetic coursework data. Do not connect this prototype directly to real robot controls. Real equipment requires validated robot-specific limits, risk assessment, and independent safety-rated hardware.
