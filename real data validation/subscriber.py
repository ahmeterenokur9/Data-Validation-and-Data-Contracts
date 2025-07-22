import json
import paho.mqtt.client as mqtt
from pandera.errors import SchemaErrors
import pandas as pd
import warnings
from schema import schema  # schema.py --> Data Contract

warnings.filterwarnings("ignore")

# MQTT Settings
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_SUB = "ıot_data"
TOPIC_VALID = "ıot_data/valid"
TOPIC_FAILED = "ıot_data/failed"

client = mqtt.Client()

row_counter = 0

def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected. Subscribing...")
    client.subscribe(TOPIC_SUB)

def on_message(client, userdata, msg):
    global row_counter 
    try:
        data_dict = json.loads(msg.payload.decode("utf-8"))
        df = pd.DataFrame([data_dict])

        # Pandera 
        validated = schema.validate(df)
        print(f"[VALID] Row {row_counter}: {json.dumps(data_dict)}")
        print("----------------------------------------------------------------")
        client.publish(TOPIC_VALID, json.dumps(data_dict))
        row_counter += 1  

    except SchemaErrors as e:
        print(f"[FAILED] Row {row_counter}: Validation Failed:\n{e.failure_cases}")
        print("--------------------------------------------------------------")
        client.publish(TOPIC_FAILED, json.dumps(data_dict))
        row_counter += 1

    except Exception as e:
        print(f"[ERROR] Row {row_counter}: error: {e}")
        print("--------------------------------------------------------------")
        row_counter += 1

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
