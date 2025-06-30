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






