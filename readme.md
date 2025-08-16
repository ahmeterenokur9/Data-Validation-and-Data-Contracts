# MQTT Data Validation & Monitoring Pipeline

A real-time, end-to-end solution for validating, processing, and visualizing IoT data streams. This project leverages a modern tech stack including MQTT, FastAPI, Pandera, InfluxDB, Prometheus, and Grafana to create a robust and highly configurable data pipeline.

![Grafana Dashboard](https://i.imgur.com/your-grafana-dashboard-image.png)
_**(NOTE: Please replace this link with an actual screenshot of your main Grafana dashboard.)**_

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

## 📖 Overview

This project provides a complete ecosystem that captures raw MQTT messages, validates them against the dynamic, user-defined schemas described above, and routes them for persistent storage and real-time visualization.

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

## 🚀 Getting Started

Follow these instructions to get the entire project stack up and running on your local machine for development and testing purposes.

### Prerequisites

Make sure you have the following software installed on your system:

-   **Docker**: [Download & Install Docker](https://www.docker.com/products/docker-desktop/)
-   **Docker Compose**: Docker Desktop for Windows and Mac includes Docker Compose. For Linux, follow the [official installation guide](https://docs.docker.com/compose/install/).
-   **Git**: [Download & Install Git](https://git-scm.com/downloads)

### Installation & Launch

1.  **Clone the repository:**  
    Open your terminal and clone the project repository to your local machine.

    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    ```
    _**(NOTE: Please replace this URL with your actual repository URL.)**_

2.  **Navigate to the project directory:**

    ```bash
    cd mqtt_validation_project
    ```

3.  **Build and run the services:**  
    Use Docker Compose to build the container images and start all the services in detached mode (`-d`).

    ```bash
    docker-compose up --build -d
    ```

    This command will:
    -   Pull the necessary base images (Python, InfluxDB, Prometheus, Grafana).
    -   Build the custom Docker image for our FastAPI application.
    -   Create and start containers for all services.
    -   Connect them in a dedicated network.

4.  **Verify the services are running:**  
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

Once all services are up and running, you can access the different parts of the system through your web browser.

-   **Admin Panel**: `http://localhost:8000/admin`
    -   This is the central hub for managing the entire pipeline. Here you can configure MQTT broker settings, add/remove/edit topic mappings, and manage validation schemas.

-   **Live Data Dashboard**: `http://localhost:8000/`
    -   A real-time view of the validated and failed messages as they are processed by the system.

-   **Grafana Dashboard**: `http://localhost:3000`
    -   The main visualization platform.
    -   **Login**: Use `admin` for both username and password. You will be prompted to change the password on your first login.
    -   The pre-configured dashboard will be available to view data from both InfluxDB and Prometheus, and to see active alerts.

-   **Prometheus UI**: `http://localhost:9090`
    -   Allows you to explore the raw metrics collected from the FastAPI application. You can use it to test and debug PromQL queries.

-   **InfluxDB UI**: `http://localhost:8086`
    -   Provides direct access to the time-series database. You can explore the raw data, run Flux queries, and manage your database buckets.

## 📂 Project Structure

The project repository is organized to clearly separate concerns, making it easier to navigate and maintain.

    .
    ├── schemas/              # Contains all Pandera validation schemas in JSON format.
    ├── sensors/              # Includes Python scripts that simulate sensor data publication.
    │   ├── gui_publisher.py  # A user-friendly GUI for manual message publishing and testing.
    │   └── ...
    ├── static/               # Frontend assets for the Admin Panel and Live Dashboard.
    │   ├── admin.html
    │   ├── dashboard.html
    │   └── ...
    ├── templates/            # HTML templates rendered by FastAPI.
    ├── config.json           # The heart of the system's configuration: MQTT settings and topic mappings.
    ├── docker-compose.yml    # Orchestrates the deployment of all services (app, databases, monitoring).
    ├── Dockerfile            # Defines the build process for the FastAPI application container.
    ├── main.py               # The main FastAPI application file: handles APIs, WebSockets, and lifespan events.
    ├── mqtt_manager.py       # Core logic for the MQTT client: handles connections, message validation, and republishing.
    ├── prometheus.yml        # Configuration file for Prometheus, defining scrape targets.
    ├── requirements.txt      # Lists the Python dependencies for the application.
    └── utils.py              # Utility functions, such as the Pandera error parser.

## 🎯 Future Work & Known Limitations

This project provides a robust foundation, but there are several areas for potential improvement and expansion:

-   **Enhanced Security**: Implement authentication and authorization for the Admin Panel and API endpoints to secure the configuration.
-   **Schema Versioning**: Introduce a system to version control schemas, allowing for smoother transitions when sensor data formats change.
-   **More Comprehensive Testing**: Add a suite of unit and integration tests to improve code reliability and catch regressions.
-   **CI/CD Pipeline**: Implement a Continuous Integration/Continuous Deployment pipeline to automate testing and deployment processes.
-   **Data Backfilling**: Develop a mechanism for reprocessing historical data if a validation schema is updated. 
