import pandas as pd
import pandera.pandas as pa
from pandera.typing.pandas import DataFrame, Series

# Input schema: temperature and oil level must be within specific ranges
class MachineInput(pa.DataFrameModel):
    temperature: Series[float] = pa.Field(ge=0.0, le=100.0, coerce=True)  # between 0 and 100 degrees
    oil_level: Series[float] = pa.Field(ge=0.0, le=10.0, coerce=True)    # between 0 and 10 units

# Output schema: input columns plus a status column indicating machine condition
class MachineOutput(MachineInput):
    status: Series[str]  # "OK" or "ALARM"

@pa.check_types
def monitor_machine(df: DataFrame[MachineInput]) -> DataFrame[MachineOutput]:
    # Determine status: alarm if temperature > 80 or oil_level < 2
    conditions = (df["temperature"] > 80) | (df["oil_level"] < 2)
    status = conditions.map({True: "ALARM", False: "OK"})
    return df.assign(status=status)

# Example data
df = pd.DataFrame({
    "temperature": [70, 85, 60, 90],
    "oil_level": [5, 1.5, 8, 9],
})

print(monitor_machine(df))

