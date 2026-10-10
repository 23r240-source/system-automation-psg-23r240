

import random
import time

LOG_FILE = "day2_factory_log.txt"
NUM_MACHINES = 5
NUM_TICKS = 10

# STEP 1: Generate simulated sensor data
def generate_sensor_data():
    return {
        "temperature": random.randint(50, 95),
        "pressure": random.randint(20, 60),
        "vibration": round(random.uniform(0.1, 10.0), 2),
        "current": round(random.uniform(2.0, 20.0), 2)
    }

# STEP 2: Define automation rules
RULES = [
    {
        "name": "CRITICAL_TEMP",
        "priority": 1,
        "condition": lambda r: r["temperature"] > 90,
        "action": "EMERGENCY_STOP",
        "urgency": 100
    },
    {
        "name": "HIGH_TEMP",
        "priority": 2,
        "condition": lambda r: r["temperature"] > 80,
        "action": "STOP_MACHINE",
        "urgency": 80
    },
    {
        "name": "HIGH_PRESSURE",
        "priority": 3,
        "condition": lambda r: r["pressure"] > 50,
        "action": "REDUCE_PRESSURE",
        "urgency": 60
    },
    {
        "name": "HIGH_VIBRATION",
        "priority": 4,
        "condition": lambda r: r["vibration"] > 7.0,
        "action": "CHECK_MACHINE",
        "urgency": 55
    },
    {
        "name": "HIGH_CURRENT",
        "priority": 5,
        "condition": lambda r: r["current"] > 16.0,
        "action": "REDUCE_LOAD",
        "urgency": 50
    },
    {
        "name": "LOW_PRESSURE",
        "priority": 6,
        "condition": lambda r: r["pressure"] < 25,
        "action": "CHECK_PRESSURE",
        "urgency": 40
    },
    {
        "name": "REPEATED_WARNING",
        "priority": 7,
        "condition": lambda r: r["temperature"] > 75,
        "action": "INVESTIGATE_REPEATED_WARNING",
        "urgency": 70
    }
]

# STEP 3: Evaluate all matching rules
def evaluate_rules(reading, rules):
    matching_rules = [
        rule for rule in rules
        if rule["condition"](reading)
    ]

    if not matching_rules:
        return {
            "name": "NO_RULE_FIRED",
            "priority": 999,
            "action": "CONTINUE_NORMAL",
            "urgency": 0
        }

    return min(matching_rules, key=lambda rule: rule["priority"])

# STEP 4: Describe the action
def take_action(action):
    actions = {
        "EMERGENCY_STOP": "CRITICAL! Emergency stop required.",
        "STOP_MACHINE": "High temperature detected. Stop and inspect.",
        "REDUCE_PRESSURE": "High pressure detected. Investigate pressure control.",
        "CHECK_MACHINE": "High vibration detected. Inspect the machine.",
        "REDUCE_LOAD": "High current detected. Investigate electrical load.",
        "CHECK_PRESSURE": "Low pressure detected. Inspect the pressure system.",
        "INVESTIGATE_REPEATED_WARNING":
            "Persistent temperature warning. Investigate the cause.",
        "CONTINUE_NORMAL": "No alert triggered. Continue monitoring."
    }

    return actions.get(action, f"Unknown action: {action}")

# STEP 5: Record every decision
def log_decision(machine_id, reading, rule_name, action, urgency):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(
            f"{timestamp} | Machine: {machine_id} | "
            f"Reading: {reading} | Rule: {rule_name} | "
            f"Action: {action} | Urgency: {urgency}\n"
        )

# STEP 6: Create five machines
def create_machines():
    return {
        f"MACHINE_{i}": {
            "previous_high_temp": False
        }
        for i in range(1, NUM_MACHINES + 1)
    }

# STEP 7: Monitor each machine
def monitor_factory(machines):
    results = []

    for machine_id, machine in machines.items():
        reading = generate_sensor_data()

        # New rule: detect consecutive high-temperature warnings
        repeated_warning = (
            reading["temperature"] > 75
            and machine["previous_high_temp"]
        )

        machine["previous_high_temp"] = reading["temperature"] > 75

        selected_rule = evaluate_rules(reading, RULES)

        if repeated_warning:
            selected_rule = {
                "name": "REPEATED_WARNING",
                "priority": 0,
                "action": "INVESTIGATE_REPEATED_WARNING",
                "urgency": 90
            }

        results.append({
            "machine_id": machine_id,
            "reading": reading,
            "rule": selected_rule["name"],
            "action": selected_rule["action"],
            "urgency": selected_rule["urgency"]
        })

    results.sort(
        key=lambda item: item["urgency"],
        reverse=True
    )

    return results

# STEP 8: Main automation workflow
def main():
    print("=" * 80)
    print("23IF02 FACTORY AUTOMATION - FIVE MACHINE MONITORING")
    print("=" * 80)

    machines = create_machines()

    with open(LOG_FILE, "w", encoding="utf-8") as file:
        file.write("FACTORY AUTOMATION DECISION LOG\n")

    for tick in range(1, NUM_TICKS + 1):
        print(f"\nTICK {tick:02d} - FACTORY SENSOR REPORT")
        print("-" * 80)

        results = monitor_factory(machines)

        for result in results:
            print(f"\nMachine ID: {result['machine_id']}")
            print(f"Sensor readings: {result['reading']}")
            print(f"Triggered rule: {result['rule']}")
            print(f"Action: {take_action(result['action'])}")
            print(f"Urgency score: {result['urgency']}")

            log_decision(
                result["machine_id"],
                result["reading"],
                result["rule"],
                result["action"],
                result["urgency"]
            )

        most_urgent = results[0]

        print("\n" + "=" * 80)
        if most_urgent["urgency"] > 0:
            print("MACHINE REQUIRING THE MOST URGENT ATTENTION")
            print(f"Machine ID: {most_urgent['machine_id']}")
            print(f"Triggered rule: {most_urgent['rule']}")
            print(f"Recommended response: {take_action(most_urgent['action'])}")
            print(f"Urgency score: {most_urgent['urgency']}")
        else:
            print("No machine triggered an alert in this tick.")

        print("=" * 80)
        time.sleep(0.2)

    print("\nFactory monitoring completed.")
    print(f"Decision log saved to: {LOG_FILE}")
    print("Sensor readings are simulated; no real machines are controlled.")

if __name__ == "__main__":
    main()
