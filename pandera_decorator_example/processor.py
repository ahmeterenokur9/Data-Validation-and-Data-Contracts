import pandas as pd
import pandera.pandas as pa
from pandera import Check
from schemas import iot_input_schema, iot_output_schema

# ==========================================
# Processing Function with @check_io
# ==========================================
# Computes dew point: dew_point = temperature - (100 - humidity) / 5

@pa.check_io(data=iot_input_schema, out=iot_output_schema)
def process_sensor_data(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    df["dew_point"] = df.apply(
        lambda row: row["temperature"] - (100.0 - row["humidity"]) / 5.0
        if pd.notna(row["temperature"]) and pd.notna(row["humidity"])
        else float('nan'),
        axis=1
    )
    return df