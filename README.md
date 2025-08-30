# Project Introduction & Goals

## Introduction
This is project is designed to stream workflow data which is sent in Json to FastAPI application. Then the data is published to kafka for further downstream and processing. The data is written to azure as well for OLAP purposes to enable advance analytics. And the OLAP follow the medaillon architecture principle with BRONZE-SILVER-GOLD layers.

## Project Goals

  Transaction Use Case (OLTP)
  * Store all Transaction  happening on the E-commerce platform (Items description,Amount,quantity) make the user to have access to each transaction
    * User to view their total spend up to date
    * View Order history by showing all invoices 
    * View all returned items

  Analytics Use Case (OLAP)
  * Business Intelligence for the analysts to view aggregate sales over time and analyse the Trends
    * Total Sales
    * Sales  Over time
    * Top 10 Products by sales
    * Customer summary : Toal, loyal customers
    * Cancelled Orders or Return
  

## The Project Overview

The project contains a complete data pipeline that supports both OLTP (Online Transaction Processing) and OLAP (Online Analytical Processing) Workload. The workflow integrates multiple technologies for real-time data processing, storage, transformation and visualization.

# Project Architecture
![Diagram-diagram](https://github.com/user-attachments/assets/861cfeb7-3703-4058-a826-3fefe097fda1)

## Stack used in the project
## Streaming OLTP
1. Python Script that Transfom csv to json format for the API Client
2. Python Client:
   Utilized to post real-time streaming messages to the backend system
3. FastAPI:
   Acts as the API gateway to receive and handle incoming streaming         messages and post it to kafka producer.
4. Apache Kafka:
   Serves as a distributed message broker to buffer and distribute          streaming messages.
5. Apache Spark:
   Processes real-time data from kafka and writes it to both postgreSQL     for transactional storage and Azure Data Lake for analytical (OLAP)   processing.
6. PostgreSQL & pgAdmin:
   PostgreSQL is used for persistent storage of processed streaming data     and pgAdmin provides a user interface for querying and visualizing the data.
7. Streamlit:
   The front -end web app that consume and display the real-time data   from posgreSQL for OLTP use case.
8. Docker and Docker compose which is hosting FastAPI, Kafka & zookepeer, Apache Spark , PostgreSQL & pgAdmin.

## Azure OLAP 
1. Data Storage - Azure DataLake : Utilized a datastore for Bronze and Silver Layer
2. Synapse Anlytics: Acting both as datastore for Gold Layer and a query engine, PBI reads directly from synapse views
3. Azure Data Factory:  Orchestrate the transformation process,  bronze ---> silver Triggering synapse notebook and silver -----> gold Executing Store procedures and loading the outputs into synapse Tables.
4. Terraform and CI/CD : Creating azure resources and access permission via Terraform and automatic build and deploy of Terraform code.
5. Azure Keyvault and Service principal: Manages and secures secrets, connections strings and credentials used in GITACTION pipeline and ADF, Synapse and Airflow.
6. Apache Airflow : Orchestrated and Schedule ADF pipelines.
7. Docker: Hosting Airflow infrastructure : Airflow webserver, Schedule, DAG processor , Airflow metadata database.
8. Power BI: Dashboard and Report are powered by Power BI

## Project Setup and Prerequisites
1. Ubuntu or WSL2 installed with al least 16 GB RAM.
2. IDE like VsCode or Pycharm
3. API Testing Software like Postman.
4. Docker and Docker Compose

## The Dataset 
I have used an E-Commerce dataset from kaggle [dataset link](https://www.kaggle.com/datasets/tunguz/online-retail)
which Contains transactional records, customer details, and product information. However added an extra column, `CustomerName` to meet the objective.

Overview of dataset Columns (Kaggle)

<img width="1181" height="770" alt="image" src="https://github.com/user-attachments/assets/c0706a81-4e5f-4e58-88d6-24d29eac7fee" />


## Building API:
1. Created a python script that converts Kaggle E-commerce dataset from csv to Json format [code](https://github.com/kada2004/Modern_OLTP_OLAP_Data_Project/blob/master/local/transform_csv_to_json.py).
2. Tested first with PostMan and Created API client to POST Json data into the FastAPI app.
3. The Fast API application is build in python [code](https://github.com/kada2004/Modern_OLTP_OLAP_Data_Project/blob/master/fastAPI/app/main.py) run inside of the Docker container and exposed on port 80:80 [link to compose and dockerfile](https://github.com/kada2004/Modern_OLTP_OLAP_Data_Project/blob/master/docker/docker-compose-kafka.yml)
## PostMan
   <img width="978" height="459" alt="image" src="https://github.com/user-attachments/assets/b02fc3d3-7fb1-4a23-a4ca-61626f71cd91" />
   
## Start the App
 I have used the same docker compose for all my stack like Kafka, PostgreSQL etc so I run this command in directory of the compose file `sudo docker-compose -f docker-compose-kafka.yml build` first time to build the image or `sudo docker-compose -f docker-compose-kafka.yml up` to start the containers

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
Api app receiving the json documents
<img width="1328" height="540" alt="fastapi_app_view" src="https://github.com/user-attachments/assets/d108d39b-3b55-4708-b411-75c10e66ea56" />

## Set Up Kafka and Zookeeper
Apache Zookeper acts as the metadata database for kafka, managing brokers, topics, and comsumers. Both Kafka and Zookeeper are defined in single docker Docker Compose file [link_compose](https://github.com/kada2004/Modern_OLTP_OLAP_Data_Project/blob/master/docker/docker-compose-kafka.yml) Kafka depend on Zookeper to start and both are the same network including Spark and PostgreSQL.

New version of Kafka does no longer requires Zookeeper.
reference confluent: [link to documentation](https://developer.confluent.io/learn/kraft/)


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


## Command to Create kafka topics from console:
 A Kafka topics are the categories used to organize messages. Each topic has a name that is unique across the entire Kafka cluster.
 Messages are sent to and read from specific topics.  In other words, producers write data to topics, and consumers read data from topics.
 
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

Spark reads the stream from Kafka ingest topic. Spark reads the Json stream and converts it to into a DataFrame that matches the data model in PostgreSQL.
At the same time, spark also writes the data to Azure  Data Lake in Parquet format. Spark also managed the logic of insertion or update into PostgresSQL.
Connection details (like passwords) are store in the `.env` files, which is listed in `.gitignore` so that the credentials are not shown in the repository.


Spark Jupiter Notebook is exposed on Port 8080 and Spark UI is available on Port 4040

Spark UI

<img width="1848" height="932" alt="spark_ui1" src="https://github.com/user-attachments/assets/284f167c-f7bc-418a-8bb8-1b7f4727169b" />

<img width="1848" height="450" alt="spark_ui" src="https://github.com/user-attachments/assets/1654c9a6-7a0e-4a83-8c6a-f78f68e30e7a" />


For connection between Spark and Azure, an access key is used instead of SAS token because SAS token was not working well was not handling the rename of folder in Azure even with all privileges.
Spark also managed the configuration and libraries which are required to write data to PostgreSQL.

# Challenge
  I faced a major challenge to connect spark and Azure Data Lake. The Spark docker image (spark 2) was unable to authenticate to Azure because spark 2 don't  have all the required  hadoop libraries to write to Azure.
  error message <pre> ```Writing batch 0 to Azure Blob Failed to write batch 0 to Azure Blob: An error occurred while calling o361.parquet. : org.apache.spark.SparkException: Job aborted.  at org.apache.spark.sql.execution.datasources.FileFormatWriter$.write(FileFormatWriter.scala:198)  at org.apache.spark.sql.execution.datasources.InsertIntoHadoopFsRelationCommand.run(InsertIntoHadoopFsRelationCommand.scala:159)  at org.apache.spark.sql.execution.command.DataWritingCommandExec.sideEffectResult$lzycompute(commands.scala:104)  at org.apache.spark.sql.execution.command.DataWritingCommandExec.sideEffectResult(commands.scala:102)  at org.apache.spark.sql.execution.command.DataWritingCommandExec.doExecute(commands.scala:122)``` </pre>
   Solution:
   To solve this, I upgraded spark image from version 2 to version 3. This allowed me to use the use abfss:// scheme instead of old wasb:// scheme, which is better supported in Spark 3. After the upgrade Spark is writting to Azure Data Lake without any problem.
   * Wasb://  stand for Windows Azure Storage Blob a legacy Hadoop File System to interact with Azure Blob Storage and no support for hierarchical namespaces 
   * abfss:// Stand Azure Blob File System Secure a Modern scheme to  interact with Azure Blob Storage and more secure, supports hierarchical namespaces, and works properly with Spark 3 and Hadoop-compatible tools
   

 # PostreSQL set up
 PostgreSQL is hosted in Docker and is on the same network as rest of the service. pgAdmin also is configured in Docker to connect to PosgreSQL and visualize the data. The connection and passwords of pgAdmin and postgreSQL are stored in the `.env` file.             PostgreSQL is exposed on port 5432 and pgAdmin is exposed on port 8080 
In order to meet the objective processing the streaming dataset for OLTP  . I need to do data modelling. Below is the ERD diagram of postgreSQL

 ERD Diagram for PostgreSQL.
 
<img width="1596" height="994" alt="image (3)" src="https://github.com/user-attachments/assets/4f3e5102-013f-44db-964a-330b64c1cfc5" />

pgAdmin UI connect to PostgreSQL
<img width="1844" height="939" alt="image" src="https://github.com/user-attachments/assets/61f2054e-f8be-4868-a953-bbaf674dfec0" />

[link PostgreSQL Tables Code](https://github.com/kada2004/Modern_OLTP_OLAP_Data_Project/blob/master/postgrsql/spark_db_schema.py)


# Streamlit Dahsboard App set up
Streamlit an open-source python Library that helps you to build customs application to share data and machine kearning web app.

In my setup, Streamlit connect directly to PostgreSQL database using psycopg2 Library. it runs SQL queries and shows the results as a dashboard in Streamlit app.

Command to start the app `streamlit run app.py`
[Link to code](https://github.com/kada2004/Modern_OLTP_OLAP_Data_Project/blob/master/Streamlitapp/app.py)

Streamlit DashBoard

<img width="1846" height="939" alt="image" src="https://github.com/user-attachments/assets/e6234c3a-2bde-4427-b7b9-b4805927e308" />

# e.g Customer with Cancelled InvoiceNo

<img width="1845" height="936" alt="image" src="https://github.com/user-attachments/assets/868b6866-a827-4f11-8a5d-b0aa6df6d042" />




# Azure OLAP Configuration
# Project Architecture
![Diagram-diagram](https://github.com/user-attachments/assets/861cfeb7-3703-4058-a826-3fefe097fda1)
# Infrastructure as code : Terraform
The entire infrastructure in Azure has been provisioned using Terraform, following best practices. Terraform State is stored in a remote backend in azure blob storage. This approach offers several benefits:
* State Locking to prevent concurrent modifications
* Improved security by avoiding having state locally.
* Centralized State file, providing a single source of truth for the current state infrastructure state
* Better Collaboration accross teams by allowing shared access to the state backend.
  
snippet code :
<pre> ```
terraform {
  backend "azurerm" {
    resource_group_name  = "data_platform"
    storage_account_name = "datastorage7i4ws2"
    container_name       = "terraform-state"
    key                  = "terraform.tfstate"
  }
} ``` </pre>

Migrate state to remote backend :

<img width="1080" height="482" alt="migrate_the_remote_backend_to_blob" src="https://github.com/user-attachments/assets/872061e4-a096-4095-831b-7ebb33ea8eb2" />

And Storage account access key store in KeyVault for better security

<img width="2548" height="257" alt="image" src="https://github.com/user-attachments/assets/52cd6aa1-2e68-4976-9e03-7e2e4da70912" />

# Terraform CI/CD Set up

I have built a CI/CD pipeline to automate the infrastructure provision with Terraform:
 * Authentication: via service principal (Contributor role), credentialas store in GitHub Secrets.
 * Workflow: defined in `.github/workflows/ci_cd.yaml`. [code](https://github.com/kada2004/Modern_OLTP_OLAP_Data_Project/blob/master/.github/workflows/ci_cd.yaml).
   * Build job: Azure login --> Terraform init/validate --> save plan as artifaact.
   * Deploy job: Azure login --> download plan --> Terraform init/apply.

 * Currently using `terraform apply -auto-approve` however in a team settings, a manual approval before apply is recommended.

   Terraform Service Principal
   
   <img width="2546" height="1000" alt="image" src="https://github.com/user-attachments/assets/0755b2d3-dd80-4b34-802f-0326e3b157ac" />

   GitHub Secrets
   
   <img width="1423" height="951" alt="image" src="https://github.com/user-attachments/assets/922a83f0-8c69-452d-a7c5-74b912d61908" />

   GitHub CI/CD Workflow 
   
   <img width="2542" height="860" alt="image" src="https://github.com/user-attachments/assets/44e846a5-29b2-4d8d-8ccb-21dadc7b7123" />
   
   Build Task in CI/CD
   
   <img width="852" height="797" alt="image" src="https://github.com/user-attachments/assets/8da33a27-c84a-43a9-8a4f-5c31571171b0" />

   Deploy Task in CI/CD
   
   <img width="790" height="750" alt="image" src="https://github.com/user-attachments/assets/84604555-7cbf-4afc-b4d7-3f5ee855e362" />

   Terraform Plan Output in GitHub Action

   
   <img width="748" height="1142" alt="image" src="https://github.com/user-attachments/assets/05ecef73-4c15-440b-babe-e6811f434ef1" />

   Terraform Apply Output in GitHub Action

   <img width="496" height="1008" alt="image" src="https://github.com/user-attachments/assets/47c67dd0-8f8c-4e7b-bb97-d3448f2aa707" />

   Azure infrastructure created via Terraform

   <img width="1732" height="755" alt="image" src="https://github.com/user-attachments/assets/5cfd6d75-0caf-4b20-8acc-f65a46937fe5" />

   ## Datastore (Medallion Architecture)
    The datastore is organized using the Medallion Architecture pattern with 3 Layers
   * Bronze Layer
     Store in Azure Data Lake Gen2, holds raw data in parquet format.
   * Silver Layer
     Also store in Azure Data Lake Gen2
     Data is transformed and split into structures tables
     
     - Dim_Customer
     - Dim_Date
     - Dim_Invoice
     - Dim_Product
     - Fact_Sales

 Datastore portal
 <img width="1927" height="1078" alt="image" src="https://github.com/user-attachments/assets/c12b013f-fbfd-4541-9641-f7e10eb23f23" />
 
 Silver Layer Tables
 
 <img width="558" height="405" alt="image" src="https://github.com/user-attachments/assets/c9cb3990-3caf-43b1-bfda-7e1242513adf" />


* Gold Layer
  Store in Azure Synapse Analytics.
  
  Serves as query engine for Power BI
  
  Data from Silver is loaded via SQL stored procedures.

  ERD GOLD
  
  <img width="1168" height="808" alt="image (5)" src="https://github.com/user-attachments/assets/c36fd257-72d9-478f-862d-f186f146696e" />


## Data Transformation
The data transformation follow the Medaillion Architecture flow:

* Bronze → Silver
  Transformations are performed using Synapse Spark Serveless Pool.
  Raw Parquet data from Bronze layer is cleaned, deduplicated and split into structured tables (`dim_customer,dim_date,dim_invoice,dim_product,fact_sales`)
  The processed outputs are stored in silver layer (ADLS Gen2).

* Silver → Gold
  Data is accessed through external tables  on the fly from stored procedures
  Transformations are handle via SQL stored procedures using upsert/merge logic
  Outputs are loaded into Synapse Tables

  Analytics pools

  <img width="1792" height="286" alt="image" src="https://github.com/user-attachments/assets/bd2d6ebb-66eb-466b-97be-71fd3bbde87c" />

Synapse connect to Azure Data Lake Gen2 via Managed Identity

## Orchestration

The orchestration of data pipelins is managed using Azure Data Factory (ADF) and Apache Airflow.

* Azure Data Factory
  * Orchestrates transformation from Bronze → Silver by executing Synapse Spark notebooks with conditional activities.
  * Manges Silver → Gold by running stored procedures in the correct sequence inside Synapse Dedicated SQL Pool

* Apache Airflow
  * Handles scheduling and triggering of ADF pipelins using Data Factory operator withing the DAG
  * Airflow run inside Docker
  * The run is scheduled to run every day at 07:40
  * Connects to Azure via Service Principal:
    * The service principal is granted the ADF Contributor role.
    * The secrets are securely stored in Keyvault and use Airflow Variable to retrieve the secrets and authenticate to Azure

This hybrid approach leverages ADF for data movement and transformation orchestration, while Airflow provide robust workflow scheduling and control.

ADF UI Silver pipeline

<img width="1810" height="991" alt="image" src="https://github.com/user-attachments/assets/03c0dabe-80f3-457a-a03d-cbedcd78da91" />

ADF UI Gold pipeline

<img width="1995" height="993" alt="image" src="https://github.com/user-attachments/assets/f47419cf-9e2c-401d-be85-202f641d8b69" />

Run from monitor trigger by Airflow

<img width="2140" height="442" alt="image" src="https://github.com/user-attachments/assets/a7f481ba-be7a-4bff-a179-c29ec9cc3cab" />
Airflow UI Run

<img width="1849" height="938" alt="airflow_dag_ui" src="https://github.com/user-attachments/assets/9a02d356-9a26-43f0-8e19-8e74770913e9" />
Run Logs

<img width="1490" height="475" alt="airflow_logs_anotherONE" src="https://github.com/user-attachments/assets/83c9c788-9c10-4773-94c7-b14d9b740c1d" />

VsCode Logs

<img width="1324" height="602" alt="dag_trigger_logs_from_vscode" src="https://github.com/user-attachments/assets/c1d3b1e8-55bb-4985-9680-7289accd124c" />

## Power BY 

Power BY is connected directly to Azure Synapse (Gold Layer) direct query to enable reporting for the analyst.
I have built a Sales Dashboard that supports The objectives defined for this dataset with insights such as:

* Total Sales
* Sales Over Time
* Cancelled Orders
* Top 10 Products by sales
* Top loyal customers

Power By Dashboard 

<img width="1421" height="746" alt="image" src="https://github.com/user-attachments/assets/38a736ee-a267-49dd-8829-31b0449d81fd" />


## Conclusion

This project was a great way for me to show my skillsset in an industry relevant context. build solution that meet user needs and project goals

I used FastAPI, Kafka, Zookeeper, Apache Spark, Apache Airflow, and PostreSQL, all running  in Docker containers, and along with  Azure stack for OLAP.
Some of the challenges were setting up Zookeeper and Kafka and getting Spark to write to Azure Data Lake.

Going forward, I plan to:
* To explore how to run kafka without Zookeeper
* Follow best practices for managing Docker Images using container registries



 



    


   




   

   

   










 

 

  





