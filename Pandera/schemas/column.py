import pandas as pd
import pandera.pandas as pa
from pandera import Check

# Create a DataFrame
df = pd.DataFrame({
    "age": [21, 25, 30],
    "name": ["Ali", "Bob", "Charlie"]
})

# Define schema: age must be >= 18 and name must be a string of length > 0
schema = pa.DataFrameSchema({
    "age": pa.Column(int, Check.ge(18)),
    "name": pa.Column(str, Check.str_length(min_value=1))
})

# Validate the DataFrame
validated_df = schema.validate(df)
print(validated_df)

