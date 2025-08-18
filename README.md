# OLTP AND OLAP DATA WORKFLOW

This is project is designed to stream workflow data which is sent in Json to FastAPI application. Then the data is published to kafka for further downstream and processing. The data is written to azure as well for OLAP purposes to enable advance analytics. And the OLAP follow the medaillon architecture principle with BRONZE-SILVER-GOLD layers.

## The Project Overview

The project contains a complete data pipeline that supports both OLTP (Online Transaction Processing) and OLAP (Online Analytical Processing) Workload. The workflow integrates multiple technologies for real-time data processing, storage, transformation and visualization.

# Stack used in the project
## Streaming OLTP
1. Python Script that Transfom csv to json format for the APi Client
2. Python Client:
   Utilized to post real-time streaming messages to the backend system
3. FastAPI:
   Acts as the API gateway to receive and handle incoming streaming         messages and post it to kafka producer.
4. Apache Kafka:
   Serves as a distributed message broker to buffer and distribute          streaming messages.
5. Apache Spark:
   Processes real-time data from kafka and writes it to both postgreSQL     for transactional storage and Azure Data Lake for analytical (OLAP)   processing.
6. PostgreSQL & pgAdmin:
   PostgreSQL is used for persisten storage of processed streaming data     and pgAdmin provides a user interface for querying and visualizing the data.
7. Streamlit:
   The front -end web app that consume and display the real-time data   from posgreSQL for OLTP use case.
8. Docker and Docker compose which is hosting FastAPI, Kafka & zookepeer, Apache Spark , PostgreSQL & pgAdmin.

## Azure OLAP 
1. Data Storage - Azure DataLake : Utilized a datastore for Bronze and Silver Layer
2. Synapse Anlytics: Acting both as datastore for Gold Layer and a query engine, PBI reads directly from synapse views
3. Azure Data Factory:  Orchestrate the transformation process,  bronze ---> silver Triggering synapse notebook and silver -----> gold Executing Store procedures and loading the outputs into synapse Tables.
4. Terraform and CI/CD : Creating azure resources and access permission via Terraform and automatic build and deploy of Terraform code.
5. Azure Keyvault and Service principal: Manages and secures secrets, connections strings and credentials used in GITACTION pipeline and ADF, Synapse and AIRFLOW.
6. Apache Airflow : Orchestrated and Schedule ADF pipelines.
7. Docker: Hosting Airflow infrastructure : Airflow webserver, Schedule, DAG processor , Airflow metadata database.
8. Power BI: Dashboards and Reports are powered by Power BI
   



                                     to be continuee for azure under construction


# Managed Identity between Azure data Lake and Synapse to create External table: Need to document this.
# Project Architecture
![Diagram-diagram](https://github.com/user-attachments/assets/861cfeb7-3703-4058-a826-3fefe097fda1)

## Project Setup and Prerequisites
1. Ubuntu or WSL2 installed with al least 16 GB RAM.
2. IDE like VsCode or Pycharm
3. API Testing Software like Postman.
4. Docker and Docker Compose

## The Dataset 
I have used an E-Commerce dataset from kaggle [dataset link](https://www.kaggle.com/datasets/tunguz/online-retail)
which Contains transactional records, customer details, and product information.

## Building API:
1. Created a python [script](code to be added after push to repo) that converts Kaggle E-commerce dataset from csv to Json format.
2. Tested first with Postman and Created API client to POST Json data into the FastAPI app.
3. The Fast API application is build in python [code](to be added later) run inside of the Docker container and exposed on port 80:80 [link to compose and dockerfile](to be added later) 
## PostMan
   <img width="978" height="459" alt="image" src="https://github.com/user-attachments/assets/b02fc3d3-7fb1-4a23-a4ca-61626f71cd91" />
   
## Start the App
 I have used the same docker compose for all my stack like Kafka, PostgreSQL etc so I run this command in directory of the compose file `sudo docker-compose -f docker-compose-kafka.yml buid` for first or `sudo docker-compose -f docker-compose-kafka.yml up` to start the containers

 <img width="804" height="195" alt="image" src="https://github.com/user-attachments/assets/38de7977-c932-4235-9821-85776ace427a" />
<img width="1298" height="537" alt="image" src="https://github.com/user-attachments/assets/c9bb9580-03ba-4da4-8b17-fd7bf3cf76a3" />

DockerFile Code that copy the app code and command to start the App:

 <pre> ``` FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --requirement /tmp/requirements.txt

COPY ./app /app
WORKDIR /app ``` </pre>

## lsklfds

   what whatups 




