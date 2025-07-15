# schemas/sensor3_schema.py

import pandas as pd
import pandera.pandas as pa
from pandera import Column, Check

Sensor3Schema = pa.DataFrameSchema(
    columns={
        "sensor_id": Column(str, Check.equal_to("sensor3"), nullable=False),
        "timestamp": Column(
            str,
            Check.str_matches(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$"),
            nullable=False,
            coerce=True,
        ),
        "voltage": Column(
            float,
            Check.between(110, 230),
            nullable=False
        ),
        "current": Column(
            float,
            Check.between(0, 20),
            nullable=False
        ),
        "power": Column(
            float,
            Check.greater_than_or_equal_to(0),
            nullable=False
        ),
    },
    strict=True,
    coerce=True
)
