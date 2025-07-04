import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series
import random
import time 
from datetime import datetime


# Data Contract
class Machine(pa.DataFrameModel):
  id : Series[str] = pa.Field(
      eq = "MC-101"
  )

  vibration : Series[float] = pa.Field(
      ge = 0.0,
      le = 10.00

  )

  count : Series[int] = pa.Field(
      ge = 0,
      le = 120

  )

  class Config:
    strict = True
    coerce = True
    
# Simulating a real sensor data flow
def generate_sensor_data():

  reading = {
      "id" : "MC-101",
      "vibration" : round(random.uniform(1.5,4.0),2),
      "count" : random.randint(90,110),


  }
  faulty_sensor = None

  if random.random() < 0.3:
    faulty_sensor = random.choice([ "vibration", "count"])

  if faulty_sensor == "vibration":
            reading[faulty_sensor] = 15.7
  elif faulty_sensor == "count":
            reading[faulty_sensor] = 125
    
          
  return reading


while True:
    
    live_data = generate_sensor_data()
    
    live_df = pd.DataFrame([live_data])
    
    print(f"[{timestamp}] Data received: {live_data}")

    
    try:
        
        Machine.validate(live_df)  # Data Validation
        
        print("Data is valid")
        
    except pa.errors.SchemaError as e:
       
        print("🚨 WARNING: INVALID DATA DETECTED!")
        print(e.failure_cases)
        
       

    
    time.sleep(3)
