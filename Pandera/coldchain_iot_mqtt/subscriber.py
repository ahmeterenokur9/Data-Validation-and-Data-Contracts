import paho.mqtt.client as mqtt
import json
import pandas as pd
import pandera.pandas as pa

from mqtt_schemas import ColdChainSensorData

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "iot/logistics/coldchain/telemetry"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[Subscriber] Successfully connected to MQTT Broker: {MQTT_BROKER}")
        client.subscribe(MQTT_TOPIC)
        print(f"[Subscriber] Listening to topic: '{MQTT_TOPIC}'")
    else:
        print(f"[Subscriber] Connection failed, return code: {rc}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    print(f"\n[Subscriber] Raw message received: {payload}")

    try:
        data_packet = json.loads(payload)
        df = pd.DataFrame([data_packet])
        ColdChainSensorData.validate(df)
        print("✅ [Subscriber] Data is valid and accepted.")

    except json.JSONDecodeError:
        print("❌ [Subscriber] ERROR: Received message is not valid JSON.")
    except pa.errors.SchemaError as e:
        print("❌ [Subscriber] INVALID DATA! Rejected.")
        print(f"Error Details: {e.failure_cases.to_dict()}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
