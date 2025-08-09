# Dynamic MQTT Data Validation and Monitoring System

A real-time data validation pipeline for MQTT streams, featuring a dynamic web-based control panel and a complete observability stack. This project is designed to capture, validate, and monitor IoT data flows with high reliability and flexibility.

![Project Architecture](https://i.imgur.com/eB4d6c8.png)
*A high-level overview of the system architecture, showcasing the flow of data from publishers to the monitoring dashboards.*

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/Docker-26.1-2496ED?style=for-the-badge&logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/Paho_MQTT-2.0-006600?style=for-the-badge" alt="Paho-MQTT">
  <img src="https://img.shields.io/badge/Pandera-0.19-003366?style=for-the-badge" alt="Pandera">
  <br>
  <img src="https://img.shields.io/badge/Prometheus-v2.53-E6522C?style=for-the-badge&logo=prometheus" alt="Prometheus">
  <img src="https://img.shields.io/badge/Grafana-11.1-F46800?style=for-the-badge&logo=grafana" alt="Grafana">
  <img src="https://img.shields.io/badge/InfluxDB-2.7-22ADF6?style=for-the-badge&logo=influxdb" alt="InfluxDB">
  <br>
  <img src="https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript" alt="JavaScript">
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5" alt="HTML5">
  <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3" alt="CSS3">
</p>

---

## 📋 Table of Contents

- [About The Project](#about-the-project)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Architecture & Data Flow](#architecture--data-flow)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Running](#installation--running)
  - [Accessing Services](#accessing-services)
- [Usage](#usage)
  - [Admin Panel](#admin-panel)
  - [Web Dashboard](#web-dashboard)
  - [Grafana Dashboard](#grafana-dashboard)
- [Project Structure](#project-structure)
- [License](#license)

---

## 📖 About The Project

In the world of the Internet of Things (IoT), data is king. However, raw data streamed from countless sensors is often noisy, inconsistent, or outright incorrect. This project addresses the critical challenge of ensuring data quality in real-time IoT applications.

It provides a robust, end-to-end solution for:
1.  **Ingesting** raw data from multiple MQTT topics.
2.  **Validating** each message against dynamically configurable rules using Pandera schemas.
3.  **Routing** the data to different topics based on the validation outcome (valid or failed).
4.  **Persisting** every message for historical analysis.
5.  **Monitoring** the entire system's health and performance through a comprehensive observability stack.

The core of the system is its dynamic nature. All configurations—from MQTT broker settings to complex validation schemas and topic mappings—can be managed on-the-fly through a user-friendly web interface without ever needing to restart the core application or touch the code.

---

## ✨ Key Features

- **Dynamic Configuration via Web UI**:
  - Manage MQTT broker settings.
  - Add, update, or delete topic mappings (source, validated, failed).
  - Create, view, edit, and delete Pandera validation schemas directly in the browser.
- **Real-time Validation & Routing**:
  - Uses `Pandera` for powerful and explicit data validation.
  - Messages are validated against their assigned JSON schemas.
  - Automatically republishes messages to `validated` or `failed` topics.
- **Live Data Dashboard**:
  - A vanilla JavaScript single-page application that displays validated and failed messages in real-time.
  - Dynamically subscribes to the correct topics based on the Admin Panel's configuration.
  - Features robust filtering by source topic, status, and error type.
- **Full Observability Stack**:
  - **Prometheus**: Collects key performance indicators (KPIs) like message processing rates and error counts.
  - **Grafana**: Provides a pre-built dashboard to visualize system health, success rates, error distributions, and detailed data from InfluxDB.
  - **InfluxDB**: Persistently stores all validated and failed messages as time-series data for analysis and historical review.
- **Fully Dockerized**:
  - The entire application stack (FastAPI app, Prometheus, InfluxDB, Grafana) is containerized.
  - Runs with a single `docker-compose up` command for easy setup and consistent deployment.

---

## 🛠️ Tech Stack

### Backend
- **Framework**: `FastAPI`
- **MQTT Communication**: `paho-mqtt`
- **Data Validation**: `Pandera`, `pydantic`
- **WebSockets**: `FastAPI WebSockets`
- **Metrics Exposition**: `prometheus-client`
- **Database Client**: `influxdb-client`
- **Server**: `Uvicorn`

### Frontend
- **Core**: `HTML5`, `CSS3`, `Vanilla JavaScript (ES6+)`
- **Real-time MQTT**: `MQTT.js` (via CDN)
- **Icons**: `Phosphor Icons`

### Database & Monitoring
- **Time-Series Database**: `InfluxDB`
- **Metrics Collection**: `Prometheus`
- **Data Visualization**: `Grafana`

### Development & Deployment
- **Containerization**: `Docker` & `Docker Compose`

---

## 🏗️ Architecture & Data Flow

The system operates on two primary flows: a **Data Flow** for processing MQTT messages and a **Control Flow** for managing the system's configuration.

### Data Flow

1.  **Publish**: Simulated sensors (`sensorX_publisher.py`) publish data to specific MQTT topics (e.g., `/sensor1`).
2.  **Ingest & Validate**: The `MQTTClient` within `mqtt_manager.py` subscribes to these source topics. Upon receiving a message, it:
    a. Parses the JSON payload.
    b. Loads the corresponding Pandera schema defined in `config.json`.
    c. Validates the data against the schema.
3.  **Route & Republish**:
    - **On Success**: The original message is republished to a `validated` topic (e.g., `/sensor1/validated`).
    - **On Failure**: A detailed error report is generated and republished to a `failed` topic (e.g., `/sensor1/failed`).
4.  **Store**: The `InfluxDBWriter` in `mqtt_manager.py` asynchronously writes every message (both valid and failed) to the InfluxDB database for persistence.
5.  **Monitor**:
    - The **Web Dashboard** (`app.js`) subscribes to the `validated` and `failed` topics to display results in real-time.
    - **Prometheus** scrapes the `/metrics` endpoint of the FastAPI app to collect statistics on processed messages.
    - **Grafana** queries both Prometheus and InfluxDB to visualize this data on its dashboard.

### Control Flow (Dynamic Configuration)

1.  **User Action**: The user makes a change in the **Admin Panel** (e.g., edits a topic mapping, updates an MQTT setting, or saves a new schema).
2.  **API Request**: The frontend sends an HTTP request (e.g., `POST /api/topic-mappings`) to the FastAPI backend.
3.  **Update Config**: `main.py` handles the request, updates the central `config.json` file on the server's disk.
4.  **Restart MQTT Client**: The application gracefully stops the current `mqtt_manager` thread and immediately restarts it. The new instance reads the updated `config.json` and connects to the broker with the new settings (new topics, new schemas, etc.).
5.  **Broadcast Update**: After restarting, the server broadcasts a `config_updated` message via WebSocket to all connected web dashboard clients.
6.  **Dashboard Re-initialization**: The **Web Dashboard** (`app.js`) receives the WebSocket message and triggers its `initializeApp` function, which fetches the new configuration and gracefully reconnects to the MQTT broker with the updated list of topics.

---

## 🚀 Getting Started

To get a local copy up and running, follow these simple steps.

### Prerequisites

You must have Docker and Docker Compose installed on your machine.
- **Docker**: [Download & Install Docker](https://www.docker.com/products/docker-desktop/)
- **Docker Compose**: It is included with modern versions of Docker Desktop.

### Installation & Running

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/your-username/mqtt-validation-project.git
    ```
2.  **Navigate to the project directory:**
    ```sh
    cd mqtt-validation-project
    ```
3.  **Build and run the services using Docker Compose:**
    ```sh
    docker-compose up --build
    ```
    The `--build` flag ensures that any changes to the application code are rebuilt into the Docker image. The first time you run this, it will take a few minutes to download the necessary base images and install dependencies. Subsequent runs will be much faster.

That's it! The entire system is now running.

### Accessing Services

Once the containers are up, you can access the different parts of the system via your web browser:

- **Web Dashboard**: `http://localhost:8000/dashboard.html`
- **Admin Control Panel**: `http://localhost:8000/admin.html`
- **FastAPI Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Grafana**: `http://localhost:3000`
  - Login with username `admin` and password `admin`.
- **Prometheus**: `http://localhost:9090`
- **InfluxDB**: `http://localhost:8086`

---

## 📖 Usage

After running the system, you can interact with it in several ways.

### Admin Panel
Navigate to the **Admin Panel** to dynamically control the system. Here you can:
-   **Set MQTT Broker details**: Change the broker host and port.
-   **Manage Topic Mappings**: Add new sensor topics, and define where their `validated` and `failed` messages should be routed. You can also assign a specific validation schema to each topic mapping.
-   **Manage Schemas**: Create a new validation schema from scratch, or edit/delete existing ones. The content must be a valid JSON that Pandera can parse.

Any change saved here will automatically and instantly reconfigure the backend MQTT client and update all connected Web Dashboards.

### Web Dashboard
Navigate to the **Web Dashboard** to see the real-time flow of validated and failed messages. Use the sidebar to:
-   Filter messages based on their original source topic.
-   Filter messages by status (`validated` or `failed`).
-   If "failed" is selected, you can further filter by the specific error type (e.g., `out_of_bounds`, `missing_key`).

### Grafana Dashboard
Navigate to **Grafana** to get a high-level overview of the system's health and performance. The pre-built dashboard includes panels for:
-   Success and failure rates over time.
-   Distribution of different error types.
-   Total messages processed.
-   A detailed table of the latest failed messages from InfluxDB.
-   Live power readings for `sensor3`.

---

## 📁 Project Structure

<pre>
mqtt-validation-project/
├── 📂 schemas/              # Contains JSON-based Pandera validation schemas
│   ├── 📜 sensor1.json
│   └── 📜 ...
├── 📂 sensors/              # Python scripts to simulate sensor data publishers
│   ├── 📜 sensor1_publisher.py
│   └── 📜 ...
├── 📂 static/               # Frontend static files
│   ├── 📜 admin.html
│   ├── 📜 admin.css
│   ├── 📜 app.js
│   ├── 📜 dashboard.html
│   └── 📜 style.css
├── 📜 .dockerignore         # Specifies files to ignore in the Docker build context
├── 📜 config.json            # Central configuration for MQTT settings and topic/schema mappings
├── 📜 docker-compose.yml     # Orchestrates all services (app, influx, prometheus, grafana)
├── 📜 Dockerfile             # Defines the build steps for the main FastAPI application
├── 📜 main.py                # FastAPI application entrypoint, handles API requests and WebSockets
├── 📜 mqtt_manager.py        # Core MQTT client logic for subscribing, validating, and republishing
├── 📜 prometheus.yml         # Configuration file for Prometheus scrape targets
├── 📜 README.md              # You are here!
└── 📜 requirements.txt       # Python dependencies for the application
</pre>

---

## 📄 License

This project is distributed under the MIT License. See `LICENSE` for more information. 
