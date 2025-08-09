# Dynamic MQTT Data Validation and Monitoring System

A real-time data validation pipeline for MQTT streams, featuring a dynamic web-based control panel and a complete observability stack. This project is designed to ingest sensor data, validate it against user-defined schemas, and provide live monitoring and persistent storage, all managed through a user-friendly interface.

<br>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#about-the-project">About The Project</a></li>
    <li><a href="#key-features">Key Features</a></li>
    <li><a href="#tech-stack">Tech Stack</a></li>
    <li><a href="#architecture--data-flow">Architecture & Data Flow</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

<br>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![InfluxDB](https://img.shields.io/badge/InfluxDB-22ADF6?style=for-the-badge&logo=influxdb&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)

<br>

### Project Architecture

*A high-level diagram illustrating the data flow from sensors to the final dashboards. This visual provides a quick overview of how all components interact.*

![Project Architecture Diagram](./docs/architecture.png)

*(Note: You can create this diagram using a tool like diagrams.net (draw.io) or Excalidraw and place the image file in a `docs` folder at the root of the project.)*

---

## About The Project

In the world of the Internet of Things (IoT), data quality is paramount. Sensor networks can produce vast amounts of data, but this data is often prone to errors, inconsistencies, or malformations. Processing this unreliable data can lead to incorrect analytics, system failures, and poor decision-making.

This project addresses this challenge by providing a robust, end-to-end solution for validating and monitoring MQTT data streams in real-time. It acts as a central gatekeeper that intercepts data from various topics, validates it against dynamically configurable rules, and then re-publishes it to designated "validated" or "failed" topics. This clean separation ensures that downstream applications only receive high-quality, reliable data.

The entire system is managed through a powerful web-based Admin Panel, allowing users to add, remove, or modify topic mappings and validation schemas on the fly, without ever needing to restart the core service manually. Coupled with a full observability stack using Prometheus, Grafana, and InfluxDB, the project offers deep insights into system performance, error rates, and the data itself.

---

## Key Features

- **Dynamic Configuration:**
  - 🚀 **On-the-fly Updates:** Manage MQTT broker settings and topic-to-schema mappings directly from a web UI.
  - 🔄 **Live Reloading:** The core MQTT client automatically restarts and applies new configurations without any downtime for other services.

- **Real-time Validation:**
  - ✅ **Schema-Powered:** Utilizes Pandera for powerful and expressive data validation based on JSON schemas.
  - 📂 **Flexible Schema Management:** Create, read, update, and delete validation schemas directly from the Admin Panel.

- **Live Monitoring & Visualization:**
  - 📊 **Web Dashboard:** A real-time, filterable log of all validated and failed messages, built with Vanilla JS and MQTT.js.
  - 📈 **Grafana Dashboards:** A comprehensive observability dashboard showing success rates, error distributions, and detailed data from InfluxDB.

- **Containerized & Scalable:**
  - 🐳 **Dockerized Environment:** The entire application stack (FastAPI, InfluxDB, Prometheus, Grafana) is managed via `docker-compose` for easy setup and deployment.
  - 📦 **Isolated Services:** Each component runs in its own container, ensuring stability and simplifying dependency management.

- **Persistent Data Storage:**
  - 💾 **Time-Series Database:** All processed messages (both valid and failed) are stored in InfluxDB, a database optimized for time-stamped data, enabling historical analysis.

---

## Tech Stack

This project is built with a modern stack of technologies, chosen for performance, scalability, and ease of use.

- **Backend:**
  - ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi&logoColor=white) - A modern, fast (high-performance) web framework for building APIs with Python.
  - ![Paho-MQTT](https://img.shields.io/badge/Paho_MQTT-538438?style=for-the-badge) - The official Eclipse MQTT client library for Python.
  - ![Pandera](https://img.shields.io/badge/Pandera-FF8C00?style=for-the-badge) - A data validation library for validating pandas DataFrames, used here to check data against schemas.
  - ![Prometheus Client](https://img.shields.io/badge/Prometheus_Client-E6522C?style=for-the-badge&logo=prometheus&logoColor=white) - The official Python client for exposing Prometheus metrics.
  - ![InfluxDB Client](https://img.shields.io/badge/InfluxDB_Client-22ADF6?style=for-the-badge&logo=influxdb&logoColor=white) - The official Python client for writing data to InfluxDB.

- **Frontend:**
  - ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) (ES6+) - Used for all client-side logic in the Admin Panel and Web Dashboard.
  - ![MQTT.js](https://img.shields.io/badge/MQTT.js-8A2BE2?style=for-the-badge) - An MQTT client for Node.js and the browser.
  - ![Phosphor Icons](https://img.shields.io/badge/Phosphor_Icons-5F9EA0?style=for-the-badge) - A flexible icon family used for modern UI elements.
  - ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) & ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) - For structuring and styling the web interfaces.

- **Database & Monitoring:**
  - ![InfluxDB](https://img.shields.io/badge/InfluxDB-22ADF6?style=for-the-badge&logo=influxdb&logoColor=white) - A high-performance time-series database for storing all MQTT messages.
  - ![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white) - A monitoring system and time-series database for collecting application metrics (e.g., message counts, error rates).
  - ![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white) - An open-source platform for monitoring and observability, used to visualize data from both Prometheus and InfluxDB.

- **Containerization:**
  - ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white) & ![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white) - For creating a reproducible, isolated, and easy-to-manage development and deployment environment.

---

## Architecture & Data Flow

The system is composed of several independent services that communicate via MQTT and HTTP requests. There are two primary workflows: the **Data Flow** and the **Control Flow**.

### Data Flow (Real-time Message Processing)
1.  **Publish:** External sensor simulators (`sensorX_publisher.py`) publish raw JSON data to specific source topics (e.g., `/sensor1`) on an MQTT broker.
2.  **Ingest:** The core FastAPI application runs a background `MQTTClient` (`mqtt_manager.py`) which is subscribed to these source topics.
3.  **Validate:** Upon receiving a message, the `MQTTClient` dynamically loads the corresponding JSON validation schema (defined in `config.json`). It uses Pandera to validate the data.
4.  **Republish:**
    - If validation is **successful**, the original message is republished to a "validated" topic (e.g., `/sensor1/validated`).
    - If validation **fails**, a detailed error report is generated and republished to a "failed" topic (e.g., `/sensor1/failed`).
5.  **Store & Monitor:**
    - The `MQTTClient` writes every processed message (both valid and failed) to the **InfluxDB** database for persistent storage.
    - It also increments **Prometheus** counters, labeling them with status (`validated`/`failed`), sensor ID, and error type.
6.  **Visualize:**
    - The **Web Dashboard** (`dashboard.html`) connects directly to the broker, subscribing to the "validated" and "failed" topics to display a live feed of messages.
    - **Grafana** connects to both Prometheus and InfluxDB to display long-term metrics and historical data on its own dashboard.

### Control Flow (Dynamic Configuration)
1.  **User Action:** A user interacts with the **Admin Panel** (`admin.html`) to change a setting (e.g., update a topic mapping, edit a schema).
2.  **API Request:** The Admin Panel's JavaScript sends an HTTP request (e.g., `POST`, `PUT`) to the **FastAPI backend**.
3.  **Update Config:** FastAPI handles the request, updates the central `config.json` file, and modifies schema files on the server's file system.
4.  **Restart Client:** After a configuration change, FastAPI triggers a graceful restart of the background `MQTTClient`, which re-initializes with the new settings.
5.  **Broadcast Update:** FastAPI uses a **WebSocket** connection to broadcast a `"config_updated"` message to all connected Web Dashboard clients.
6.  **Dashboard Refresh:** The Web Dashboard receives the WebSocket message and automatically re-initializes its own MQTT connection, subscribing to the new set of topics defined in the updated configuration. This ensures the dashboard always reflects the current system state without requiring a manual page refresh.

---

## Getting Started

Follow these steps to get the entire application stack running on your local machine.

### Prerequisites

- **Docker:** You must have Docker installed on your system. You can download it from the official [Docker website](https://www.docker.com/products/docker-desktop/).
- **Docker Compose:** Docker Compose is included with modern versions of Docker Desktop. If you have an older version, you may need to install it separately.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repository-name.git
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd your-repository-name
    ```
3.  **Run the application:**
    Use Docker Compose to build the images and start all the services in detached mode (`-d`).
    ```bash
    docker-compose up --build -d
    ```
    The initial build may take a few minutes as it downloads all the necessary base images and installs Python dependencies. Subsequent starts will be much faster.

4.  **Verify that all services are running:**
    ```bash
    docker-compose ps
    ```
    You should see `fastapi_app`, `influxdb`, `prometheus`, and `grafana` listed with a status of `running` or `up`.

---

## Usage

Once all services are running, you can access the different parts of the system through your web browser:

-   **Main Application & Web Dashboard:**
    -   **URL:** `http://localhost:8000`
    -   This is the live dashboard where you can see validated and failed messages in real-time.

-   **Admin Panel:**
    -   **URL:** `http://localhost:8000/admin`
    -   Use this interface to manage MQTT settings, topic mappings, and validation schemas.

-   **Grafana (Monitoring Dashboard):**
    -   **URL:** `http://localhost:3000`
    -   **Login:** `admin` / `admin` (you will be prompted to change the password on first login).
    -   Here you can view the pre-built dashboard that visualizes data from Prometheus and InfluxDB.

-   **Prometheus:**
    -   **URL:** `http://localhost:9090`
    -   You can use the Prometheus UI to explore collected metrics and check target status (`Status` -> `Targets`).

-   **InfluxDB:**
    -   **URL:** `http://localhost:8086`
    -   You can use the InfluxDB UI to explore the raw data stored in the `mqtt_data` bucket. The credentials are set in the `docker-compose.yml` file.
        - **Username:** `my-user`
        - **Password:** `my-password`
        - **Organization:** `my-org`
        - **Bucket:** `mqtt_data`

### Running the Sensor Publishers
To generate data, you need to run the sensor publisher scripts. Since the application is running inside Docker, the publishers need to be run on your **host machine** (your own computer) so they can send data to the public MQTT broker, which the Docker container can then access.

Open three separate terminals on your host machine and run the following commands, one in each terminal:

```bash
# Terminal 1
python sensors/sensor1_publisher.py
```

```bash
# Terminal 2
python sensors/sensor2_publisher.py
```

```bash
# Terminal 3
python sensors/sensor3_publisher.py
```

---

## Project Structure

A high-level overview of the most important files and directories in the project.

```
.
├── docs/
│   └── architecture.png        # Placeholder for the architecture diagram
├── schemas/
│   ├── sensor1.json            # JSON validation schema for sensor 1
│   └── ...                     # Other schemas
├── sensors/
│   ├── sensor1_publisher.py    # Simulates data publishing for sensor 1
│   └── ...                     # Other publishers
├── static/
│   ├── admin.html              # The web UI for the Admin Panel
│   ├── dashboard.html          # The main Web Dashboard UI
│   └── ...                     # Associated CSS and JS files
├── .dockerignore               # Specifies files to ignore in the Docker build
├── config.json                 # Central configuration for MQTT and schemas
├── docker-compose.yml          # Defines and configures all services (FastAPI, Grafana, etc.)
├── Dockerfile                  # Instructions to build the main FastAPI application image
├── main.py                     # The FastAPI application entry point (serves UI, APIs)
├── mqtt_manager.py             # Handles all core MQTT logic (subscribing, validating, republishing)
├── prometheus.yml              # Configuration file for Prometheus scrape targets
├── README.md                   # This file!
├── requirements.txt            # Python dependencies for the project
└── utils.py                    # Utility functions, e.g., for parsing errors
```

---

## License

Distributed under the MIT License. See `LICENSE` for more information.

*(Note: For this to be complete, you should add a `LICENSE` file to your project root containing the MIT License text.)* 
