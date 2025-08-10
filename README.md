# OLTP AND OLAP DATA WORKFLOW

This is project is designed to stream workflow data which is sent in Json to FastAPI application. Then the data is published to kafka for further downstream and processing. The data is written to azure as well for OLAP purposes to enable advance analytics.

## The Project Overview

The project contains a complete data pipeline that supports both OLTP (Online Transaction Processing) and OLAP (Online Analytical Processing) Workload. The workflow integrates multiple technologies for real-time data processing, storage, transformation and visualization.

# Stack used in the project

1. Python Client:
   Utilized to post real-time streaming messages to the backend system
2. FastAPI:
   Acts as the API gateway to receive and handle incoming streaming         messages and post it to kafka producer.
3. Apache Kafka:
   Serves as a distributed message broker to buffer and distribute          streaming messages.
4. Apache Spark:
   Processes real-time data from kafka and writes it to both postgreSQL     for transactional storage and Azure Data Lake for analytical (OLAP)   processing.
5. PostgreSQL & pgAdmin:
   PostgreSQL is used for persisten storage of processed streaming data     and pgAdmin provides a user interface for querying and visualizing the data.
6. Streamlit:
   The front -end web app that consume and display the real-time data   from posgreSQL for OLTP use case.

                                     to be continuee for azure under construction


# Managed Identity between Azure data Lake and Synapse to create External table: Need to document this.
# Project Architecture
![Diagram-diagram](https://github.com/user-attachments/assets/861cfeb7-3703-4058-a826-3fefe097fda1)
