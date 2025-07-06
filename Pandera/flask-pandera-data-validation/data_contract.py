import pandera.pandas as pa
from pandera.typing import Series

class SensorData(pa.DataFrameModel):
  id : Series[str] = pa.Field(
      str_startswith="PWR-",
      str_length=8,
      nullable=False
  )

  current : Series[float] = pa.Field(
      ge = 0.0,
      le = 20.0

  )

  voltage : Series[float] = pa.Field(
      ge = 210.0,
      le = 240.0
  )

  class Config:
    strict = True
    coerce = True
