# Use this when validating a specific column within a full DataFrame (table)

import pandas as pd
from pandera import DataFrameSchema, Column, Check

# Create a DataFrame
df = pd.DataFrame({
    "age": [21, 25, 30],
    "name": ["Ali", "Bob", "Charlie"]
})

# Define schema: age must be >= 18 and name must be a string of length > 0
schema = DataFrameSchema({
    "age": Column(int, Check.ge(18)),
    "name": Column(str, Check.str_length(min_value=1))
})

# Validate the DataFrame
validated_df = schema.validate(df)
print(validated_df)

