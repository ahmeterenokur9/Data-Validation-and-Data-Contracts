# sensors/sensor2_publisher.py

import time, json, random
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT   = 1883
TOPIC  = "/sensor2"

def generate_sensor2_data():
    """
    %90 valid, %10 invalid
    Valid Range:
    pressure:     950 … 1050 hPa
    acceleration: -10 … 10  m/s^2
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  
    data = {
        "sensor_id": "sensor2",
        "timestamp": timestamp,
        "pressure": round(random.uniform(950, 1050), 2),
        "acceleration": round(random.uniform(-10, 10), 2)
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
            if random.random() < 0.5:
                data["pressure"] = round(random.choice([random.uniform(1051, 1100), random.uniform(900, 949)]), 2)
            else:
                data["acceleration"] = round(random.choice([random.uniform(11, 20), random.uniform(-20, -11)]), 2)
        elif error_type == "missing_key":
            if random.random() < 0.5:
                del data["pressure"]
            else:
                del data["acceleration"]
        elif error_type == "wrong_type":
            if random.random() < 0.5:
                data["pressure"] = "high"
            else:
                data["acceleration"] = {"x": 1, "y": 2}  # object
        elif error_type == "null_value":
            if random.random() < 0.5:
                data["pressure"] = None
            else:
                data["acceleration"] = None
        elif error_type == "extra_field":
            data["vibration"] = 99.9
        elif error_type == "malformed_timestamp":
            data["timestamp"] = "2025-01-01 00:00:00" # Standardized malformed string
        elif error_type == "wrong_id":
            data["sensor_id"] = "invalid-sensor-2"

    return data

def main():
    client = mqtt.Client(); client.connect(BROKER, PORT)
    print(f"[Sensor2] Connected, topic={TOPIC}")
    try:
        while True:
            data = generate_sensor2_data()
            client.publish(TOPIC, json.dumps(data))
            print(f"[Sensor2] {data}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[Sensor2] publish stopped."); client.disconnect()

if __name__ == "__main__":
    main()
