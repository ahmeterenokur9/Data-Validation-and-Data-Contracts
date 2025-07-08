import pandas as pd
import pandera.pandas as pa
from pandera.typing import DataFrame, Series

# data contract
class engine_data(pa.DataFrameModel):
  engine_id : Series(str) = pa.Field(
    str_startswith="ENG-"
  )
  mode : Series(str) = pa.Field(
    isin = ["active","rest"]
  )
  temp : Series(float) = pa.Field(
    le= 200.0,
    ge= 0.0
  )

  @pa.dataframe_check # special rule for engine mode
  def check_engine_mode(cls, df : pd.DataFrame):
    active_mode = (df["mode"] == "active") & (df["temp"].between(70,100))
    rest_mode = (df["mode"] == "rest") & (df["temp"].between(20, 50))
    return active_mode | rest_mode

# example datas
valid_data = pd.DataFrame({
    "engine_id": ["ENG-12345", "ENG-54321", "ENG-12345", "ENG-98765"],
    "timestamp": pd.to_datetime(["2023-10-27 10:00:00", "2023-10-27 10:01:00", "2023-10-27 10:05:00", "2023-10-27 10:06:00"]),
    "mode": ["active", "rest", "active", "rest"],
    "temperature_celsius": [86.5, 35.0, 99.9, 21.2],
})

# This DataFrame contains several errors and should fail validation.
invalid_data = pd.DataFrame({
    "engine_id": ["ENG-12345", "ENG-54321", "BAD-ID-999", "ENG-98765"],
    "timestamp": pd.to_datetime(["2023-10-27 11:00:00", "2023-10-27 11:01:00", "2023-10-27 11:05:00", "2023-10-27 11:06:00"]),
    "mode": ["active", "rest", "active", "idle"], # "idle" is not a valid mode
    "temperature_celsius": [110.0, 65.0, 90.0, 30.0], # 110 is too high for active, 65 is too high for rest
})

print("--- Validating CORRECT data ---")
try:
    validated_df = EngineDataSchema.validate(valid_data,lazy=True)
    print("✅ Validation successful! The data is valid.")
    print(validated_df)
except pa.errors.SchemaErrors as exc:
    print("❌ Validation failed unexpectedly!")
    print(exc)

print("\n" + "="*40 + "\n")

print("--- Validating INCORRECT data ---")
try:
    EngineDataSchema.validate(invalid_data,lazy=True)
except pa.errors.SchemaErrors as exc:
    print("❌ Validation failed as expected. See errors below:")
    print(exc.failure_cases)







    



