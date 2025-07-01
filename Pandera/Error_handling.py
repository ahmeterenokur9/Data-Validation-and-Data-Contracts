# Eager (default) mode : it will stop when it finds a mistake 

import pandas as pd
from pandera import DataFrameSchema, Column, Check, errors

df = pd.DataFrame({
    "age": [21, 15, 30],        # 15 is invalid (<18)
    "name": ["Alice", "", "Bob"]  # "" is invalid (empty string)
})

schema = DataFrameSchema({
    "age": Column(int, Check.ge(18)),
    "name": Column(str, Check.str_length(min_value=1))
})

try:
    validated_df = schema.validate(df)  # eager mode (default)
    print("✅ Data is valid")
    print(validated_df)
except errors.SchemaError as e:
    print("❌ Validation failed (eager mode)")
    print(e)
