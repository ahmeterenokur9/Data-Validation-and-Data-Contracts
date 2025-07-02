schema = pa.DataFrameSchema(
    {"id": pa.Column(int, pa.Check.lt(10))},
    name="MySchema",
    strict=True,  # strict=True ensures that the DataFrame contains only the columns explicitly defined in the schema—no more, no less.
)

df = pd.DataFrame({"id": [1, None, 30], "extra_column": [1, 2, 3]})

try:
    schema.validate(df, lazy=True)
except pa.errors.SchemaErrors as exc:
    print(exc)

