import random
import time
import requests

SERVER_URL = 'http://127.0.0.1:5001/data/power' # the url that data will be send

# generating random data
def generate_sensor_reading():
    
    reading = {
        "id": f"PWR-{random.randint(1000, 9999)}",
        "current": round(random.uniform(1.0, 15.0), 2),
        "voltage": round(random.uniform(220.0, 235.0), 2)
    }
    
    if random.random() < 0.3:
        fault_type = random.choice(['id_error', 'range_error', 'type_error'])
      
        if fault_type == 'id_error':
            reading['id'] = "SENSOR-12345"
        elif fault_type == 'range_error':
            reading['current'] = 25.5
        elif fault_type == 'type_error':
            reading['voltage'] = "225.0v"
    return reading

def run_sensor_simulator():
    time.sleep(3) 

    while True:
        data_to_send = generate_sensor_reading()
        try:
            print(f"\n[Sensor] Data Sent: {data_to_send}")
            response = requests.post(SERVER_URL, json=data_to_send)

            print(f"[Server Response] HTTP Status: {response.status_code}, Message: {response.json()}")
        except requests.exceptions.ConnectionError:
            print("[Sensor] ERROR: Could not connect to the server. Please wait...")
        time.sleep(3)

if __name__ == '__main__':
    run_sensor_simulator()
