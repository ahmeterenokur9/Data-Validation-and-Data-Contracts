import pandas as pd
import pandera.pandas as pa
from pandera import Column, Check

# for age column: data variables have to be int and >= 0 
column_schema = Column(int, Check.ge(0))

# createing a DataFrame
df = pd.DataFrame({"age": [25, 30, 40]})


validated_column = column_schema.validate(df["age"])

print(validated_column)
