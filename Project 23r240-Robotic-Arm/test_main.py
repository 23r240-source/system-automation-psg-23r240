import unittest
from main import decide_arm


class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.normal = {
            "shoulder": {"torque_nm": 28, "temperature_c": 48, "vibration_mm_s": 3.2},
            "elbow": {"torque_nm": 31, "temperature_c": 50, "vibration_mm_s": 3.5},
            "wrist": {"torque_nm": 19, "temperature_c": 45, "vibration_mm_s": 2.8},
        }

    def test_safe(self):
        self.assertEqual(decide_arm("T", self.normal, "routine inspection")["decision"], "SAFE")

    def test_monitor(self):
        self.assertEqual(decide_arm("T", self.normal, "slight vibration noted")["decision"], "MONITOR")

    def test_schedule(self):
        self.assertEqual(decide_arm("T", self.normal, "grinding sound reported")["decision"], "SCHEDULE_MAINTENANCE")

    def test_emergency_stop_is_independent(self):
        readings = {k: dict(v) for k, v in self.normal.items()}
        readings["elbow"]["torque_nm"] = 90
        self.assertEqual(
            decide_arm("T", readings, "routine inspection", model=None)["decision"],
            "EMERGENCY_STOP",
        )


if __name__ == "__main__":
    unittest.main()
