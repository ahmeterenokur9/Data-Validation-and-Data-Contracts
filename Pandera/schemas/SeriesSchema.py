# Use this when you want to validate a single pandas.Series

import pandas as pd
from pandera import SeriesSchema, Check

# Create a Series of ages
ages = pd.Series([21, 25, 30])

# Define the schema: integers and greater than or equal to 18
schema = SeriesSchema(
    int,
    checks=Check.ge(18)
)

# Validate the Series
validated_series = schema.validate(ages)
print(validated_series)


