import time
import json
import random
from datetime import datetime
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "/sensor4"

def generate_environment_data():
    """
    Generates simulated data from an environmental sensor.
    Produces 90% valid data and 10% invalid data.
    """
    data = {
        "sensor_id": "sensor4",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "radiation_level": round(random.uniform(0.1, 0.8), 4),
        "soil_temperature": round(random.uniform(-5.0, 25.0), 2)
    }

    # 10% chance to generate an error
    if random.random() < 0.1:
        error_type = random.choice([
            "out_of_bounds_radiation",
            "out_of_bounds_temp",
            "missing_radiation",
            "wrong_type",
            "null_radiation",
            "malformed_timestamp",
            "wrong_id"
        ])
        
        print(f"*** Generating error: {error_type} ***")

        if error_type == "out_of_bounds_radiation":
            data["radiation_level"] = round(random.uniform(1.1, 2.0), 4)
        elif error_type == "out_of_bounds_temp":
            data["soil_temperature"] = round(random.uniform(51.0, 70.0), 2)
        elif error_type == "missing_radiation":
            del data["radiation_level"]
        elif error_type == "wrong_type":
            data["soil_temperature"] = "cold"
        elif error_type == "null_radiation":
            # This will fail schema validation since nullable is False for this field
            data["radiation_level"] = None
        elif error_type == "malformed_timestamp":
            data["timestamp"] = datetime.now().isoformat() # Wrong format
        elif error_type == "wrong_id":
            data["sensor_id"] = "sensor-99"
            
    # Randomly make soil_temperature null, which is allowed by the schema
    elif random.random() < 0.05: # 5% of valid messages
        data["soil_temperature"] = None


    return data

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.connect(BROKER, PORT)
    print(f"[Sensor4] Connected: {BROKER}:{PORT}, topic={TOPIC}")

    try:
        while True:
            data = generate_environment_data()
            payload = json.dumps(data)
            client.publish(TOPIC, payload)
            print(f"[Sensor4] Sent: {payload}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n[Sensor4] Environment Publisher stopped.")
        client.disconnect()

if __name__ == "__main__":
    main() 