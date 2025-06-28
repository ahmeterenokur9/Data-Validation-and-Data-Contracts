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
