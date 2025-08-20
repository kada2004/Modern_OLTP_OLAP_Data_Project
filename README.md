# Project Introduction & Goals

## Introduction
This is project is designed to stream workflow data which is sent in Json to FastAPI application. Then the data is published to kafka for further downstream and processing. The data is written to azure as well for OLAP purposes to enable advance analytics. And the OLAP follow the medaillon architecture principle with BRONZE-SILVER-GOLD layers.

## Project Goals
 Objectives of the project
* Build streaming data pipeline using open-source technologies.
* Learn and understand stream processing.
* Set up and connect different open-source tools to work together(API,Kafka,PostgreSQL)
* Improve understanding of Docker and how to host applications
* Practice and improve data modelling skills and SQL store procedures
* Build an end-to-end pipeline in Azure.
  Transaction Use Case (OLTP)
  

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

## Objectives to achieve with this dataset OLTP & OLAP

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

## API Client 
The API client sends a JSON payload to the API app and displays the response in the terminal.  
On success, it returns a status message such as: `Status code:  201`
<img width="1336" height="321" alt="client_posting_data_api_app_sample" src="https://github.com/user-attachments/assets/db997d70-3dbc-4b36-8f27-23f15ad58f61" />

## Set Up Kafka and Zookeeper
Apache Zookeper acts as the metadata database for kafka, managing brokers, topics, and comsumers. Both Kafka and Zookeeper are defined in single docker Docker Compose file [link_compose](link) Kafka depend on Zookeper to start and both are Network including Spark and PostgreSQL.

    depends_on:
      - zookeeper
    networks:
      - kafka-net
    user: "root"

A Kafka topic is created to receive  data from the API backend through the producer.
The Local Consumer subscribes to and read the messages.
start kafka & Zookeper with command `sudo docker-compose -f docker-compose-kafka.yml build` for building the images or `sudo docker-compose -f docker-compose-kafka.yml up` to start kafka and zookeper. And in the project setup all services are defined in a single Docker Compose file to make sure they are in the same network  to ensure communication between the streaming services.


<img width="996" height="134" alt="starting container" src="https://github.com/user-attachments/assets/0b9a17a1-34a2-43ae-be70-10468ada102f" />
<img width="1355" height="595" alt="Zookeeper" src="https://github.com/user-attachments/assets/b63b653d-88cb-4013-9210-fc2408f2270c" />

## Some Important to command to kafka topics:

<pre> ```
#First to attach the Kafka shell then go to the dictory
cd /opt/bitnami/kafka/bin
#comand to list the existing topic of kafka
./kafka-topics.sh --list --bootstrap-server localhost:9092 

#command to create ingest topic :
./kafka-topics.sh --create --topic ingestion-topic --bootstrap-server localhost:9092
./kafka-console-consumer.sh --topic spark-output --bootstrap-server localhost:9092  #spark spark ouput topic

#command to create a local consummer:
./kafka-console-consumer.sh --topic ingestion-topic --bootstrap-server localhost:9092 ``` </pre>

local consumer:
<img width="1327" height="386" alt="local_consummer_df" src="https://github.com/user-attachments/assets/3d7c47d5-801f-4126-98be-bae8ebc35463" />

## Spark Set up

Spark read the stream the ingest topic from Kafka and Spark is set in the same compose as kafka and zookeeper and all start at the same time the compose up.
Spark read the stream and prepare the structure of json into a dataframe in order to math the Data modele in PostgreSQL and at the same time spark write data to Azure data lake in parquet format. without any tranformation for OLAP just the format which change and the deduplicating and logic to in jupiter notebook the way to insert logic into the database for new and update logic because I need preferent to use Store procedures for streaming and let spark handle the insert logic into the databse. and the connection passords and connection between spark and postgress is kept in the .env commit to gitignore to that it will not be display in the repostory. In connection between Saprk and Azure i'm using access key because the SAS token was not behaving properly with the version of my park.

one issue for hfbsf to write to spark . to be continue and write properly.




