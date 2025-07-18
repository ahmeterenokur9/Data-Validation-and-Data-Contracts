import pandas as pd
import json
import time
import paho.mqtt.client as mqtt

# MQTT Ayarları
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "ıot_data"

# CSV dosyasını oku
df = pd.read_csv("data.csv")

# MQTT Client ayarla
client = mqtt.Client()
client.connect(BROKER, PORT, 60)

# Satır satır publish et
for idx, row in df.iterrows():
    payload = row.to_json()
    client.publish(TOPIC, payload)
    print(f"[PUBLISH] Row {idx}: {payload}")
    time.sleep(0.5)  # Her 1 saniyede bir gönderim, istersen azaltabilirsin

client.disconnect()
