import pandas as pd 
import pandera.pandas as pa
from pandera.typing import DataFrame , Series

# Data Contract
class SalesDataContract(pa.DataFrameModel):
  product_id : Series[str] = pa.Field(
      str_startswith="PROD-", # it should start with PROD-
      unique=True # have to be unique
      
  )

  quantity: Series[int] = pa.Field(
      ge=1, coerce=True # should be greater than or equal to 1 
      
  )

  price : Series[float] = pa.Field(
      gt=0.0 # should be greater than 0
  )

  order_date : Series[pa.DateTime] = pa.Field(
      le=pd.Timestamp.now() # the date must be old from today
      
  )

  class Config:
    strict = True # It cant include any columns except those defined in the contracts

# The Data
data = pd.DataFrame({
    "product_id" : ["PROD-101","PROD-102","PROD-103","PROD-105"],

    "quantity" : ["5", 10 , 2, 3],

    "price" :  [19.99 , 50.0, 15.25, 0.6],

    "order_date": [
        pd.to_datetime("2023-10-01"),
        pd.to_datetime("2023-10-02"),
        pd.to_datetime("2023-10-03"),
        pd.to_datetime("2009-01-01")
    ],

    "extra_column" : [1,2,3,4],

    
    
    })

# Validation
try:
  SalesDataContract.validate(data, lazy=True) # Lazy Mode will check whole data
except pa.errors.SchemaErrors as e:
  print("Data Validation Failed:")
  print(e.failure_cases.to_string()) # More Readable format
else:
  print("Data Validation Successful")


