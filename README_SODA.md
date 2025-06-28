# Soda: The End-to-End Platform for Data Quality

A comprehensive platform for ensuring reliable, trustworthy, and high-quality data across your entire data stack.

---

## What is Soda?

In today's data-driven world, poor data quality leads to flawed business decisions, erodes trust, and creates costly engineering rework. Soda is an open-source, data reliability platform that enables data teams to proactively find, analyze, and resolve data issues before they have a downstream impact.

It provides a unified, declarative language (**SodaCL**) to define what good data looks like, directly within your engineering workflows. Soda then runs tests against your data, monitors for anomalies, and provides a central command center (**Soda Cloud**) for collaboration and incident management.

## Core Capabilities

Soda empowers data teams with a suite of powerful capabilities to manage the entire data quality lifecycle:

*   ✅ **Comprehensive Testing & Validation**: Use the intuitive Soda Checks Language (SodaCL) to define a vast array of tests—from simple null checks and freshness validations to complex SQL-based business logic.

*   🤖 **Automated Monitoring & Anomaly Detection**: Schedule scans to run within your data pipelines (Airflow, Dagster, etc.) or on a regular basis. Leverage machine learning to automatically detect anomalies and unexpected changes in your data patterns.

*   🤝 **Centralized Collaboration & Incident Management**: Soda Cloud acts as your central command center. It visualizes data health over time, creates actionable 'Incidents' from failed checks, and notifies the right people on the right channels (Slack, Teams, Jira).

*   📝 **Proactive Data Contracts**: Shift left and prevent bad data at the source. Implement machine-readable Data Contracts to enforce schema and quality guarantees between data producers and consumers, directly within your CI/CD pipeline.

## Who is Soda For?

Soda is built for modern data teams—including **Data Engineers, Analytics Engineers, Data Scientists, and Data Analysts**—who are committed to delivering reliable data products.

## How Soda Works: The Core Components

Soda's power comes from its modular architecture, which separates the definition of quality, the execution of tests, and the management of results. This process revolves around a few key components:

### 1. SodaCL: The Language of Data Quality
At the heart of Soda is **SodaCL** (Soda Checks Language), a human-readable, domain-specific language (DSL) written in YAML. It provides a simple yet powerful way for both technical and non-technical users to define what good data looks like.

Instead of writing complex SQL queries, you declare your expectations:

```yaml
# In a file named checks.yml
checks for orders:
  - row_count > 0:
      name: Dataset is not empty
  - missing_count(customer_id) = 0:
      name: All orders must have a customer
  - duplicate_count(order_id) = 0:
      name: Order IDs must be unique
````

### 2. The Soda Scan: Executing Checks

A scan is the central action in Soda. When a scan is initiated, Soda's engine performs a critical function:

1. It reads your `checks.yml` file.
2. It translates your SodaCL checks into optimized SQL queries that are native to your data source (e.g., Snowflake, BigQuery, PostgreSQL).
3. It executes these queries directly within your data source.

This "push-down" approach is fundamental to Soda's security and performance model. Your data never leaves your environment—Soda only retrieves the aggregated results of the checks (e.g., a row count, a number of missing values), not the underlying data itself.

### 3. Soda Cloud: The Command Center

While scans can be run from the command line, Soda Cloud is the centralized platform for observability, collaboration, and incident management. It is where you:

* 📊 **Visualize Results**: See the health of your datasets over time through interactive dashboards.
* 🔔 **Manage Incidents**: Automatically create, assign, and track data quality issues from failed checks.
* ⚙️ **Configure Alerts**: Set up rules to notify your team via Slack, MS Teams, or Jira when a data quality issue is detected.
* 🗓️ **Schedule Scans**: Automate your data quality monitoring to run on a schedule without manual intervention.
* 👥 **Collaborate**: Discuss data issues with your team directly within the context of the data.

### 4. Deployment Models: Soda Library & Soda Agent

Soda's execution engine can be deployed in a way that best fits your infrastructure:

* **Soda Library**: The core Python library and Command-Line Interface (CLI). Ideal for self-operated deployments—run scans from your local machine, a CI/CD runner, or a data orchestrator like Airflow.
* **Soda Agent**: A secure, containerized version of the Soda Library. Acts as a bridge, allowing Soda Cloud to initiate scans within your private network without exposing database credentials. This underpins both Soda-hosted and self-hosted deployments, enabling a user-friendly, UI-driven experience.

````markdown
## Getting Started: Your First Data Quality Scan

The fastest way to experience Soda is to run a scan on your local machine using our "Take a Sip" tutorial. This 15-minute guide will walk you through setting up Soda, running it against a sample dataset, and seeing the results.

### Prerequisites

Before you begin, ensure you have the following installed on your system:

* **Python** (version 3.8, 3.9, or 3.10)  
* **Pip** (version 21.0 or greater)  
* **(Optional) Docker Desktop**: To easily spin up a sample PostgreSQL database.

### 1. Set Up Your Project

First, create a project directory and a Python virtual environment. This is a best practice to keep your project dependencies isolated.

```bash
# Create and navigate to your project directory
mkdir soda_project
cd soda_project

# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
# On macOS and Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
````

### 2. Install Soda

Install the Soda Library package for PostgreSQL. This tutorial uses a PostgreSQL sample dataset, but Soda supports over 20 different data sources.

```bash
# Install Soda Library for PostgreSQL
pip install soda-postgres
```

### 3. Configure Your Data Connection

Create a `configuration.yml` file. This file tells Soda how to connect to your data source. For this tutorial, we will use Docker to run a sample PostgreSQL database.

```bash
# Run the sample database in Docker
docker run \
  --name sip-of-soda \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=soda \
  sodadata/soda-adventureworks
```

Now, create the `configuration.yml` file with the following content:

```yaml
# In a new file named configuration.yml
data_source adventureworks:
  type: postgres
  host: localhost
  port: 5432
  username: postgres
  password: soda
  database: postgres
  schema: public
```

### 4. Write Your Data Quality Checks

Create a `checks.yml` file. This is where you define your data quality rules using SodaCL.

```yaml
# In a new file named checks.yml
checks for dim_customer:
  - row_count > 0:
      name: Dataset is not empty
  - missing_count(last_name) = 0:
      name: Last names must be populated
  - duplicate_count(phone) = 0:
      name: Phone numbers must be unique
```

### 5. Run the Scan

You are now ready to run your first Soda scan! Execute the following command in your terminal:

```bash
soda scan -d adventureworks -c configuration.yml checks.yml
```

### 6. Analyze the Results

The output in your terminal will show a summary of the scan, indicating which checks passed and which failed:

```text
Scan summary:
2/3 checks PASSED:
  dim_customer in adventureworks
    Dataset is not empty [PASSED]
    Last names must be populated [PASSED]
1/3 checks FAILED:
  dim_customer in adventureworks
    Phone numbers must be unique [FAILED]
      check_value: 715

Oops! 1 failure. 0 warnings. 0 errors. 2 pass.
```

Congratulations! You've just run your first data quality scan and identified an issue (715 duplicate phone numbers) in your data.


