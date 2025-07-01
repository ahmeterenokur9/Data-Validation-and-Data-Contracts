from pandera import DataFrameSchema, Column, Check
import pandas as pd

df = pd.DataFrame({
    "yaş": [25, 30, 35]
})

# DataFrame için schema: yaş sütunu int ve pozitif olacak
schema = DataFrameSchema({
    "yaş": Column(int, checks=Check.ge(0))
})

schema.validate(df)
