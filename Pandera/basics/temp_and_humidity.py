import pandas as pd
import pandera.pandas as pa
from pandera.typing import DataFrame , Series


# Data Contract
class SensorData(pa.DataFrameModel):

  sensor_id : str = pa.Field(
      
      str_startswith="A-",
      unique=True
      
      )
  
  temperature : float = pa.Field(
      ge = -20,
      le = 100,
      coerce = True
      )

  humidity: float = pa.Field(
      ge=0, 
      le=100,
      coerce = True
      
      )

  class Config:
    strict = True


# Validation Function
def data_check(data):

  try:
    df = pd.DataFrame([data])

    SensorData.validate(df, lazy=True)
    print("Validation Successful")

  except pa.errors.SchemaErrors as e:
    print("Validation Failed:")
    print(e.failure_cases)




# example data 
data_1 = {
    "sensor_id" : "A-321",
    "temperature" : 21,
    "humidity" : "-14"
}



data_check(data_1)
