from paho.mqtt.client import Client
from paho.mqtt.enums import CallbackAPIVersion
import json
import time
import random
from datetime import datetime

# mqtt configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT   = 1883
MQTT_TOPIC  = "iot/logistics/coldchain/telemetry"

# sensor data simulation
def generate_truck_data():
  data = {
      "truck_id": f"TRUCK-{random.randint(100, 999)}",
        

      "timestamp": datetime.utcnow().isoformat(),
        

      "temperature_c": round(random.uniform(0.0, 5.0), 2),
        

      "humidity_percent": random.randint(50, 80),
        

      "latitude": 39.9334,
      "longitude": 32.8597
  }

  # simulating wrong data
  if random.random() < 0.3:  
       
        fault_type = random.choice(['temp_range', 'humidity_type', 'id_format'])
        
        if fault_type == 'temp_range':
            data['temperature_c'] = 15.5  
            

        elif fault_type == 'humidity_type':
            data['humidity_percent'] = 75.5  
            

        elif fault_type == 'id_format':
            data['truck_id'] = "-123"  
            

  return data
   


    

# connection
client = Client(callback_api_version=CallbackAPIVersion.VERSION1)

client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.loop_start() 

print("[Publisher] Simulator started. Data will be published every 3 seconds.")

# loop
try:
    while True:
        telemetry_data = generate_truck_data()
        payload = json.dumps(telemetry_data)
        

        print(f"\n[Publisher] Data: {payload}")
        client.publish(MQTT_TOPIC, payload)
        

        time.sleep(3)
        
except KeyboardInterrupt:
    
    print("\n[Publisher] Publishing stopped manually.")
finally:
    client.loop_stop()
    client.disconnect()
