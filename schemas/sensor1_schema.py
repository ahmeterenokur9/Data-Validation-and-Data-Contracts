# schemas/sensor1_schema.py

import pandas as pd
import pandera.pandas as pa
from pandera import Column, Check

Sensor1Schema = pa.DataFrameSchema(
    columns={
        "sensor_id": Column(str, Check.equal_to("sensor1"), nullable=False),
        "timestamp": Column(
            str,
            Check.str_matches(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"), # the format is YYYY-MM-DD HH:MM:SS
            nullable=False,
            coerce=True, 
        ),
        "temperature": Column(
            float,
            Check.between(-40, 85),
            nullable=False
        ),
        "humidity": Column(
            float,
            Check.between(0, 100),
            nullable=False
        ),
    },
    strict=True,   
    coerce=True    
)
