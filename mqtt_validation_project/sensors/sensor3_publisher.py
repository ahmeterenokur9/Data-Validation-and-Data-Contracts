# sensors/sensor3_publisher.py

import time, json, random
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT   = 1883
TOPIC  = "/sensor3"

def generate_sensor3_data():
    """
    %90 valid, %10 invalid
    valid ranges:
    voltage: 110 … 230 V
    current: 0 … 20 A
    power:   >= 0 W
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    voltage = round(random.uniform(110, 230), 2)
    current = round(random.uniform(0, 20), 2)
    data = {
        "sensor_id": "sensor3",
        "timestamp": timestamp,
        "voltage": voltage,
        "current": current,
        "power": round(voltage * current, 2)
    }


    if random.random() < 0.1:
        error_type = random.choice([
            "out_of_bounds",
            "missing_key",
            "wrong_type",
            "null_value",
            "extra_field",
            "malformed_timestamp",
            "wrong_id"
        ])


        if error_type == "out_of_bounds":
            choice = random.choice(["voltage", "current", "power"])
            if choice == "voltage":
                data["voltage"] = round(random.choice([random.uniform(231, 300), random.uniform(50, 109)]), 2)
            elif choice == "current":
                data["current"] = round(random.choice([random.uniform(21, 30), random.uniform(-10, -1)]), 2)
            else: # power
                data["power"] = -100  # Negatif güç
        elif error_type == "missing_key":
            del data[random.choice(["voltage", "current", "power"])]
        elif error_type == "wrong_type":
            choice = random.choice(["voltage", "current", "power"])
            data[choice] = f"invalid-{choice}"
        elif error_type == "null_value":
            choice = random.choice(["voltage", "current", "power"])
            data[choice] = None
        elif error_type == "extra_field":
            data["frequency"] = "50Hz"
        elif error_type == "malformed_timestamp":
            data["timestamp"] = "2023/01/01 12:00:00"  
        elif error_type == "wrong_id":
            data["sensor_id"] = "invalid-sensor-3"

    return data

def main():
    client = mqtt.Client(); client.connect(BROKER, PORT)
    print(f"[Sensor3] Connected, topic={TOPIC}")
    try:
        while True:
            data = generate_sensor3_data()
            client.publish(TOPIC, json.dumps(data))
            print(f"[Sensor3] {data}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[Sensor3] publish stopped"); client.disconnect()

if __name__ == "__main__":
    main()
