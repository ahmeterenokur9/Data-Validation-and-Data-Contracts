import json
import paho.mqtt.client as mqtt
from pandera.errors import SchemaErrors
import pandas as pd
import warnings
from schema import schema  # schema.py içinden DataFrameSchema nesnesini import et

# Uyarıları gizle (örn. boş değer uyarıları için)
warnings.filterwarnings("ignore")

# MQTT Ayarları
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_SUB = "ıot_data"
TOPIC_VALID = "ıot_data/valid"
TOPIC_FAILED = "ıot_data/failed"

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("[MQTT] Connected. Subscribing...")
    client.subscribe(TOPIC_SUB)

def on_message(client, userdata, msg):
    try:
        data_dict = json.loads(msg.payload.decode("utf-8"))
        df = pd.DataFrame([data_dict])

        # Pandera 
        validated = schema.validate(df)
        print(f"[VALID] {data_dict}")
        client.publish(TOPIC_VALID, json.dumps(data_dict))

    except SchemaErrors as e:
        print(f"[FAILED] Validation Failed:\n{e.failure_cases}")
        client.publish(TOPIC_FAILED, json.dumps(data_dict))
    
    except Exception as e:
        print(f"[ERROR] error: {e}")

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_forever()
