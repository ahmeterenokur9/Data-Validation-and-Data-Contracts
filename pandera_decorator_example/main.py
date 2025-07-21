import time
import pandas as pd
import pandera.pandas as pa
from data_generator import generate_sensor_data
from processor import process_sensor_data
from schemas import iot_input_schema  # Sadece bilgi amaçlı

def run_continuous_simulation(error_rate: float = 0.1):
    print("Starting continuous IoT data validation simulation (press Ctrl+C to stop)...")
    
    processed_count = 0
    error_count = 0
    iteration = 0

    try:
        while True:  # loop
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
           
            df_raw = generate_sensor_data(num_records=1, error_rate=error_rate)
            
            try:
                df_processed = process_sensor_data(df_raw)
                processed_count += 1
                print(f"✅ Valid record processed: {df_processed.to_dict(orient='records')[0]}")
            except pa.errors.SchemaError as e:
                error_count += 1
                print(f"❌ Validation error caught for raw data: {df_raw.to_dict(orient='records')[0]}")
                print(f"   Error details: {e.args[0]}")
            except Exception as e:
                error_count += 1
                print(f"⚠️ An unexpected error occurred: {e}")
                print(f"   Raw data causing error: {df_raw.to_dict(orient='records')[0]}")
            
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n--- Simulation Interrupted by User ---")
    finally:
        print("\n--- Simulation Summary ---")
        print(f"Total iterations: {iteration}")
        print(f"Successfully processed records: {processed_count}")
        print(f"Records with validation errors: {error_count}")
        if iteration > 0:
            print(f"Error rate observed: {error_count / iteration:.2%}")
        else:
            print("No iterations completed.")

if __name__ == "__main__":
    run_continuous_simulation(error_rate=0.1)
