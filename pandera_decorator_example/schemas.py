import pandas as pd
import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check

# ==========================================
# Input Schema: IoT Sensor Data
# ==========================================
# - sensor_id: one of ['tr-12', 'it-41', 'en-33']
# - timestamp: pd.Timestamp, not in the future
# - temperature: float, -40.0 <= value <= 100.0
# - humidity: float, 0.0 <= value <= 100.0

iot_input_schema = DataFrameSchema({
    "sensor_id": Column(
        str,
        Check.isin(["tr-12", "it-41", "en-33"]),
        description="Valid sensor IDs: tr-12, it-41, en-33",
        nullable=False # sensor_id cannot be null
    ),
    "timestamp": Column(
        pa.Timestamp,
        Check(lambda ts: ts <= pd.Timestamp.now(), element_wise=True),
        description="Timestamp must not be in the future",
        nullable=False
    ),
    "temperature": Column(
        float,
        Check(lambda t: -40.0 <= t <= 100.0, element_wise=True),
        description="Temperature in °C between -40 and 100",
        nullable=True # temperature can sometimes be null
    ),
    "humidity": Column(
        float,
        Check(lambda h: 0.0 <= h <= 100.0, element_wise=True),
        description="Humidity percentage between 0 and 100",
        nullable=True # humidity can sometimes be null
    ),
})

# ==========================================
# Output Schema: Adds dew_point
# ==========================================
iot_output_schema = iot_input_schema.add_columns({
    "dew_point": Column(
        float,
        Check(lambda dp: -100.0 <= dp <= 200.0, element_wise=True),
        description="Computed dew point in °C",
        nullable=False
    )
})