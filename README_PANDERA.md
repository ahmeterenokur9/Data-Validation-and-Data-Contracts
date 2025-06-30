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


