import pandas as pd
import json
import time
import paho.mqtt.client as mqtt

# MQTT 
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "ıot_data"

# CSV 
df = pd.read_csv("data.csv")

# MQTT Client
client = mqtt.Client()
client.connect(BROKER, PORT, 60)

# row by row
for idx, row in df.iterrows():
    payload = row.to_json()
    client.publish(TOPIC, payload)
    print(f"[PUBLISH] Row {idx}: {payload}")
    print("---------------------------------------------------------------------")
    time.sleep(1)  

client.disconnect()
