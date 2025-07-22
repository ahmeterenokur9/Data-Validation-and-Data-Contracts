import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def generate_sensor_data(num_records: int = 1, error_rate: float = 0.1) -> pd.DataFrame:

    records = []
    sensor_ids = ["tr-12", "it-41", "en-33"]

    for _ in range(num_records):
        record = {}
        is_error = random.random() < error_rate

        record["sensor_id"] = random.choice(sensor_ids)
        record["timestamp"] = pd.to_datetime(datetime.now() - timedelta(seconds=random.randint(0, 86400)))
        record["temperature"] = random.uniform(-20.0, 40.0) 
        record["humidity"] = random.uniform(30.0, 90.0)    

        if is_error:
            error_type = random.choice([
                "null_value",
                "out_of_range",
                "wrong_type",
                "missing_column", # for 'humidity' or 'temperature'
                "extra_column"
            ])

            if error_type == "null_value":
                field_to_null = random.choice(["temperature", "humidity"])
                record[field_to_null] = np.nan # NaN (Not a Number) 
                print(f"DEBUG: Null value error injected for {field_to_null}")

            elif error_type == "out_of_range":
                field_to_corrupt = random.choice(["temperature", "humidity"])
                if field_to_corrupt == "temperature":
                    record["temperature"] = random.choice([-100.0, 150.0]) 
                else: # humidity
                    record["humidity"] = random.choice([-10.0, 110.0])   
                print(f"DEBUG: Out of range error injected for {field_to_corrupt}")

            elif error_type == "wrong_type":
                field_to_corrupt = random.choice(["temperature", "humidity"])
                record[field_to_corrupt] = "invalid_string"
                print(f"DEBUG: Wrong type error (string) injected for {field_to_corrupt}")

            elif error_type == "missing_column":
                column_to_remove = random.choice(["temperature", "humidity"])
                if column_to_remove in record:
                    del record[column_to_remove]
                print(f"DEBUG: Missing column error injected for {column_to_remove}")

            elif error_type == "extra_column":
                record["extra_data"] = "some_random_value"
                print("DEBUG: Extra column error injected")
        
        records.append(record)

    return pd.DataFrame(records)
