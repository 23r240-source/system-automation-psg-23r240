"""
Robotic Arm Joint Health Monitoring System
Individual assignment implementation.

Safety note: This is a synthetic educational prototype, not a certified industrial safety controller.
For real equipment, implement hardwired safety circuits and validate thresholds with the robot manufacturer.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "historical_joint_readings.csv"

LIMITS = {
    "torque_nm": 85.0,
    "temperature_c": 90.0,
    "vibration_mm_s": 18.0,
    "warning_torque_nm": 65.0,
    "warning_temperature_c": 75.0,
    "warning_vibration_mm_s": 10.0,
}
FEATURES = ["torque_nm", "temperature_c", "vibration_mm_s"]
JOINTS = ("shoulder", "elbow", "wrist")
ARMS = ("ARM-01", "ARM-02", "ARM-03", "ARM-04", "ARM-05", "ARM-06")

HIGH_RISK_TERMS = (
    "overheat", "overheating", "grinding", "metallic noise", "crack",
    "seized", "excessive vibration", "burning smell", "torque spike",
    "joint jam", "oil leak", "abnormal backlash", "bearing damage",
)
MEDIUM_RISK_TERMS = (
    "noise", "warm", "lubrication", "backlash", "drift", "intermittent",
    "rough movement", "inspection required", "vibration",
)


def _load_csv_rows(path: Path = DATA_PATH) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key in FEATURES:
            row[key] = float(row[key])
        row["wear_label"] = int(row["wear_label"])
    return rows


def train_wear_model():
    """Train a RandomForest classifier on included synthetic labeled history."""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.metrics import accuracy_score
    except ImportError as exc:
        raise RuntimeError("Missing dependency. Run: pip install -r requirements.txt") from exc

    rows = _load_csv_rows()
    X = [[r[k] for k in FEATURES] for r in rows]
    y = [r["wear_label"] for r in rows]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    model = RandomForestClassifier(
        n_estimators=160, max_depth=5, class_weight="balanced", random_state=42
    )
    model.fit(X_train, y_train)
    return model, accuracy_score(y_test, model.predict(X_test))


def immediate_safety_stop(joint_readings: dict[str, dict[str, float]]) -> tuple[bool, list[str]]:
    """Deterministic safety check, independent of ML inference."""
    reasons = []
    for joint, reading in joint_readings.items():
        for key, limit in (
            ("torque_nm", LIMITS["torque_nm"]),
            ("temperature_c", LIMITS["temperature_c"]),
            ("vibration_mm_s", LIMITS["vibration_mm_s"]),
        ):
            value = float(reading[key])
            if not math.isfinite(value) or value < 0:
                reasons.append(f"{joint}: invalid {key} reading ({value})")
            elif value >= limit:
                reasons.append(f"{joint}: {key}={value:.1f} crosses hard limit {limit:.1f}")
    return bool(reasons), reasons


def detect_spoofed_sensor(
    joint_readings: dict[str, dict[str, float]],
    previous_readings: dict[str, dict[str, float]] | None = None,
) -> tuple[bool, list[str]]:
    """Flag invalid values and a few simple cross-sensor/temporal inconsistencies."""
    alerts = []
    for joint, r in joint_readings.items():
        torque, temp, vibration = (float(r[k]) for k in FEATURES)
        if not all(math.isfinite(v) and v >= 0 for v in (torque, temp, vibration)):
            alerts.append(f"{joint}: invalid sensor value")
            continue
        if vibration >= 12 and temp >= 70 and torque < 12:
            alerts.append(
                f"{joint}: suspicious low torque ({torque:.1f}) conflicts with "
                f"vibration ({vibration:.1f}) and temperature ({temp:.1f})"
            )
        if previous_readings and joint in previous_readings:
            old_torque = float(previous_readings[joint]["torque_nm"])
            if old_torque > 25 and torque < old_torque * 0.25 and vibration >= 10:
                alerts.append(
                    f"{joint}: abrupt torque drop from {old_torque:.1f} to {torque:.1f} "
                    "while vibration remains elevated"
                )
    return bool(alerts), alerts


def scan_maintenance_notes(notes: str) -> tuple[str, list[str]]:
    """Return HIGH, MEDIUM, or LOW risk and any matched phrases."""
    text = notes.lower()
    high = [term for term in HIGH_RISK_TERMS if term in text]
    medium = [term for term in MEDIUM_RISK_TERMS if term in text]
    if high:
        return "HIGH", high
    if medium:
        return "MEDIUM", medium
    return "LOW", []


def _joint_feature_rows(joint_readings):
    return [[float(joint_readings[j][f]) for f in FEATURES] for j in JOINTS]


def decide_arm(
    arm_id: str,
    joint_readings: dict[str, dict[str, float]],
    maintenance_notes: str,
    model=None,
    previous_readings: dict[str, dict[str, float]] | None = None,
) -> dict[str, Any]:
    """Return one final decision per arm, following a fixed priority order."""
    stop, stop_reasons = immediate_safety_stop(joint_readings)
    spoof, spoof_reasons = detect_spoofed_sensor(joint_readings, previous_readings)
    note_risk, note_matches = scan_maintenance_notes(maintenance_notes)

    if stop:
        decision = "EMERGENCY_STOP"
        wear_probability = None
        reason = "Hard safety limit/invalid critical reading crossed."
    elif spoof:
        decision = "SCHEDULE_MAINTENANCE"
        wear_probability = None
        reason = "Sensor consistency defense raised an alert; investigate sensor integrity."
    else:
        wear_probability = 0.0
        if model is not None:
            probs = model.predict_proba(_joint_feature_rows(joint_readings))
            classes = list(model.classes_)
            if 1 in classes:
                wear_probability = max(float(p[classes.index(1)]) for p in probs)
        if note_risk == "HIGH" or wear_probability >= 0.75:
            decision = "SCHEDULE_MAINTENANCE"
            reason = "High-risk technician note or high predicted wear probability."
        elif note_risk == "MEDIUM" or wear_probability >= 0.40:
            decision = "MONITOR"
            reason = "Moderate note risk or elevated predicted wear probability."
        else:
            decision = "SAFE"
            reason = "No hard-limit, spoofing, high-risk note, or elevated wear alert."

    return {
        "arm_id": arm_id,
        "decision": decision,
        "reason": reason,
        "wear_probability": None if wear_probability is None else round(wear_probability, 3),
        "maintenance_note_risk": note_risk,
        "matched_note_terms": note_matches,
        "emergency_stop_reasons": stop_reasons,
        "spoof_alerts": spoof_reasons,
    }


def demo_scenarios(model=None) -> list[dict[str, Any]]:
    """Four explicit examples, one for each required decision."""
    normal = {
        "shoulder": {"torque_nm": 28, "temperature_c": 48, "vibration_mm_s": 3.2},
        "elbow": {"torque_nm": 31, "temperature_c": 50, "vibration_mm_s": 3.5},
        "wrist": {"torque_nm": 19, "temperature_c": 45, "vibration_mm_s": 2.8},
    }
    monitor = {
        "shoulder": {"torque_nm": 48, "temperature_c": 68, "vibration_mm_s": 8.5},
        "elbow": {"torque_nm": 43, "temperature_c": 66, "vibration_mm_s": 7.2},
        "wrist": {"torque_nm": 25, "temperature_c": 56, "vibration_mm_s": 4.0},
    }
    schedule = {
        "shoulder": {"torque_nm": 52, "temperature_c": 71, "vibration_mm_s": 9.5},
        "elbow": {"torque_nm": 49, "temperature_c": 69, "vibration_mm_s": 8.2},
        "wrist": {"torque_nm": 27, "temperature_c": 57, "vibration_mm_s": 4.2},
    }
    emergency = {
        "shoulder": {"torque_nm": 91, "temperature_c": 62, "vibration_mm_s": 7.0},
        "elbow": {"torque_nm": 32, "temperature_c": 49, "vibration_mm_s": 3.0},
        "wrist": {"torque_nm": 20, "temperature_c": 45, "vibration_mm_s": 2.5},
    }
    return [
        decide_arm("DEMO-SAFE", normal, "Routine inspection completed; no abnormal findings.", model=None),
        decide_arm("DEMO-MONITOR", monitor, "Slight vibration noted; monitor next shift.", model=None),
        decide_arm("DEMO-SCHEDULE", schedule, "Technician reported grinding and abnormal backlash.", model=None),
        decide_arm("DEMO-STOP", emergency, "Routine inspection.", model=None),
    ]


def main():
    model, accuracy = train_wear_model()
    print(f"Synthetic test-split accuracy: {accuracy:.3f} (educational demo only)")
    print("\nRequired four decision examples:")
    for result in demo_scenarios(model):
        print(json.dumps(result, indent=2))
    print("\nFleet sample decisions using the first historical readings:")
    rows = _load_csv_rows()
    for arm_index, arm_id in enumerate(ARMS):
        chunk = rows[arm_index * 3: arm_index * 3 + 3]
        readings = {
            joint: {feature: chunk[i][feature] for feature in FEATURES}
            for i, joint in enumerate(JOINTS)
        }
        result = decide_arm(arm_id, readings, "Routine inspection completed.", model=model)
        print(f"{arm_id}: {result['decision']} — {result['reason']}")


if __name__ == "__main__":
    main()
