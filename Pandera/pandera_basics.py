import pandas as pd
import pandera as pa
from pandera import Check

schema = pa.DataFrameSchema({
    "column1": pa.Column(int, Check.ge(0)),
    "column2": pa.Column(float, Check.lt(100)),
    "column3": pa.Column(str, Check.isin(["a", "b", "c"])),
})


data = {
    "column1": [1, 2, 3],
    "column2": [10.5, 20.3, 30.1],
    "column3": ["a", "b", "c"],
}

df = pd.DataFrame(data)

try:
    validated_df = schema.validate(df)
    print("Validation succeeded!")
    print(validated_df)
except pa.errors.SchemaError as e:
    print("Validation failed:")
    print(e)


