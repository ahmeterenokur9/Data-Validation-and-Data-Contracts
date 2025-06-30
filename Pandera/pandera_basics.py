# importing librarires
import pandas as pd
import pandera.pandas as pa
from pandera import Check


# creating schema
schema = pa.DataFrameSchema({
    "column1": pa.Column(int, Check.ge(0)), # all values must be integer and also can not be nagative
    "column2": pa.Column(float, Check.lt(100)), # all values must be float and also should be less than 100
    "column3": pa.Column(str, Check.isin(["a", "b", "c"])), # have to be string and cant be anything except a,b,c
})

# creating test data
data = {
    "column1": [1, 2, 3],
    "column2": [10.5, 20.3, 30.1],
    "column3": ["a", "b", "c"],
}

df = pd.DataFrame(data)

# data validation
try:
    validated_df = schema.validate(df)
    print("Validation succeeded!")
    print(validated_df)
except pa.errors.SchemaError as e:
    print("Validation failed:")
    print(e)


