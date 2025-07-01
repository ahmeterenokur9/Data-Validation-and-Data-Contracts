# Lazy Mode : it collects all errors

import pandas as pd
from pandera import DataFrameSchema, Column, Check, errors

df = pd.DataFrame({
    "age": [21, 15, 30],
    "name": ["Alice", "", "Bob"]
})

schema = DataFrameSchema({
    "age": Column(int, Check.ge(18)),
    "name": Column(str, Check.str_length(min_value=1))
})

try:
    validated_df = schema.validate(df, lazy=True)  # collect all errors
except errors.SchemaErrors as e:
    print("❌ Validation failed (lazy mode)")
    print("Failure cases:")
    print(e.failure_cases)
