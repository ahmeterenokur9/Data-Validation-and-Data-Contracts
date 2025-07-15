# schemas/sensor2_schema.py

import pandas as pd
import pandera.pandas as pa
from pandera import Column, Check

Sensor2Schema = pa.DataFrameSchema(
    columns={
        "sensor_id": Column(str, Check.equal_to("sensor2"), nullable=False),
        "timestamp": Column(
            str,
            Check.str_matches(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"),
            nullable=False,
            coerce=True,
        ),
        "pressure": Column(
            float,
            Check.between(950, 1050),
            nullable=False
        ),
        "acceleration": Column(
            float,
            Check.between(-10, 10),
            nullable=False
        ),
    },
    strict=True,
    coerce=True
)
