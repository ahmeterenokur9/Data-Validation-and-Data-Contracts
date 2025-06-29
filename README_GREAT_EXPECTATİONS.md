# Great Expectations (GX)

![GX](images/GX.jpeg)

## 1. What is Great Expectations?

Great Expectations (GX) is a leading open-source Python framework for data quality. Its core mission is to help data teams eliminate pipeline debt through data testing, documentation, and profiling. Think of it as unit testing for your data.

GX is built around a simple, powerful idea: making implicit assumptions about your data explicit. It does this through three core concepts:

- **Expectations**: Declarative, human-readable assertions about your data. These are the "tests" themselves.  
  - Example: `expect_column_values_to_not_be_null(column="user_id")`  
  - Example: `expect_column_values_to_be_between(column="order_amount", min_value=0)`

- **Validations**: The process of running a suite of Expectations against a batch of your data to check if it meets your quality standards.

- **Data Docs**: Human-readable documentation and data quality reports automatically generated from your Validation Results.

As a Python library, GX integrates seamlessly into data pipelines, CI/CD workflows, and data science notebooks, providing a robust foundation for building reliable data products.

## 2. Introducing GX Cloud: The Managed Data Quality Platform

**GX Cloud** is the fully managed, enterprise-grade SaaS platform that builds upon the power of the open-source framework.

### Key Advantages:
- **Centralized Collaboration**: A single source of truth for all data quality rules and results.
- **UI-Driven Workflows**: Intuitive web interface to manage Expectations and Validations.
- **Powerful Automation**: Schedule checks, configure alerts, and detect anomalies.
- **ExpectAI**: AI-powered feature that auto-generates high-value Expectations based on your data.

## 3. The GX Cloud Workflow

![GX](images/GX_workflow.png)

A typical workflow in GX Cloud involves:

1. **Connect to Data**: Securely connect to your source (e.g., PostgreSQL, Snowflake).
2. **Create a Data Asset**: Select tables/views to monitor.
3. **Define Expectations**:
   - Manually via UI
   - Automatically with anomaly detection
   - Using **ExpectAI** for AI-recommended tests
4. **Validate Your Data**: Run checks manually, on a schedule, or via orchestrators like Airflow.
5. **Review & Share**: Analyze results in dashboards, and share links with your team.

![GX](images/GX_workflow2.png)

## 4. Deployment Patterns

### Fully-Hosted

| Pattern      | How It Works                                                         | When to Use It                    |
|--------------|----------------------------------------------------------------------|----------------------------------|
| Fully-Hosted | GX Cloud connects to your data via a secure, read-only cloud connection. | Quick setup; ideal for open environments. |

![Fully Hosted Deployment](images/GX_fh.png)

---

### Agent-Enabled

| Pattern       | How It Works                                            | When to Use It                         |
|---------------|---------------------------------------------------------|---------------------------------------|
| Agent-Enabled | You run a GX Agent in your environment; data stays private. | For strict security policies; control stays internal. |

![Agent Enabled Deployment](images/GX_agent.png)

---

### Read-Only

| Pattern   | How It Works                                                   | When to Use It                                                           |
|-----------|----------------------------------------------------------------|-------------------------------------------------------------------------|
| Read-Only | You run validations locally with the open-source GX lib; only metadata is sent to GX Cloud. | For advanced users who need full control and only want to use GX Cloud for UI. |

![Read Only Deployment](images/GX_reado.png)




## 5. Connecting to Data Sources

GX Cloud offers an easy UI to connect to sources like **Databricks**, **PostgreSQL**, **Redshift**, and **Snowflake**.

### Best Practices:
- **Use a Dedicated User**: With read-only permissions.
- **Navigate to**: `Data Assets > New Data Source` in the UI.
- **Provide Connection String**: Include host, port, username, password, and DB name.
- **Create Assets**: Select tables to monitor and start testing.

## 6. Programmatic Usage with Python

Interact with GX Cloud using the `great_expectations` Python library.

### Step 1: Install the Library

```bash
pip install great_expectations
````

### Step 2: Set Environment Variables

```bash
export GX_CLOUD_ACCESS_TOKEN="<YOUR_GX_CLOUD_TOKEN>"
export GX_CLOUD_ORGANIZATION_ID="<YOUR_GX_CLOUD_ORG_ID>"
```

### Step 3: Python Script Example

```python
import great_expectations as gx
import great_expectations.expectations as gxe

# 1. Get GX Cloud context
context = gx.get_context(mode="cloud")

# 2. Load data (example: read from remote CSV using pandas source)
batch = context.data_sources.pandas_default.read_csv(
    "https://raw.githubusercontent.com/great-expectations/gx_tutorials/main/data/yellow_tripdata_sample_2019-01.csv"
)

# 3. Create Expectation Suite
suite = gx.ExpectationSuite(name="my_taxi_data_quality_suite")

# 4. Add Expectations
suite.add_expectation(gxe.ExpectColumnValuesToNotBeNull(column="pickup_datetime"))
suite.add_expectation(
    gxe.ExpectColumnValuesToBeBetween(column="passenger_count", min_value=1, max_value=6)
)

# 5. Run Validation
results = batch.validate(suite)

# 6. Review results
print(results.describe())
```

Validation results will appear in the GX Cloud UI for review and collaboration.

## 7. Operational Management: Metrics, Validations, Schedules, and Alerts

Once your Data Assets and Expectations are configured, **GX Cloud** provides a powerful set of operational tools to manage the full data quality lifecycle. These features help you move beyond defining data quality toward actively monitoring, automating, and responding to it.

### 📊 Data Profiling and Metrics

Before writing effective Expectations, understanding your data is crucial. GX Cloud includes built-in profiling tools for this purpose.

- **Automatic and On-Demand Profiling**:  
  Upon creation, each Data Asset is automatically analyzed for basic schema information. You can also trigger deeper profiling manually by clicking "Profile Data" from the **Metrics** tab.

- **Key Metrics Provided**:
  - **Row Count**: Total number of records.
  - **Data Type**: As reported by the source system (e.g., `INTEGER`, `VARCHAR`, `TIMESTAMP`).
  - **Numeric Statistics**: For numerical columns – `Min`, `Max`, `Mean`, `Median`.
  - **Completeness**: Percentage of `NULL` values per column.

These insights directly inform the creation of Expectations.  
_Example: If you see a `transaction_value` column has a minimum of `-50.00`, you might add_  
```python
expect_column_values_to_be_between(min_value=0)
````

*to flag invalid data.*

---

### ✅ Running Validations & Automating with Schedules

**Validations** are when GX runs Expectations against actual data. GX Cloud makes this easy to do manually or on a recurring schedule.

* **Manual Validations**:
  Trigger an instant check by clicking **Validate** from a Data Asset page — ideal when:

  * Creating or debugging new Expectations.
  * Investigating a recent change in the data.

* **Batch-Aware Validations**:
  For time-based datasets, validations can be scoped using `DATE` or `DATETIME` fields.

  * **Latest**: Validate only the most recent batch (e.g., yesterday).
  * **Custom**: Validate specific periods (e.g., May 2024).

* **Validation History**:

  * View past results in a **timeline graph**.
  * Filter by **failures only** for faster triage.
  * Each run has a **shareable URL** for team collaboration.

* **Automated Schedules**:

  * When your first Expectation is added, a **daily validation schedule** is enabled by default.
  * You can change:

    * **Frequency** (e.g., hourly, weekly)
    * **Start Time**
    * Or disable it altogether via a toggle.

  ⚠️ *Note: These built-in schedules are only for **UI-managed** Expectations. For **API-managed** Expectations, use external orchestrators like Airflow.*

---

### 🚨 Proactive Alerts & Notifications

GX Cloud ensures you’re notified of critical quality events — before they impact your downstream systems.

* **Alert Triggers**:

  * When a **validation fails**.
  * When **ExpectAI** completes an analysis and recommends new Expectations.

* **Personalized Configuration**:

  * Alerts are set **per-user and per-asset**.
  * You receive alerts only for the data you are responsible for.

* **Smart Defaults**:

  * Alerts are **enabled by default** for Data Assets you create.
  * Alerts are **disabled by default** for assets created by others.

Manage all alert preferences from the **Alerts** tab of any Data Asset using simple toggle switches.

# Example Workflow: A Visual Tour of the GX Cloud UI

To understand how these concepts come together in practice, let's walk through a typical workflow using the Great Expectations Cloud web interface. This example uses the built-in demo data to showcase the end-to-end process from connection to debugging.

---

### Step 1: Connect to a Data Source

Your journey begins on the connection screen. Here, you can establish a direct connection to your primary data sources like Snowflake, PostgreSQL, Databricks SQL, or Redshift.

For a quick start without connecting to your own infrastructure, you can select **"Use demo data"**, which provides a pre-loaded sample dataset.

![Step 1 - Connect to Data Source](images/1.png)

---

### Step 2: Select Your Data Asset

Once you've selected a data source (in this case, the GX demo data), you are presented with a list of available tables. You select the tables you want to monitor. Each selected table becomes a Data Asset in GX Cloud. Here, we've selected the `nyc_taxi_data` table.

![Step 2 - Select Data Asset](images/2.png)

---

### Step 3: Enable Automated Anomaly Detection

This is a key step for accelerating your data quality coverage. By default, GX Cloud automatically enables Anomaly Detection for your new Data Asset. It pre-configures and monitors three critical data quality dimensions:

- **Schema:** Detects any changes to column names or the total number of columns.
- **Volume:** Monitors the table's row count to detect unexpected drops or non-increasing volume.
- **Completeness:** Tracks the proportion of null vs. non-null values in each column to spot changes in data integrity.

You can de-select any of these if you wish, but they provide an excellent baseline for data health monitoring.

![Step 3 - Enable Anomaly Detection](images/3.png)

---

### Step 4: Create Specific Expectations

After setting up the automated baseline, you can define more specific, business-focused rules. The **New Expectation** screen helps you do this by organizing tests into logical categories like Numeric, Uniqueness, Validity (for pattern matching), and even custom SQL.

The UI also provides helpful suggestions. For instance, it recommends checking that the `fare_amount` is within a reasonable range and that the `pickup_borough` values are from a specific, valid set.

![Step 4 - Create Specific Expectations](images/4.png)

---

### Step 5: View the Overall Health Dashboard

The main **Expectations** tab serves as your central data quality dashboard. It provides a high-level overview of all your data quality tests, grouped by category. You can immediately see what's working ("All passed") and what's broken.

In this example, we can instantly see that there are failures in our Numeric and SQL expectations, indicating a problem that needs investigation.

![Step 5 - Health Dashboard](images/5.png)

---

### Step 6: Filter Your View for Focus

The dashboard can be filtered to help you focus. Here, the view has been filtered to show only **"Anomaly Detection"** rules. This allows you to quickly check the status of the automated baseline tests that were configured in Step 3, separate from the more specific, explicit rules you may have created manually.

![Step 6 - Filter View](images/6.png)

---

### Step 7: Drill Down into Failures for Root Cause Analysis

This is where GX Cloud provides true, actionable insights. By switching to the **Validations** tab and filtering for **"Failures only"**, you can investigate why a test failed.

For the Custom SQL Expectations, it shows the exact number of unexpected rows (1,144 and 1,359) returned by the queries, confirming a logic or data integrity violation.

For the `fare_amount` validation, the result is even more detailed. It not only shows that the rule failed with a Success rate of 99.37%, but it also provides a Sample of unexpected values (-21, -17.75, -12.5, etc.).

This sample of failing data is critical for debugging, as it allows a developer to immediately see the nature of the bad data (in this case, negative fare amounts) and fix the root cause.

![Step 7 - Root Cause Analysis](images/7.png)


# GX Core: The Python Data Quality Engine

**GX Core** is the open-source Python library that serves as the foundation for all Great Expectations functionality. It provides a powerful, programmatic interface for developers who want to integrate data quality directly into their code, build custom data validation workflows, and maintain complete control over their execution environment.

---

##  The Pattern of a GX Workflow

All workflows in GX Core—whether simple scripts or production pipelines—follow a consistent four-step pattern:

1. **Set up a GX Environment**  
   Initialize a Data Context, the central object that manages configurations, connections, and results.

2. **Connect to Data**  
   Define your Data Sources and Data Assets (tables, files, etc.) that you want to validate.

3. **Define Expectations**  
   Write Expectations (data quality rules) and organize them into Expectation Suites.

4. **Run Validations**  
   Use Checkpoints or validation definitions to validate data and trigger results or alerts.

![Workflow Overview](images/GX_core.png)

---

##  Setup and Quick Start Examples

###  Prerequisites

- Python 3.9 to 3.12

###  Installation

```bash
pip install great_expectations
````

To verify installation:

```python
import great_expectations as gx
print(gx.__version__)
```

## ✅ Example 1: Validate Data in a Pandas DataFrame

This workflow is ideal for local testing, data exploration, or quick prototypes.

---

###  Step 1: Import Required Libraries

Begin by importing the `great_expectations` and `pandas` libraries.

```python
import great_expectations as gx
import pandas as pd
````

---

###  Step 2: Load Sample Data

Download and load a demo dataset into a Pandas DataFrame.

```python
df = pd.read_csv(
    "https://raw.githubusercontent.com/great-expectations/gx_tutorials/main/data/yellow_tripdata_sample_2019-01.csv"
)
```


---

###  Step 3: Create a Data Context

A Data Context is the main entrypoint for interacting with GX.

```python
context = gx.get_context()
```



---

###  Step 4: Connect to Data and Create a Batch

Define a Data Source, Data Asset, and Batch Definition. Then load your DataFrame as a Batch.

```python
data_source = context.data_sources.add_pandas("pandas")
data_asset = data_source.add_dataframe_asset(name="pd dataframe asset")
batch_definition = data_asset.add_batch_definition_whole_dataframe("batch definition")
batch = batch_definition.get_batch(batch_parameters={"dataframe": df})
```



---

###  Step 5: Create an Expectation

Define an Expectation that the `passenger_count` column should only contain values between 1 and 6.

```python
expectation = gx.expectations.ExpectColumnValuesToBeBetween(
    column="passenger_count", min_value=1, max_value=6
)
```


---

###  Step 6: Validate the Data and View Results

Run the validation and print the results:

```python
validation_result = batch.validate(expectation)
print(validation_result)
```

The output will confirm whether the data met the expectation:

```json
{
  "success": true,
  "expectation_config": {
    "type": "expect_column_values_to_be_between",
    "kwargs": {
      "batch_id": "pandas-pd dataframe asset",
      "column": "passenger_count",
      "min_value": 1.0,
      "max_value": 6.0
    },
    "meta": {}
  },
  "result": {
    "element_count": 10000,
    "unexpected_count": 0,
    "unexpected_percent": 0.0,
    "partial_unexpected_list": [],
    "missing_count": 0,
    "missing_percent": 0.0,
    "unexpected_percent_total": 0.0,
    "unexpected_percent_nonmissing": 0.0,
    "partial_unexpected_counts": [],
    "partial_unexpected_index_list": []
  },
  "meta": {},
  "exception_info": {
    "raised_exception": false,
    "exception_traceback": null,
    "exception_message": null
  }
}
```


---

This simple example illustrates the full lifecycle of data validation using GX Core with Pandas. It can easily be extended to include multiple expectations or be used in automated workflows.


##  Example 2: Validate Data in a SQL Table

### 1. Create Context and Connect

```python
context = gx.get_context()

connection_string = "postgresql+psycopg2://try_gx:try_gx@postgres.workshops.greatexpectations.io/gx_example_db"
data_source = context.data_sources.add_postgres("postgres db", connection_string=connection_string)
data_asset = data_source.add_table_asset(name="taxi data", table_name="nyc_taxi_data")
batch_definition = data_asset.add_batch_definition_whole_table("batch definition")
```


---

### 2. Create Expectation Suite

```python
suite = context.suites.add(gx.ExpectationSuite(name="expectations"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="passenger_count", min_value=1, max_value=6))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="fare_amount", min_value=0))
```


---

### 3. Create a Validation Definition

```python
validation_definition = context.validation_definitions.add(
    gx.ValidationDefinition(name="validation definition", data=batch_definition, suite=suite)
)
```


---

### 4. Create and Run Checkpoint

```python
checkpoint = context.checkpoints.add(
    gx.Checkpoint(name="checkpoint", validation_definitions=[validation_definition])
)
checkpoint_result = checkpoint.run()
print(checkpoint_result.describe())
```


---

## 🔐 Secure Credential Management

### Store Credentials as Environment Variables

```bash
export MY_PG_USER="your_username"
export MY_PG_PASSWORD="your_secret_password"
export MY_PG_HOST="your_db_host"
```

### Reference in Python

```python
connection_string = "postgresql+psycopg2://${MY_PG_USER}:${MY_PG_PASSWORD}@${MY_PG_HOST}/my_db"
```


---

##  Create an Expectation

```python
from great_expectations import expectations as gxe

preset_expectation = gxe.ExpectColumnMaxToBeBetween(
    column="passenger_count", min_value=1, max_value=6
)
```


---

##  Create a Reusable Validation Definition

```python
validation_definition = gx.ValidationDefinition(
    name="validate_daily_taxi_data_against_core_rules",
    data=batch_definition,
    suite=expectation_suite
)

context.validation_definitions.add(validation_definition)
```

This allows for repeatable validations and forms the backbone of your data quality pipelines.




