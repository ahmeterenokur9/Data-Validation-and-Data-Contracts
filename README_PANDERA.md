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

