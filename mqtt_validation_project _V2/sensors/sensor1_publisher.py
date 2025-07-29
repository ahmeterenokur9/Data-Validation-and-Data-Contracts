# sensors/sensor1_publisher.py

import time
import json
import random
from datetime import datetime
import paho.mqtt.client as mqtt


BROKER = "broker.hivemq.com"
PORT   = 1883
TOPIC  = "/sensor1"

def generate_sensor1_data():
    """
    %90 valid, %10 invalid data
    Valid Ranges:
    temperature: -40 … 85 °C
    humidity:    0 … 100 %
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    
    data = {
        "sensor_id": "sensor1",
        "timestamp": timestamp,
        "temperature": round(random.uniform(-40, 85), 2),
        "humidity": round(random.uniform(0, 100), 2)
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
                data["temperature"] = round(random.choice([random.uniform(86, 120), random.uniform(-100, -50)]), 2)
            else:
                data["humidity"] = round(random.choice([random.uniform(101, 150), random.uniform(-50, -1)]), 2)
        elif error_type == "missing_key":
            
            if random.random() < 0.5:
                del data["temperature"]
            else:
                del data["humidity"]
        elif error_type == "wrong_type":
            
            if random.random() < 0.5:
                data["temperature"] = "hot"
            else:
                data["humidity"] = False  # bool
        elif error_type == "null_value":
            
            if random.random() < 0.5:
                data["temperature"] = None
            else:
                data["humidity"] = None
        elif error_type == "extra_field":
            
            data["extra_info"] = "this-is-not-allowed"
        elif error_type == "malformed_timestamp":
            
            data["timestamp"] = "2025-01-01 00:00:00" # Standardized malformed string
        elif error_type == "wrong_id":
            
            data["sensor_id"] = "sensorX"


    return data

def main():
    client = mqtt.Client()
    client.connect(BROKER, PORT)
    print(f"[Sensor1] Connected: {BROKER}:{PORT}, topic={TOPIC}")

    try:
        while True:
            data = generate_sensor1_data()
            payload = json.dumps(data)
            client.publish(TOPIC, payload)
            print(f"[Sensor1] Sent: {payload}")
            time.sleep(2)  # Her 2 saniyede bir
    except KeyboardInterrupt:
        print("\n[Sensor1] publish stopped.")
        client.disconnect()

if __name__ == "__main__":
    main()
