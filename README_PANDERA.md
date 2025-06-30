# Pandera: A Data Validation Toolkit for Data Scientists & Engineers

![Intro](images/pandera.png)

---

## What is Pandera?

Pandera is a powerful and flexible **data validation** library for Python, designed to check dataframe-like objects. Think of it as a quality control checkpoint for your data.

In any data pipeline, from analytics to machine learning, the quality of your output is determined by the quality of your input. Pandera helps you prevent the "**Garbage In, Garbage Out**" problem by allowing you to define a clear, readable, and explicit schema, or "**contract**," for your data. 

This contract specifies rules that your data must follow, such as:

- The data types of columns (int, str, datetime).
- The range of acceptable values (age > 0, score between 0 and 100).
- Unique or required columns.
- More complex statistical properties.


By validating your data against this schema at runtime, Pandera makes your data processing pipelines more readable, robust, and easier to debug.

##  Key Features

**Pandera** empowers you to build reliable data pipelines by providing a rich set of features that go beyond simple type-checking.

###  Expressive and Readable Schema Definitions

Define your **data validation** rules in a clear and declarative way. Pandera supports two powerful APIs:

* A modern, class-based **`DataFrameModel`** (similar to **Pydantic**)
* A flexible, object-based **`DataFrameSchema`**

---

### Comprehensive Validation Checks

Implement a wide range of checks, from simple value constraints like **`greater_than`**, **`isin`**, and **`str_matches`** to complex, custom business logic.
You can validate:

* Individual values
* Entire columns
* Relationships between multiple columns

---

###  Statistical Validation and Hypothesis Testing

Go beyond structural validation by performing **statistical hypothesis tests** directly on your data.

* Assert that a sample comes from a specific distribution
* Assert that two groups are statistically different

---

###  Seamless Pipeline Integration

Integrate **data validation** directly into your existing functions and data workflows with simple decorators:

* **`@check_types`**
* **`@check_io`**

Validate inputs and outputs without cluttering your core logic.

---

###  Data Synthesis for Testing

Generate **synthetic data** directly from your schemas.
This is invaluable for **property-based testing**, ensuring your functions are robust against a wide variety of valid (and invalid) data inputs.

---

###  Lazy Validation and Rich Error Reporting

Instead of failing at the first error, **Pandera** can **collect all validation failures at once**.
It provides:

* Detailed, machine-readable **error reports**
* Clear insight into **what** failed and **where**, making debugging significantly faster.

---

###  Data Cleaning and Transformation

**Pandera** is not just a validator. You can:

* Use built-in **Parsers** to codify preprocessing steps (e.g., cleaning, normalization)
* Automatically **drop invalid rows** that fail validation checks

---

###  Broad Ecosystem Support

While built for **pandas**, Pandera also supports:

* **Polars**
* **Dask**
* **Modin**
* **pyspark**

This enables **scalable data quality checks** on both in-memory and out-of-memory data.

Elbette! Aşağıda verdiğiniz metni **Markdown formatında** yeniden düzenledim. Önemli kısımları **kalın**, kod bloklarını uygun şekilde vurguladım. Her başlığı ayrı tutarak hem kurulum hem de hızlı başlangıç kısmı okunabilir hale getirildi.

---

## 📦 Installation

Get started by installing **Pandera** with pandas support:

### 🔹 With pip:

```bash
pip install "pandera[pandas]"
```

### 🔹 With conda:

```bash
conda install -c conda-forge pandera-pandas
```

---

###  Optional Extras

Install additional features as needed:

```bash
pip install 'pandera[hypotheses]'  # hypothesis checks
pip install 'pandera[io]'          # yaml/script schema io utilities
pip install 'pandera[strategies]'  # data synthesis strategies
pip install 'pandera[mypy]'        # enable static type-linting of pandas
pip install 'pandera[fastapi]'     # fastapi integration
pip install 'pandera[dask]'        # validate dask dataframes
pip install 'pandera[pyspark]'     # validate pyspark dataframes
pip install 'pandera[modin]'       # validate modin dataframes
pip install 'pandera[modin-ray]'   # validate modin dataframes with ray
pip install 'pandera[modin-dask]'  # validate modin dataframes with dask
pip install 'pandera[geopandas]'   # validate geopandas geodataframes
pip install 'pandera[polars]'      # validate polars dataframes
```

---

##  Quick Start

Let’s validate a **DataFrame** using **`DataFrameModel`**, the modern and Pydantic-style schema API.

### ✅ Validating a Good Dataset

```python
import pandas as pd
import pandera.pandas as pa

# 1. Define your data
data = pd.DataFrame({
    "column1": [1, 2, 3],
    "column2": [1.1, 1.2, 1.3],
    "column3": ["a", "b", "c"],
})

# 2. Define a schema
class Schema(pa.DataFrameModel):
    column1: int = pa.Field(ge=0)
    column2: float = pa.Field(lt=10)
    column3: str = pa.Field(isin=[*"abc"])

    @pa.check("column3")
    def check_column_length(cls, series: pd.Series) -> pd.Series:
        """Ensure all values in column3 have a length of 1."""
        return series.str.len() == 1

# 3. Validate your data
try:
    validated_df = Schema.validate(data)
    print("✅ Validation Successful!")
    print(validated_df)
except pa.errors.SchemaError as e:
    print(f"❌ Validation Error: {e}")
```

---

### ❌ Validating a Dataset with Errors

```python
invalid_data = pd.DataFrame({
    "column1": [-20, 5, 10],       # -20 fails the ge=0 check
    "column2": [1.1, 15.0, 1.3],   # 15.0 fails the lt=10 check
    "column3": ["a", "b", "xyz"],  # "xyz" fails isin and length checks
})

try:
    # Use lazy=True to collect ALL validation errors at once
    Schema.validate(invalid_data, lazy=True)
except pa.errors.SchemaErrors as err:
    print("❗ Caught validation errors:")
    print(err.failure_cases)
```

###  Sample Output

```text
Caught validation errors:
  schema_context   column                   check                   check_number  failure_case index
0         Column  column1  greater_than_or_equal_to(0)             0           -20       0
1         Column  column2              less_than(10)              0           15.0      1
2         Column  column3        isin(['a', 'b', 'c'])             0           xyz       2
3         Column  column3     check_column_length              None        xyz       2
```

-



##  DataFrameSchema: Validating  DataFrames with Confidence

`DataFrameSchema` is a core feature of **Pandera**, allowing you to define a **clear, explicit contract** for your DataFrames. It validates column types, checks value constraints, handles missing or extra data, and more.

---

###  Basic Usage

```python
import pandas as pd
import pandera.pandas as pa

schema = pa.DataFrameSchema({
    "column1": pa.Column(int),
    "column2": pa.Column(float, pa.Check(lambda s: s < 10)),
    "column3": pa.Column(str, checks=[
        pa.Check.str_startswith("value"),
        pa.Check.str_length(6),
    ]),
}, index=pa.Index(int), coerce=True)
```

* **Column types** are enforced (e.g., `int`, `float`, `str`)
* **Checks** ensure valid content (`< 10`, string patterns, etc.)
* **Index** type can be validated
* `coerce=True` tries to automatically convert values to the correct type

---

###  Null Handling

By default, nulls **are not allowed**. You must opt-in:

```python
schema = pa.DataFrameSchema({
    "column1": pa.Column(float, nullable=True)
})
```

---

###  Type Coercion

You can force Pandera to coerce column types before validation:

```python
df = pd.DataFrame({"column1": [1, 2, 3]})
schema = pa.DataFrameSchema({"column1": pa.Column(str, coerce=True)})
validated_df = schema.validate(df)
```

---

###  Strict Column Enforcement

Control what happens with unexpected or missing columns:

* `strict=True`: Only allow schema-defined columns
* `strict="filter"`: Drop extra columns
* `add_missing_columns=True`: Add missing columns with default or NaN

---

###  Column Order Validation

Enforce column order if needed (important in ML pipelines):

```python
schema = pa.DataFrameSchema(
    {"a": pa.Column(int), "b": pa.Column(int)},
    ordered=True
)
```

---

###  Multi-Column Constraints

Ensure that **combinations** of columns are unique:

```python
schema = pa.DataFrameSchema(
    {"a": pa.Column(int), "b": pa.Column(int)},
    unique=["a", "b"]
)
```

---

###  Transforming Schemas

You can programmatically **add**, **remove**, or **update** schema elements:

```python
schema = schema.add_columns({
    "new_col": pa.Column(str, default="default_value")
})
```

---

###  Regex Column Matching

Validate **groups of columns** using regex:

```python
schema = pa.DataFrameSchema({
    "metric_.+": pa.Column(float, regex=True)
})
```

---

###  Index & MultiIndex Support

You can also define validation rules for index or multi-index structures:

```python
schema = pa.DataFrameSchema(
    {"value": pa.Column(int)},
    index=pa.Index(str, pa.Check.str_startswith("index_"))
)
```

---

###  Standalone Column Validation

You don't need a full schema to validate one or two columns:

```python
col_schema = pa.Column(int, name="column1")
col_schema.validate(df)
```

# Key Points on Pandera `DataFrameModel`

### 1. What is `DataFrameModel`?

* Class-based API for defining dataframe schemas
* Inspired by Pydantic models
* Enables type-safe, declarative data validation

---

### 2. Defining a Schema

```python
from pandera.typing import Series
import pandera.pandas as pa

class InputSchema(pa.DataFrameModel):
    year: Series[int] = pa.Field(gt=2000, coerce=True)
    month: Series[int] = pa.Field(ge=1, le=12, coerce=True)
```

---

### 3. Validating DataFrames

* Use the `@pa.check_types` decorator on functions with typed DataFrames
* Or validate directly with `InputSchema.validate(df)`

---

### 4. Optional Fields

* Use `typing.Optional` to make a column optional

```python
from typing import Optional
class Schema(pa.DataFrameModel):
    a: Series[str]
    b: Optional[Series[int]]  # Optional column
```

---

### 5. Schema Inheritance

* Build complex schemas by inheriting base schemas

```python
class Base(pa.DataFrameModel):
    year: Series[int]

class Extended(Base):
    passengers: Series[int]
```

---

### 6. Config Class

* Control schema-wide options like coercion, strictness

```python
class Schema(pa.DataFrameModel):
    year: Series[int] = pa.Field(gt=2000)

    class Config:
        coerce = True
        strict = True
```

---

### 7. Custom Checks

* Add class methods with `@pa.check("column_name")` for custom validation

```python
class Schema(pa.DataFrameModel):
    age: Series[int]

    @pa.check("age")
    def age_check(cls, series):
        return series >= 18
```

---

### 8. Aliases for Columns

* Use `alias` in `Field` for columns that aren’t valid Python identifiers

```python
class Schema(pa.DataFrameModel):
    col_2020: Series[int] = pa.Field(alias="2020")
```

---

### 9. MultiIndex Support

* Use `Index` type and configure MultiIndex in `Config`

```python
from pandera.typing import Index

class Schema(pa.DataFrameModel):
    year: Index[int] = pa.Field(gt=2000)

    class Config:
        multiindex_name = "time"
```

---

### 10. Converting to DataFrameSchema & Validate

```python
schema = InputSchema.to_schema()
validated_df = InputSchema.validate(df)
```

# Pandera Data Type Validation 

### 1. Purpose of Data Type Validation

* Ensures input data matches expected types
* Prevents corrupted data propagating downstream (analytics, ML, etc.)
* Enables *fail fast* behavior in data pipelines

---

### 2. How to Specify Data Types

* At **column** level in `DataFrameSchema`:

```python
import pandera.pandas as pa

schema = pa.DataFrameSchema({
    "column1": pa.Column(int),
    "column2": pa.Column(float),
    "column3": pa.Column(str),
}, index=pa.Index(int))
```

* At **dataframe-wide** level if all columns share the same type:

```python
schema_df = pa.DataFrameSchema(dtype=int)
```

* Equivalent with `DataFrameModel`:

```python
from pandera.typing import Series, Index

class Model(pa.DataFrameModel):
    column1: Series[int]
    column2: Series[float]
    column3: Series[str]
    index: Index[int]

class ModelDF(pa.DataFrameModel):
    class Config:
        dtype = int
```

---

### 3. Supported Data Types

* Python built-ins: `int`, `float`, `str`, `bool`, etc.
* NumPy types: `np.int64`, `np.bool_`, etc.
* Pandas native types: `pd.StringDtype`, `pd.BooleanDtype`, `pd.DatetimeTZDtype`, etc.
* String aliases supported by pandas (`"int64"`, `"float64"`, etc.)
* Pandera's own types like `pa.Int`, `pa.Int64`

**Example of multiple ways to declare integer type:**

```python
import numpy as np

schema = pa.DataFrameSchema({
    "col1": pa.Column(int),
    "col2": pa.Column("int"),
    "col3": pa.Column("int64"),
    "col4": pa.Column(np.int64),
    "col5": pa.Column(pa.Int),
    "col6": pa.Column(pa.Int64),
})
```

---

### 4. Parameterized Data Types (e.g. timezone-aware datetime)

* Pandas dtype objects like `pd.DatetimeTZDtype(unit="ns", tz="UTC")` can be used

**With `DataFrameSchema`:**

```python
schema = pa.DataFrameSchema({
    "dt": pa.Column(pd.DatetimeTZDtype(unit="ns", tz="UTC"))
})
```

**With `DataFrameModel` and Python type annotations:**

```python
from typing import Annotated

class DateTimeModel(pa.DataFrameModel):
    dt: Series[Annotated[pd.DatetimeTZDtype, "ns", "UTC"]]
```

or use `Field` with `dtype_kwargs`:

```python
class DateTimeModel(pa.DataFrameModel):
    dt: Series[pd.DatetimeTZDtype] = pa.Field(dtype_kwargs={"unit": "ns", "tz": "UTC"})
```

---

### 5. Data Type Coercion

* Pandera primarily **validates** types but does not mutate data
* Use `coerce=True` in schema or column to **convert** data to the specified type during validation:

```python
schema = pa.DataFrameSchema(
    {
        "column": pa.Column(int, coerce=True)
    }
)
validated_df = schema.validate(df)  # df values coerced to int
```

* Coercion works similarly on `DataFrameModel` fields via `Field(coerce=True)` or config

---

### 6. Nullable and Data Types

* `nullable=True` allows `NaN`/`None` in columns
* But if dtype **does not support nulls**, validation fails regardless of `nullable=True`
* Type checks run **before** nullable checks in validation pipeline

---

### 7. Support for Python `typing` Module Generic Types

* Validate columns containing objects like:

  * `Dict[K, V]`
  * `List[T]`
  * `Tuple[T, ...]`
  * `TypedDict`
  * `NamedTuple`

* Uses **typeguard** under the hood (if installed) for deep validation

* Without `typeguard >=3.0.0`, only first item is checked in collections

**Example schema with typing generics:**

```python
from typing import Dict, List, Tuple, TypedDict, NamedTuple
import pandera.pandas as pa

class PointDict(TypedDict):
    x: float
    y: float

class PointTuple(NamedTuple):
    x: float
    y: float

schema = pa.DataFrameSchema({
    "dict_col": pa.Column(Dict[str, int]),
    "list_col": pa.Column(List[float]),
    "tuple_col": pa.Column(Tuple[int, str, float]),
    "typed_dict_col": pa.Column(PointDict),
    "named_tuple_col": pa.Column(PointTuple),
})
```

---

### 8. PyArrow Data Types Support

* Pandera supports PyArrow dtypes via pandas ArrowDtype wrappers

```python
import pyarrow
import pandas as pd
import pandera.pandas as pa

schema = pa.DataFrameSchema({
    "pyarrow_col": pa.Column(pyarrow.float64()),
    "pandas_str_alias": pa.Column("float64[pyarrow]"),
    "pandas_dtype": pa.Column(pd.ArrowDtype(pyarrow.float64()))
})

from typing import Annotated

class PyarrowModel(pa.DataFrameModel):
    pyarrow_dtype: pyarrow.float64
    pandas_dtype: Annotated[pd.ArrowDtype, pyarrow.float64()]
    pandas_dtype_kwargs: pd.ArrowDtype = pa.Field(dtype_kwargs={"pyarrow_dtype": pyarrow.float64()})
```



# Pandera Hypothesis Testing 

### 1. Purpose

* Allows you to perform statistical hypothesis tests on your data within schema validation.
* Example: Testing if the mean of two groups differs significantly.

---

### 2. Installation

* Requires installing Pandera with the `hypothesis` extra:

  ```bash
  pip install pandera[hypothesis]
  ```

---

### 3. Example: Two-Sample T-Test

```python
import pandas as pd
import pandera.pandas as pa
from scipy import stats

df = pd.DataFrame({
    "height_in_feet": [6.5, 7, 6.1, 5.1, 4],
    "sex": ["M", "M", "F", "F", "F"]
})

schema = pa.DataFrameSchema({
    "height_in_feet": pa.Column(
        float,
        checks=[
            pa.Hypothesis.two_sample_ttest(
                sample1="M",
                sample2="F",
                groupby="sex",
                relationship="greater_than",
                alpha=0.05,
                equal_var=True,
            )
        ],
    ),
    "sex": pa.Column(str)
})

try:
    schema.validate(df)
except pa.errors.SchemaError as exc:
    print(exc)
```

* Tests whether the mean height of group "M" is greater than "F".
* If the test fails, a `SchemaError` is raised.

---

### 4. Custom Hypothesis Tests

* You can define your own test and relationship functions:

```python
def two_sample_ttest(array1, array2):
    return stats.ttest_ind(array1, array2)

def null_relationship(stat, pvalue, alpha=0.01):
    return pvalue / 2 >= alpha

schema = pa.DataFrameSchema({
    "height_in_feet": pa.Column(
        float,
        checks=[
            pa.Hypothesis(
                test=two_sample_ttest,
                samples=["M", "F"],
                groupby="sex",
                relationship=null_relationship,
                relationship_kwargs={"alpha": 0.05},
            )
        ],
    ),
    "sex": pa.Column(str, checks=pa.Check.isin(["M", "F"]))
})

schema.validate(df)
```

---

### 5. Long (Tidy) and Wide Form Data Support

* Pandera primarily supports **long (tidy) data**, where each row is an observation.
* Also supports **wide form data** for hypothesis tests across columns.

**Long form example:**

```python
df = pd.DataFrame({
    "height": [5.6, 7.5, 4.0, 7.9],
    "group": ["A", "B", "A", "B"],
})

schema = pa.DataFrameSchema({
    "height": pa.Column(
        float,
        pa.Hypothesis.two_sample_ttest(
            "A", "B",
            groupby="group",
            relationship="less_than",
            alpha=0.05
        )
    ),
    "group": pa.Column(str, pa.Check(lambda s: s.isin(["A", "B"])))
})

schema.validate(df)
```

**Wide form example:**

```python
df = pd.DataFrame({
    "height_A": [5.6, 4.0],
    "height_B": [7.5, 7.9],
})

schema = pa.DataFrameSchema(
    columns={
        "height_A": pa.Column(float),
        "height_B": pa.Column(float),
    },
    checks=pa.Hypothesis.two_sample_ttest(
        "height_A", "height_B",
        relationship="less_than",
        alpha=0.05
    )
)

schema.validate(df)
```


# Pandera Preprocessing with Parsers

### What are Parsers?

* Parsers let you **preprocess** data (DataFrames, columns, or Series) *before* running validation checks.
* Useful to **clean, normalize, clip**, or transform data as part of your schema.

---

### Parsing vs Validation

* **Parsing** = transforming raw data into a desired format or state.
* **Validation** = checking if the data meets the constraints (e.g., types, ranges).

---

### Built-in Parsers Examples

* `coerce=True`: Converts data types before validation.
* `strict="filter"`: Removes columns not in schema.
* `add_missing_columns=True`: Adds missing nullable columns or those with defaults.

---

### Custom Parsers

* You can specify **custom parsers** to apply any transformation function on the data *inside* the schema.
* Parsers receive a `pandas.Series` (for columns) or `DataFrame` (for the whole dataframe) and return the transformed version.

---

### Example: Column-level Parser

```python
import pandas as pd
import pandera.pandas as pa

schema = pa.DataFrameSchema({
    "a": pa.Column(
        int,
        parsers=pa.Parser(lambda s: s.clip(lower=0)),  # clip negative values to 0
        checks=pa.Check.ge(0),
    )
})

data = pd.DataFrame({"a": [1, 2, -1]})
schema.validate(data)
```

* Input: `[1, 2, -1]`
* After parsing: `[1, 2, 0]`
* Validation passes because all values ≥ 0.

---

### Multiple Parsers on a Column

* You can provide a list of parsers, applied in order:

```python
schema = pa.DataFrameSchema({
    "string_numbers": pa.Column(
        str,
        parsers=[
            pa.Parser(lambda s: s.str.zfill(10)),  # pad with zeros to length 10
            pa.Parser(lambda s: s.str[2:]),        # slice from character 3 onward
        ]
    ),
})
```

---

### DataFrame-level Parsers

* Parsers can be applied to entire DataFrames before column-level parsing.

Example:

```python
schema = pa.DataFrameSchema(
    parsers=pa.Parser(lambda df: df.transform("sqrt")),
    columns={
        "a": pa.Column(float),
        "b": pa.Column(float, parsers=pa.Parser(lambda s: s * -1)),
        "c": pa.Column(float, parsers=pa.Parser(lambda s: s + 1)),
    }
)

data = pd.DataFrame({
    "a": [2.0, 4.0, 9.0],
    "b": [2.0, 4.0, 9.0],
    "c": [2.0, 4.0, 9.0],
})

schema.validate(data)
```

Output:

| a        | b         | c        |
| -------- | --------- | -------- |
| 1.414214 | -1.414214 | 2.414214 |
| 2.000000 | -2.000000 | 3.000000 |
| 3.000000 | -3.000000 | 4.000000 |

---

### Using Parsers in DataFrameModel API

```python
class DFModel(pa.DataFrameModel):
    a: float
    b: float
    c: float

    @pa.dataframe_parser
    def sqrt(cls, df):
        return df.transform("sqrt")

    @pa.parser("b")
    def negate(cls, series):
        return series * -1

    @pa.parser("c")
    def plus_one(cls, series):
        return series + 1
```

---

# Pandera Decorators for Pipeline Integration

Pandera provides decorators that make it easy to **validate pandas DataFrames or Series** passed into or returned from your existing functions, helping to integrate validation smoothly into data pipelines.

---

### 1. `@check_input`

* Validates the **input** DataFrame or Series before the wrapped function runs.
* By default, assumes the **first positional argument** is the DataFrame/Series to validate.
* You can specify which argument to check by **name** (string) or **index** (integer).

**Example:**

```python
import pandas as pd
import pandera.pandas as pa

df = pd.DataFrame({
    "column1": [1, 4, 0, 10, 9],
    "column2": [-1.3, -1.4, -2.9, -10.1, -20.4],
})

in_schema = pa.DataFrameSchema({
    "column1": pa.Column(int, pa.Check(lambda x: 0 <= x <= 10, element_wise=True)),
    "column2": pa.Column(float, pa.Check(lambda x: x < -1.2)),
})

@pa.check_input(in_schema)
def preprocessor(dataframe):
    dataframe["column3"] = dataframe["column1"] + dataframe["column2"]
    return dataframe

preprocessed_df = preprocessor(df)
print(preprocessed_df)
```

Output:

| column1 | column2 | column3 |
| ------- | ------- | ------- |
| 1       | -1.3    | -0.3    |
| 4       | -1.4    | 2.6     |
| 0       | -2.9    | -2.9    |
| 10      | -10.1   | -0.1    |
| 9       | -20.4   | -11.4   |

---

### 2. `@check_output`

* Validates the **output** DataFrame or Series from the wrapped function.
* Works by default on the sole output, but you can specify an **index**, a **key** (if output is dict-like), or a **custom function** to select the output to validate.

**Example:**

```python
out_schema = pa.DataFrameSchema({
    "column1": pa.Column(int, pa.Check(lambda x: x == 0))
})

@pa.check_output(out_schema)
def zero_column_1(df):
    df["column1"] = 0
    return df

zeroed_df = zero_column_1(preprocessed_df)
```

This checks that all values in `"column1"` are zero.

---

### 3. `@check_io`

* Convenient decorator to validate **both inputs and outputs** in one place.
* You can specify input and output schemas as keyword arguments with any names.

**Example:**

```python
in_schema = pa.DataFrameSchema({
    "column1": pa.Column(int),
    "column2": pa.Column(float),
})

out_schema = in_schema.add_columns({"column3": pa.Column(float)})

@pa.check_io(df1=in_schema, df2=in_schema, out=out_schema)
def preprocessor(df1, df2):
    return (df1 + df2).assign(column3=lambda x: x.column1 + x.column2)

result = preprocessor(df, df)
print(result)
```

Output:

| column1 | column2 | column3 |
| ------- | ------- | ------- |
| 2       | -2.6    | -0.6    |
| 8       | -2.8    | 5.2     |
| 0       | -5.8    | -5.8    |
| 20      | -20.2   | -0.2    |
| 18      | -40.8   | -22.8   |

---

### 4. Decorators Support Sync & Async Functions and Methods

* All pandera decorators (`check_input`, `check_output`, `check_io`, `check_types`) work on:

  * **Synchronous** and **asynchronous** functions.
  * Class methods (including static and class methods).
  * Regular functions or coroutines.
  * Even on metaclasses’ methods.

**Example:**

```python
import pandera.pandas as pa
from pandera.typing import DataFrame, Series

class Schema(pa.DataFrameModel):
    col1: Series[int]

    class Config:
        strict = True

@pa.check_types
async def coroutine(df: DataFrame[Schema]) -> DataFrame[Schema]:
    return df

@pa.check_types
async def function(df: DataFrame[Schema]) -> DataFrame[Schema]:
    return df

class SomeClass:
    @pa.check_output(Schema.to_schema())
    async def regular_coroutine(self, df) -> DataFrame[Schema]:
        return df

    @classmethod
    @pa.check_input(Schema.to_schema(), "df")
    async def class_coroutine(cls, df):
        return Schema.validate(df)

    @staticmethod
    @pa.check_io(df=Schema.to_schema(), out=Schema.to_schema())
    def static_method(df):
        return df
```








