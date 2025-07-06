import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series 

class Data_Contract(pa.DataFrameModel):

  sensor_id : Series[int] = pa.Field(
      gt = 0,
      le = 10
  )

  gas_concentration_ppm : Series[float] = pa.Field(
      le = 550,
      ge = 0
  )

  magnetic_flux_uT : Series[float]

  sound_level_dB : Series[float] = pa.Field(
      gt = 50.0,
      ge = 0
  )


df = pd.read_csv("iot_data.csv")

try:
  Data_Contract.validate(df, lazy=True)
except pa.errors.SchemaErrors as e:
  print(e.failure_cases)
