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


{
    "SCHEMA": {
        "COLUMN_NOT_IN_SCHEMA": [
            {
                "schema": "MySchema",
                "column": "MySchema",
                "check": "column_in_schema",
                "error": "column 'extra_column' not in DataFrameSchema {'id': <Schema Column(name=id, type=DataType(int64))>}"
            }
        ],
        "SERIES_CONTAINS_NULLS": [
            {
                "schema": "MySchema",
                "column": "id",
                "check": "not_nullable",
                "error": "non-nullable series 'id' contains null values:1   NaNName: id, dtype: float64"
            }
        ],
        "WRONG_DATATYPE": [
            {
                "schema": "MySchema",
                "column": "id",
                "check": "dtype('int64')",
                "error": "expected series 'id' to have type int64, got float64"
            }
        ]
    },
    "DATA": {
        "DATAFRAME_CHECK": [
            {
                "schema": "MySchema",
                "column": "id",
                "check": "less_than(10)",
                "error": "Column 'id' failed element-wise validator number 0: less_than(10) failure cases: 30.0"
            }
        ]
    }
}

