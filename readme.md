# MQTT Data Validation & Monitoring Pipeline

A real-time, end-to-end solution for validating, processing, and visualizing IoT data streams. This project leverages a modern tech stack including MQTT, FastAPI, Pandera, InfluxDB, Prometheus, and Grafana to create a robust and highly configurable data pipeline.

![Grafana Dashboard](https://i.imgur.com/your-grafana-dashboard-image.png)
_**(NOTE: Please replace this link with an actual screenshot of your main Grafana dashboard.)**_

## 📖 Overview

This project provides a complete ecosystem that captures raw MQTT messages, validates them against dynamic, user-defined schemas, and routes them for persistent storage and real-time visualization.

The core of the system is a FastAPI application that acts as a central hub. It features a powerful web-based **Admin Panel** that allows users to dynamically configure MQTT broker settings, manage topic mappings, and—most importantly—create or edit the Pandera validation schemas on the fly.

Validated and failed data points are intelligently separated. Time-series data is stored persistently in **InfluxDB**, while system performance metrics are exposed to **Prometheus**. Finally, **Grafana** serves as the unified visualization layer, offering comprehensive dashboards for live data monitoring, system health checks, and a powerful alerting system.

## 📚 Table of Contents

- [The Core Philosophy: Data Contracts with Pandera](#the-core-philosophy-data-contracts-with-pandera)
- [Key Features](#-key-features)
- [Tech Stack](#️-tech-stack)
- [Architecture & Detailed Data Flow](#️-architecture--detailed-data-flow)
- [Getting Started](#-getting-started)
- [Usage](#️-usage)
- [Project Structure](#-project-structure)
- [Future Work & Known Limitations](#-future-work--known-limitations)

## The Core Philosophy: Data Contracts with Pandera

In any data-driven system, especially in the world of IoT where data streams from countless diverse sources, the principle of "Garbage In, Garbage Out" holds true. Unreliable, malformed, or unexpected data can cause silent failures, corrupt databases, and lead to flawed analysis. This project's first and most critical objective is to act as a guardian of data quality.

We achieve this by treating data validation not as a simple check, but as a formal **Data Contract**. A Data Contract is an agreement between the data producer (the sensor) and the data consumer (our pipeline) that explicitly defines the structure, format, and rules the data must follow.

To implement and enforce these contracts, we use **Pandera**, a powerful and expressive data validation library for Python's Pandas library.

### A Deeper Look into Pandera

At its core, Pandera allows you to define a `Schema` object that acts as a blueprint for your data. This schema specifies what your `DataFrame` should look like, from column data types to the acceptable range of values within them.

#### Simple Example: Basic Schema Definition

Imagine you expect data about students. A basic schema would define the data types for each column.

```python
import pandas as pd
import pandera as pa

# Define the "contract" or blueprint for our student data
student_schema = pa.DataFrameSchema({
    "student_id": pa.Column(int),
    "student_name": pa.Column(str),
    "exam_score": pa.Column(int),
})

# Create a valid DataFrame
valid_df = pd.DataFrame({
    "student_id": [101, 102],
    "student_name": ["Alice", "Bob"],
    "exam_score": [85, 92],
})

# This will pass without errors
validated_df = student_schema.validate(valid_df)
print("Validation successful!")
```

#### The Real Power: Adding Checks

Pandera's true strength lies in its `Check` objects, which allow you to define rules for the *values* themselves. Let's make our contract stricter: exam scores must be between 0 and 100.

```python
# A stricter schema with value-level rules
strict_student_schema = pa.DataFrameSchema({
    "student_id": pa.Column(int),
    "student_name": pa.Column(str),
    "exam_score": pa.Column(int, pa.Check.in_range(0, 100)), # Add a Check
})

# Create an invalid DataFrame
invalid_df = pd.DataFrame({
    "student_id": [103],
    "student_name": ["Charlie"],
    "exam_score": [105],  # This value violates the in_range check
})

try:
    strict_student_schema.validate(invalid_df)
except pa.errors.SchemaError as e:
    print("Validation failed. Pandera provides detailed error reports:")
    # This error object contains a DataFrame of all failure cases
    print(e.failure_cases)
```
When this validation fails, Pandera doesn't just return `False`. It raises a `SchemaErrors` exception containing a rich DataFrame that details exactly which column, which check, and which value caused the failure. This structured error reporting is critical for our pipeline to generate meaningful failure messages.

### Why Pandera for This Project?

-   **Decoupling Rules from Code**: By defining schemas, we separate the *what* (the data contract) from the *how* (the processing logic). In our project, we take this a step further by defining these schemas in external `.json` files, making the validation logic completely dynamic and configurable via the Admin Panel without a single line of code change or server restart.
-   **Clarity and Readability**: Schemas are easy to read and understand, serving as a single source of truth for what the data should look like.
-   **Guaranteed Data Quality**: By validating at the entry point, every downstream component—from the InfluxDB database to the Grafana dashboards—is guaranteed to receive clean, predictable, and reliable data.

By placing Pandera at the heart of our ingestion process, we transform the pipeline from a passive receiver of information into an active guardian of data quality.

## ✨ Key Features

-   **Real-time Data Processing**: Ingests and processes MQTT data streams with low latency.
-   **Dynamic Schema Validation**: Utilizes Pandera for robust data validation against user-defined JSON schemas.
-   **Fully-Featured Admin Panel**: A web-based UI to manage MQTT settings, topic mappings, and validation schemas without any downtime.
-   **Live Data Dashboard**: A simple, real-time dashboard to visualize the flow of validated and failed messages as they are processed.
-   **Persistent Time-Series Storage**: Stores all processed data in InfluxDB, preserving historical records for detailed analysis and querying.
-   **Comprehensive Monitoring**: Exposes key performance indicators (KPIs) like message counts and error rates to Prometheus for system health monitoring.
-   **Advanced Visualization & Alerting**: Leverages Grafana to create detailed, interactive dashboards from both InfluxDB (historical data) and Prometheus (metrics), complete with a powerful, configurable alerting engine.
-   **Containerized Environment**: The entire application stack is containerized with Docker and orchestrated with Docker Compose for one-command setup and consistent deployment across any environment.

## 🛠️ Tech Stack

This project integrates a variety of powerful tools and libraries. The entire environment is managed by Docker Compose, ensuring version consistency and easy setup.

| Category                  | Technology / Library  | Version           | Purpose                                                                          |
| :------------------------ | :-------------------- | :---------------- | :------------------------------------------------------------------------------- |
| **Backend (Python)**      | Python                | `3.10`            | The core programming language for the application logic.                         |
|                           | FastAPI               | `0.116.1`         | A modern, high-performance web framework for building APIs.                      |
|                           | Uvicorn               | `0.35.0`          | A lightning-fast ASGI server that runs the FastAPI application.                  |
|                           | Paho-MQTT             | `2.1.0`           | A Python client library for connecting to the MQTT broker for data ingestion.    |
|                           | Pandera               | `0.25.0`          | A data validation library used to enforce schema rules on incoming data.         |
|                           | Pandas                | `2.3.1`           | The core library for data manipulation, used as a backbone for Pandera.          |
|                           | InfluxDB Client       | `1.49.0`          | The official Python client for writing data points to InfluxDB.                  |
|                           | Prometheus Client     | `0.22.1`          | A library for instrumenting the application and exposing metrics to Prometheus.  |
|                           | Websockets            | `15.0.1`          | Enables real-time, two-way communication between the server and clients.         |
|                           | Jinja2                | `3.1.6`           | A templating engine used by FastAPI to render HTML pages.                        |
|                           | AIOFiles              | `24.1.0`          | Provides asynchronous file I/O, used for non-blocking file operations.           |
|                           | Python-Multipart      | `0.0.20`          | A streaming multipart parser, required by FastAPI for form data.                 |
| **Frontend**              | JavaScript (ES6+)     | -                 | Powers the interactivity of the Admin Panel and the Live Dashboard.              |
|                           | MQTT.js               | -                 | A JavaScript client library for connecting the Live Dashboard to the MQTT broker.|
|                           | HTML5 / CSS3          | -                 | Standard languages for structuring and styling the web interfaces.               |
| **Infrastructure & Data** | Docker & Docker Compose | -               | Containerizes the application and all services for easy, reliable deployment.  |
|                           | InfluxDB              | `2.7`             | A time-series database for persistently storing all message and error data.      |
|                           | Prometheus            | `v2.x`            | An open-source monitoring system for collecting application performance metrics. |
|                           | Grafana               | `latest`          | An open-source platform for visualizing data and creating powerful alerts.       |

## 🏗️ Architecture & Detailed Data Flow

This project is built on a microservices-oriented architecture where each component has a distinct responsibility. All services are containerized using Docker, ensuring they operate in an isolated and consistent environment. This section provides a deep dive into the system's initialization, the journey of a single data message, and the dynamic configuration loop that makes the system truly flexible.

![System Architecture Diagram](https://i.imgur.com/your-architecture-diagram.png)
_**(NOTE: A diagram showing the relationships between publishers, MQTT broker, FastAPI app, InfluxDB, Prometheus, and Grafana would be highly effective here.)**_

### Stage 1: System Initialization

When you run `docker-compose up`, the entire ecosystem comes to life. The process for our core application is as follows:
1.  The `fastapi_app` container starts, executing `main.py` with the Uvicorn server.
2.  FastAPI's `lifespan` event is triggered on startup. This is our entry point for initialization.
3.  The application reads the `config.json` file to get the initial MQTT broker settings and topic mappings.
4.  A new instance of the `MQTTClient` class from `mqtt_manager.py` is created. This client is initialized with the topic mappings read from the config file.
5.  This `MQTTClient` instance is started in a **separate background thread**, ensuring that the MQTT client's blocking loop doesn't freeze the FastAPI web server.
6.  The `MQTTClient` connects to the broker and, upon a successful connection (`on_connect` callback), it subscribes to every `source` topic defined in the topic mappings (e.g., `/sensor1`, `/sensor2`, etc.).
7.  At this point, the system is fully operational and actively listening for incoming data on the configured topics.

### Stage 2: The Journey of a Single Message

Here is a step-by-step breakdown of what happens when a sensor publishes a message:

1.  **Publication**: A sensor (e.g., `sensor1_publisher.py`) publishes a JSON payload to a topic like `/sensor1`.

2.  **Ingestion**: The background `MQTTClient` thread receives the message, triggering its `on_message` callback method.

3.  **Schema Lookup & Dynamic Validation**:
    -   The client uses its in-memory `topic_mappings` to find the associated validation schema path (e.g., `schemas/sensor1.json`) for the incoming topic.
    -   The `build_schema_from_json` utility function is called. This function reads the `.json` file and dynamically constructs a `pandera.DataFrameSchema` object in memory. This allows schemas to be edited and reloaded without a server restart.
    -   The incoming JSON payload is validated against this schema. Pandera checks for data types, nullability, value ranges, and extra fields (if `strict: true`). The `coerce: true` setting provides flexibility by automatically converting compatible types (e.g., an integer `5` to a float `5.0`).

4.  **Bifurcation (The Split)**: Based on the validation outcome, the data flow splits.

    #### A) If Validation Succeeds (`VALIDATED`):
    1.  **Republish for Live View**: The clean, original data is immediately republished to the corresponding `validated` topic (e.g., `/sensor1/validated`). This stream is consumed by the **Live Web Dashboard** (`app.js`).
    2.  **Persist to InfluxDB**: The `InfluxDBWriter` asynchronously writes the data to InfluxDB. A `Point` is created with the measurement `mqtt_messages`, a tag `status=validated`, and fields for each data point (e.g., `temperature`, `humidity`).
    3.  **Increment Prometheus Counter**: The `mqtt_messages_processed_total` Prometheus `Counter` is incremented with labels `status="validated"` and the correct `sensor_id`. This updates our high-level monitoring metrics.

    #### B) If Validation Fails (`FAILED`):
    1.  **Generate Error Report**: The `SchemaErrors` exception is caught. The `utils.parse_pandera_errors` function is called to transform the complex exception into a clean, structured JSON error report. This utility also prioritizes errors (e.g., `wrong_type` is more critical than `out_of_range`) to provide the most relevant root cause.
    2.  **Republish for Live View**: The detailed error report is published to the `failed` topic (e.g., `/sensor1/failed`) for the **Live Web Dashboard**.
    3.  **Persist to InfluxDB**: The error report is written to InfluxDB with the tag `status=failed`.
    4.  **Increment Prometheus Counter**: The Prometheus `Counter` is incremented for *each error found* in the report, using labels `status="failed"`, the `sensor_id`, and the specific `error_type`. This allows for granular tracking of data quality issues.

### Stage 3: The Dynamic Configuration Loop

The system's true power lies in its ability to be reconfigured on the fly via the **Admin Panel**.

1.  **User Action**: The user navigates to the Admin Panel (`http://localhost:8000/admin`). The JavaScript on this page fetches all current settings from the FastAPI backend via GET requests (e.g., `/api/topic-mappings`).
2.  **Configuration Change**: The user modifies a setting—for example, changing a schema file or updating a `validated` topic destination—and clicks "Save".
3.  **API Call**: The frontend sends a `POST` request to the appropriate endpoint in `main.py` (e.g., `/api/topic-mappings`), containing the **full, updated configuration** for that section.
4.  **Backend Response (`main.py`)**:
    -   The API endpoint receives the new configuration and overwrites the `config.json` file on disk, persisting the change.
    -   **Crucially, it calls the `restart_mqtt_client()` function.** This function gracefully stops the old `MQTTClient` background thread and immediately starts a new one.
    -   The new `MQTTClient` thread initializes by reading the now-updated `config.json`, meaning it automatically uses the latest settings (e.g., subscribing to new topics or using new schema paths).
    -   Finally, the backend broadcasts a `"config_updated"` message over the WebSocket connection.
5.  **System-Wide Sync**:
    -   The **Live Web Dashboard** (`app.js`), connected to the WebSocket, receives the `"config_updated"` message. This triggers its `initializeApp()` function, causing it to re-fetch the configuration from the API and subscribe to the new, correct `validated` and `failed` topics on the MQTT broker. This ensures all parts of the system are always in sync.

### Stage 4: Visualization and Alerting

-   **Grafana** acts as the final presentation layer, using two distinct data sources:
    -   **Prometheus**: For querying high-level operational metrics like message rates (`rate(...)`), success/failure ratios, and error counts. This monitors the *health* of the pipeline.
    -   **InfluxDB**: For querying the rich, historical, raw data content using the Flux language (e.g., `SELECT humidity WHERE topic='/sensor1'`). This is for analyzing the *content* of the data.
-   The **Alerting Engine** in Grafana continuously evaluates rules against both data sources, providing comprehensive monitoring of both system health and data quality.

### Data Access and Integration Model

The InfluxDB, Prometheus, and Grafana services do not directly subscribe to MQTT topics. Instead, the **FastAPI application (`fastapi_app`) acts as the central bridge and translator** for all of them. It is the only component that processes the raw MQTT messages, subsequently preparing and serving the data in formats that each specialized tool can understand.

#### InfluxDB Integration (The "Push" Model)

InfluxDB stores the rich, detailed content of every message. Our application actively **pushes** data to it.

1.  **The Component**: Inside `mqtt_manager.py`, we have an `InfluxDBWriter` class.
2.  **The Trigger**: After a message is validated (either successfully or as a failure), the `mqtt_manager` calls the appropriate method on the writer (e.g., `write_validated_data`).
3.  **The Action**: The writer constructs a data `Point` using the `influxdb-client` library. This `Point` is structured with a measurement (`mqtt_messages`), tags for easy filtering (like `status`, `topic`, `sensor_id`), and fields containing the actual data (like `temperature`, `humidity`, or the full JSON error report).
4.  **The Result**: This data point is sent over HTTP to the InfluxDB container. InfluxDB receives it and stores it, making the full historical record of every message available for querying.

#### Prometheus Integration (The "Pull" Model)

Prometheus stores high-level performance metrics. It operates on a **pull** model, meaning it periodically scrapes (requests) data from our application.

1.  **The Component**: We use the `prometheus-client` library within `mqtt_manager.py` to define a `Counter` metric named `mqtt_messages_processed_total`.
2.  **The Trigger**: Every time a message is processed (validated or failed), our code simply increments this in-memory counter with the appropriate labels (`status`, `sensor_id`, `error_type`).
3.  **The Exposure**: The FastAPI application automatically exposes a special endpoint: `http://localhost:8000/metrics`. This page serves the current value of all our counters in a simple text format that Prometheus is designed to understand.
4.  **The Action**: The `prometheus.yml` configuration file tells the Prometheus container to "scrape" this `/metrics` endpoint every 15 seconds. Prometheus visits the URL, reads the values, and stores them in its own time-series database.
5.  **The Result**: Prometheus builds a highly efficient database of our system's performance over time, without ever needing to know the content of the actual MQTT messages.

#### Grafana's Role (The Unifier)

Grafana is the final piece that brings everything together. It does not talk to our FastAPI application at all. Instead:
-   It is configured with **two Data Sources**: one pointing to the Prometheus container (`http://prometheus:9090`) and another pointing to the InfluxDB container (`http://influxdb:8086`).
-   When you view a dashboard, Grafana sends queries to these data sources—PromQL queries to Prometheus for performance metrics and Flux queries to InfluxDB for historical data content—and masterfully combines the results into the unified dashboards you see.


## 🚀 Getting Started

Follow these instructions to get the entire project stack up and running on your local machine for development and testing purposes.

### Prerequisites

Make sure you have the following software installed on your system:

-   **Docker**: [Download & Install Docker](https://www.docker.com/products/docker-desktop/)
-   **Docker Compose**: Docker Desktop for Windows and Mac includes Docker Compose. For Linux, follow the [official installation guide](https://docs.docker.com/compose/install/).

### Installation & Launch

1.  **Download the Project:**  
    Download the project files as a ZIP archive. If you are on the GitHub page, click the green `<> Code` button, then select `Download ZIP`.

2.  **Extract the Files:**  
    Extract the contents of the downloaded ZIP file to a location of your choice on your computer. The extracted folder will be named something like `mqtt_validation_project-main`.

3.  **Navigate to the Project Directory:**  
    Open your terminal or command prompt and navigate into the extracted project folder.

    ```bash
    cd path/to/your/mqtt_validation_project-main
    ```

4.  **Build and run the services:**  
    Use Docker Compose to build the container images and start all the services in detached mode (`-d`).

    ```bash
    docker-compose up --build -d
    ```

    This command will:
    -   Pull the necessary base images (Python, InfluxDB, Prometheus, Grafana).
    -   Build the custom Docker image for our FastAPI application based on the local files.
    -   Create and start containers for all services and connect them in a dedicated network.

5.  **Verify the services are running:**  
    You can check the status of all running containers with:

    ```bash
    docker-compose ps
    ```

    You should see all services (`fastapi_app`, `influxdb`, `prometheus`, `grafana`) with a status of `Up` or `Running`. To see the real-time logs of the main application, you can run:
    
    ```bash
    docker-compose logs -f fastapi_app
    ```

That's it! The entire pipeline is now running.

## 🕹️ Usage

Once all services are up and running, you can access the different parts of the system through your web browser. Each interface serves a unique purpose.

### Admin Panel: `http://localhost:8000/admin`

**What it is**: The central control room for the entire data pipeline.

**Purpose**: This web interface gives you complete, real-time control over the data pipeline's configuration. All changes made here are applied instantly without needing to restart any services, allowing for true dynamic behavior.

The panel is divided into three main sections:

#### 1. MQTT Broker Settings
This section at the top allows you to configure the connection to your MQTT broker.
-   **Broker**: The address of the MQTT broker (e.g., `broker.hivemq.com`).
-   **Port**: The connection port (usually `1883` for unencrypted connections).
-   **Saving**: After making changes, click the **"Save MQTT Settings"** button. The button will visually indicate when there are unsaved changes, ensuring you don't forget to apply them.

#### 2. Topic Mappings Management
This is where you define the core routing and validation logic of the pipeline. Each "mapping" is a card that represents a contract for a specific data source.
-   **Source Topic**: The raw topic the system subscribes to (e.g., `/sensor1`). This is the entry point for data.
-   **Validated Topic**: The topic where clean, successfully validated data will be republished.
-   **Failed Topic**: The topic where a detailed error report will be published if the data fails validation.
-   **Schema File**: A dropdown menu to select the validation contract (a `.json` file from the `schemas/` directory) that should be applied to the data from the `Source Topic`.

**Actions:**
-   **Add a New Mapping**: Click the **"Add New Mapping"** button, fill in the details for a new sensor or data source, and click the save icon.
-   **Edit an Existing Mapping**: Simply click on any field in a card, modify its value, and the card will be marked for saving.
-   **Delete a Mapping**: Click the trash can icon on a card to remove it.
-   **Saving Changes**: After adding, editing, or deleting mappings, click the main **"Save Topic Mappings"** button at the bottom of the section to apply all changes.

#### 3. Schema Management
This powerful section on the right allows you to manage the data contracts (Pandera schemas) themselves directly from the UI.

-   **File List**: Shows all available `.json` schema files in the `schemas/` directory. Clicking a file name loads its content into the editor below.
-   **Create New Schema**: The **"Create New Schema"** button allows you to start a new, empty schema file.

**The Schema Editor:**
The editor has two modes, allowing both technical and non-technical users to manage schemas effectively:

-   **Visual Editor (Default)**: A user-friendly, form-based interface for building a schema without writing any code.
    -   You can define general schema settings like `strict` mode (to reject extra fields).
    -   Add `Columns` by name, specify their `Data Type` (e.g., `str`, `int`, `float`, `datetime`), and set properties like `Nullable` or `Unique`.
    -   For each column, you can add multiple `Checks` to enforce specific rules (e.g., `in_range`, `greater_than`, `str_matches` for regex).
-   **Raw Text (JSON) Editor**: For advanced users, this mode allows you to view, edit, or paste the schema definition as a raw, strict JSON object. The system automatically syncs the content between the Visual and Raw editors.

**How it Works (The Magic of Dynamic Configuration):**
When you save any change in the Admin Panel (be it MQTT settings, mappings, or a schema), the following happens in sequence:
1.  The frontend sends the updated configuration to the backend API.
2.  The backend (`main.py`) persists the changes to the appropriate file (`config.json` or a file in `schemas/`).
3.  **Crucially, it gracefully restarts the internal MQTT client (`mqtt_manager.py`) in a background thread.**
4.  The new MQTT client initializes by reading the updated configuration files, instantly applying the new settings (e.g., subscribing to new topics or using a modified schema).
5.  The backend also sends a WebSocket notification to the Live Data Dashboard, ensuring it re-syncs and subscribes to the correct topics.

This entire process happens in seconds, providing a seamless and truly dynamic control over your data pipeline.

---

### Live Data Dashboard: `http://localhost:8000/dashboard`

**What it is**: A real-time, lightweight message feed designed for immediate operational awareness.

**Purpose**: While Grafana is used for deep analysis and historical trends, the Live Data Dashboard serves a different, more immediate purpose: to provide a live, unfiltered view of the data pipeline's pulse. It answers the question, "What is happening in the system *right now*?"

**How It Works:**
The dashboard's JavaScript (`app.js`) connects directly to the MQTT broker using the MQTT.js library. It doesn't interact with any databases. When the page loads, it first fetches the current topic mappings from the backend API. It then subscribes to all the `validated` and `failed` topics defined in the Admin Panel.

This direct connection to the message bus makes it incredibly fast and efficient.

**Key Features:**

-   **Live Message Cards**: Every message republished by the `mqtt_manager` appears instantly as a card in the main feed.
    -   **Green `VALIDATED` Cards**: Show clean data that has successfully passed schema validation.
    -   **Red `FAILED` Cards**: Display the detailed error report for messages that failed validation. This is invaluable for real-time debugging, as you can see exactly which field failed, why, and what the original problematic data was.
-   **Real-time Statistics**: The top-left corner shows a running count of total messages received, as well as a breakdown of validated vs. failed messages for the current session.
-   **Dynamic Filtering**: The sidebar allows you to filter the live feed to quickly find what you're looking for.
    -   **Filter by Status**: Show only `Validated` messages, only `Failed` messages, or both.
    -   **Filter by Source Topic**: The list of source topics is dynamically generated based on the configuration in the Admin Panel. You can select one or more topics to isolate data from specific sensors.
    -   **Filter by Error Type**: For failed messages, you can drill down into specific error categories (e.g., `wrong_type`, `out_of_range`, `bad_format`) to diagnose recurring data quality issues.
-   **Automatic Re-synchronization**: The dashboard maintains a WebSocket connection to the backend server. If you make a change in the Admin Panel (e.g., add a new sensor topic), the backend sends a `"config_updated"` notification. The dashboard automatically receives this, re-fetches the configuration, and subscribes to the new topics without requiring a page refresh. This ensures it is always in sync with the pipeline's current state.

---

### Grafana Dashboards: `http://localhost:3000`

**What it is**: The main platform for advanced data visualization, long-term analysis, and alerting.

**Login**:
-   **Username**: `admin`
-   **Password**: `admin`
-   *(You will be prompted to change this on first login.)*

**Purpose**: Grafana is the most powerful component of our visualization stack. It unifies data from multiple sources into a single, cohesive dashboard, allowing you to correlate system performance with the actual data being processed. In our project, Grafana is configured with two distinct data sources, each serving a specific purpose.

#### The Two Pillars: InfluxDB and Prometheus Integration

Understanding why we use two data sources is key to understanding the system's observability strategy.

1.  **InfluxDB - The "What"**:
    -   **Data Type**: Stores the rich, raw, historical data (the *content* of the messages). Every temperature reading, humidity value, and detailed error report is stored here.
    -   **Query Language**: Flux.
    -   **Use Case**: Used for deep analysis of the data itself. Answers questions like, *"What was the trend of `radiation_level` for `sensor4` over the last 24 hours?"* or *"Show me all `failed` messages for `sensor1` where the `error_type` was `out_of_range`."*

2.  **Prometheus - The "How Well"**:
    -   **Data Type**: Stores time-series metrics about the *performance* and *health* of the application. It doesn't know what the humidity value was, but it knows *how many* messages were processed.
    -   **Query Language**: PromQL.
    -   **Use Case**: Used for monitoring the health and throughput of the pipeline. Answers questions like, *"What is the rate of incoming messages per second from `sensor1`?"* or *"What is the ratio of `validated` to `failed` messages over the last hour?"*

By combining these two, we can answer complex questions, such as "Did the rate of `out_of_range` errors increase after the per-second message rate spiked?"

#### Example Queries Used in Our Dashboards

Here are some examples of the queries that power our pre-configured Grafana dashboard, showcasing how we use both data sources.

**1. Visualizing a Specific Data Field (InfluxDB - Flux)**
This query retrieves the historical `humidity` values for `sensor1`, allowing us to plot its trend over time.

```bash
// InfluxDB Flux Query
from(bucket: "mqtt_data")
  |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
  |> filter(fn: (r) =>
    r._measurement == "mqtt_messages" and
    r.status == "validated" and
    r.topic == "/sensor1" and
    r._field == "humidity"
  )
  |> yield(name: "humidity")
```

**2. Calculating the Live Message Rate (Prometheus - PromQL)**
This query calculates the per-second average rate of `validated` messages from `sensor1` over the last minute. This is perfect for a "Stat" or "Gauge" panel to show live throughput.

```promql
// Prometheus PromQL Query
rate(mqtt_messages_processed_total{sensor_id="sensor1", status="validated"}[1m])
```

**3. Counting Total Failures by Error Type (Prometheus - PromQL)**
This query counts the total increase in failed messages over the selected time range and groups them by the `error_type`. This is ideal for a pie chart or bar chart to quickly identify the most common data quality issues.

```promql
// Prometheus PromQL Query
sum(increase(mqtt_messages_processed_total{status="failed"}[$__range])) by (error_type)
```

#### The Alerting System

Beyond simple visualization, one of Grafana's most powerful capabilities is its integrated alerting engine. Instead of requiring a user to passively watch dashboards, the system can be configured to proactively issue alerts when data breaches predefined thresholds. This section explains how this system works, using our critical **High Radiation Alert** as a case study.

**How to Recreate or Understand an Alert (Case Study: High Radiation)**

This is a guide for understanding the logic behind our alerts. You can follow these steps in the Grafana UI by editing the "Live Radiation Level" panel and navigating to the "Alert" tab.

1.  **The Goal**: The objective is to trigger an alert instantly if the `radiation_level` from `sensor4` exceeds a critical safety threshold of `1.0 µSv/h`.

2.  **The Data Source & Query (InfluxDB)**: First, we need to isolate the exact data point to monitor. The alert rule is attached to a panel that uses the following Flux query to get the latest radiation level from InfluxDB:
    ```flux
    from(bucket: "mqtt_data")
      |> range(start: -1m) // Look at recent data
      |> filter(fn: (r) =>
        r._measurement == "mqtt_messages" and
        r.status == "validated" and
        r.topic == "/sensor4" and
        r._field == "radiation_level"
      )
      |> last() // We only care about the most recent value
    ```

3.  **The Condition (The Trigger Rule)**: The core of the alert is a simple but powerful condition:
    -   `WHEN` **`last()`** `OF` **`query_result`** `IS ABOVE` **`1.0`**
    -   This tells Grafana: "Look at the single, most recent value returned by our query. If that value is greater than 1.0, the condition is met."

4.  **The Evaluation Behavior (The Speed)**: This defines how quickly the system reacts.
    -   **Evaluation Interval**: The rule is evaluated every **`10 seconds`**. This means Grafana checks the radiation level against the threshold six times per minute, providing rapid detection.
    -   **Pending Period (`For`)**: This is set to **`0s`**. This is critical. It means the moment the condition is met, the alert immediately enters the `Firing` state without any delay. For less critical alerts, you might set this to `1m` to avoid alerts from brief, transient spikes.

**What Happens When an Alert Fires?**
-   The border of the panel on the dashboard will turn red and show a pulsing heartbeat icon.
-   A red vertical line (an "annotation") will appear on all graphs at the timestamp the alert was triggered.
-   In a production environment, this could also trigger notifications to email, Slack, or other services.

This same logic is applied to other pre-configured alerts, such as the **High Humidity Alert** (using InfluxDB) and the **Sensor Inactivity Alert** (which uses Prometheus and the `rate()` function to check if a sensor has stopped sending data).

---

### Prometheus UI: `http://localhost:9090`

**What it is**: The raw, built-in user interface for the Prometheus monitoring system.

**Login**: No authentication is configured by default.

**Purpose**: While Grafana is our primary tool for *visualizing* metrics, the Prometheus UI is the best tool for *exploring and debugging* them. It serves two main purposes for a developer:

1.  **Metric Exploration**: The "Expression" bar allows you to instantly see which metrics our FastAPI application is exposing and what their current values and labels are. For example, typing `mqtt_messages_processed_total` and clicking "Execute" will show you every single time-series for that metric, allowing you to confirm that labels like `sensor_id` and `error_type` are being reported correctly.

2.  **PromQL Query Prototyping**: Before building a complex panel in Grafana, you can use this interface to build, test, and refine your PromQL queries. The "Graph" tab provides a simple, instant visualization, which is perfect for ensuring your query returns the data you expect before you spend time configuring a Grafana panel.

---

### InfluxDB UI: `http://localhost:8086`

**What it is**: A powerful web-based data management and administration interface for the InfluxDB database.

**Login**:
-   **Username**: `my-user`
-   **Password**: `my-password`

**Purpose**: This UI provides direct, low-level access to the time-series data stored by our pipeline. It's an essential tool for deep-dives, administration, and debugging data-related issues.

**Key Features for Our Project:**

-   **Data Explorer**: This is the most used feature. It allows you to build and execute **Flux** queries to inspect the raw data. You can switch between a Script Editor for writing queries manually and a visual Query Builder. This is the ultimate source of truth to confirm that data is being written correctly to the database with the right tags and fields.
-   **Buckets Management**: You can view the `mqtt_data` bucket, see its current retention policies (how long data is stored), and manage other database settings.
-   **Load Data**: While our project writes data via the API, this section allows you to manually upload or paste sample data, which can be useful for testing specific scenarios.

## 📂 Project Structure

The project repository is organized to clearly separate concerns. Here are the most important files and directories:

```yaml
.
├── schemas/              # Contains all Pandera validation schemas in JSON format.
├── sensors/              # Includes various Python scripts that simulate sensor data publication for testing.
├── static/               # Frontend assets (HTML, CSS, JS) for the Admin Panel and Live Dashboard.
├── config.json           # The heart of the system's configuration: MQTT settings and topic mappings.
├── docker-compose.yml    # Orchestrates the deployment of all services (app, databases, monitoring).
├── Dockerfile            # Defines the build process for the FastAPI application container.
├── main.py               # The main FastAPI application file: handles APIs, WebSockets, and overall application state.
├── mqtt_manager.py       # Core logic for the MQTT client: handles connections, message validation, and data routing.
├── prometheus.yml        # Configuration file for Prometheus, defining scrape targets.
├── requirements.txt      # Lists the Python dependencies for the application.
└── utils.py              # Utility functions, such as the Pandera error parser.
```

## 🎯 Future Work & Known Limitations

This project provides a robust foundation for a real-time data validation pipeline. The following areas represent opportunities for future development and enhancement:

-   **Enhanced Security Layer**: The current implementation lacks authentication and authorization for the Admin Panel and its corresponding APIs. A crucial next step for any production-like environment would be to implement a robust security layer (e.g., using OAuth2 or API keys) to protect sensitive system configurations.

-   **Configurable Alert Notifications**: Grafana's alerting engine is capable of sending notifications to various channels (Email, Slack, PagerDuty, etc.). A key improvement would be to fully configure and document these notification channels, transforming alerts from simple dashboard indicators into actionable, real-time notifications.

-   **Integrated MQTT Broker**: The system currently relies on a public, external MQTT broker. For a more self-contained, secure, and reliable deployment, an integrated broker service (e.g., Mosquitto) could be added to the `docker-compose.yml` stack.

-   **Support for Advanced Pandera Features**: The validation logic is currently built around dynamically loading `DataFrameSchema` definitions. The system could be extended to support other powerful Pandera features, offering alternative, code-centric validation approaches. This could include:
    -   **Integration with `DataFrameModel`**: Allowing developers to define schemas as Python classes that inherit from `pa.DataFrameModel`. This provides the benefits of static type checking and IDE auto-completion for schema definitions.
    -   **Decorator-Based Validation**: Integrating with Pandera's function decorators (`@pa.check_input`, `@pa.check_output`) for schema enforcement directly at the function level within the application code.

-   **Integration with Real-World Data Streams**: While the provided simulators are effective for testing, a future milestone would involve integrating and testing the pipeline with data from actual physical sensors to validate its performance and resilience under real-world conditions.

-   **AI-Powered Schema and Anomaly Detection**: A forward-looking enhancement could involve integrating machine learning models to analyze incoming data streams. This could enable advanced features such as:
    -   **Automatic Schema Inference**: Generating a baseline Pandera schema by analyzing a sample of the data.
    -   **Dynamic Anomaly Detection**: Automatically adjusting alarm thresholds in Grafana based on learned normal operating behaviors, moving from static thresholds to dynamic anomaly detection. 
