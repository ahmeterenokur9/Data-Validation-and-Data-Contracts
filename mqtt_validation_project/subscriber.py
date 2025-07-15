# subscriber.py

import json
import pandas as pd
import paho.mqtt.client as mqtt
from pandera.errors import SchemaErrors
import warnings


warnings.filterwarnings(
    "ignore",
    message="The behavior of DataFrame concatenation with empty or all-NA entries is deprecated.*",
    category=FutureWarning,
    module="pandera"
)


from schemas.sensor1_schema import Sensor1Schema
from schemas.sensor2_schema import Sensor2Schema
from schemas.sensor3_schema import Sensor3Schema


from utils import parse_pandera_errors

# MQTT broker
BROKER = "broker.hivemq.com"
PORT   = 1883

# topics
SENSOR_TOPICS = ["/sensor1", "/sensor2", "/sensor3"]

def replace_nan_with_null(obj):
    """
    Recursively walk a dictionary or list and replace NaN values with None (which becomes null in JSON).
    """
    if isinstance(obj, dict):
        return {k: replace_nan_with_null(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan_with_null(elem) for elem in obj]
    elif isinstance(obj, float) and pd.isna(obj):
        return None
    return obj

def process_message(topic: str, payload: str, client: mqtt.Client):

    data = json.loads(payload)
    df = pd.DataFrame([data])

    if topic == "/sensor1":
        schema = Sensor1Schema
    elif topic == "/sensor2":
        schema = Sensor2Schema
    else:
        schema = Sensor3Schema

    try:
        
        schema.validate(df, lazy=True)
       
        client.publish(f"{topic}/validated", json.dumps(data))
        print(f"[VALID] {topic} → {data}")
    except SchemaErrors as e:
        
        errors = parse_pandera_errors(e)
        fail_msg = {
            "sensor": topic.strip("/"),
            "errors": errors,
            "original_payload": data
        }
        
        # Replace NaN with null before publishing
        fail_msg_cleaned = replace_nan_with_null(fail_msg)
        
        client.publish(f"{topic}/failed", json.dumps(fail_msg_cleaned))
        print(f"[INVALID] {topic} → {fail_msg_cleaned}")

def on_connect(client, userdata, flags, rc, props):
    print(f"[Subscriber] Connected with result code {rc}")
    
    for t in SENSOR_TOPICS:
        client.subscribe(t)
        print(f"[Subscriber] Subscribed to {t}")

def on_message(client, userdata, msg):
    
    process_message(msg.topic, msg.payload.decode(), client)

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(BROKER, PORT)
    client.loop_forever()

if __name__ == "__main__":
    main()
