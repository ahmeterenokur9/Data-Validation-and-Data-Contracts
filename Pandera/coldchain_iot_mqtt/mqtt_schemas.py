import pandera.pandas as pa
from pandera.typing import Series, DateTime

print("Defining Cold Chain Logistics Sensor Data Contract...")

class ColdChainSensorData(pa.DataFrameModel):
  truck_id: Series[str] = pa.Field(
      str_startswith="TRUCK-",
      nullable=False
  )

  timestamp: Series[DateTime] = pa.Field()

  temperature_c : Series[float] = pa.Field(
      ge=-5.0,
      le=10.0
  )

  humidity_percent : Series[float] = pa.Field(
      ge=40.0,
      le=90.0
  )

  latitude : Series[float] = pa.Field(ge=-90.0, le=90.0)
  longitude : Series[float] = pa.Field(ge=-180.0, le=180.0)

  class Config:
    strict = True
    coerce = True
