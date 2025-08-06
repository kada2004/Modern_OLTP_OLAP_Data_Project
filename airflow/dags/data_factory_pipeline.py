from airflow import DAG
from airflow.providers.microsoft.azure.operators.data_factory import AzureDataFactoryRunPipelineOperator
from airflow.providers.microsoft.azure.sensors.data_factory import AzureDataFactoryPipelineRunStatusSensor
from airflow.operators.email import EmailOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime, timedelta
from azure.identity import DefaultAzureCredential
from azure.mgmt.datafactory import DataFactoryManagementClient
import logging

# Default args
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Function to fetch ADF pipeline run details and log errors
def log_adf_run_details(task_id, run_id, adf_conn_id, **context):
    """
    Fetch ADF pipeline run details and log errors for display in Airflow UI.
    """
    try:
        # Retrieve connection details from Airflow connection
        conn = Variable.get(adf_conn_id, deserialize_json=True)
        subscription_id = conn.get("subscription_id")
        resource_group = conn.get("resource_group")
        factory_name = conn.get("factory_name")

        # Initialize ADF client
        credential = DefaultAzureCredential()
        adf_client = DataFactoryManagementClient(credential, subscription_id)

        # Get pipeline run details
        run_response = adf_client.pipeline_runs.get(
            resource_group, factory_name, run_id
        )

        # Extract status and error details
        status = run_response.status
        error_message = run_response.additional_properties.get("error", None)

        # Log details to Airflow UI
        logging.info(f"ADF Pipeline Run ID: {run_id}")
        logging.info(f"Status: {status}")
        
        if status != "Succeeded" and error_message:
            error_details = error_message.get("message", "No detailed error message available")
            logging.error(f"ADF Pipeline failed with error: {error_details}")
            raise ValueError(f"ADF Pipeline failed: {error_details}")
        else:
            logging.info("ADF Pipeline completed successfully.")

    except Exception as e:
        logging.error(f"Failed to fetch ADF run details: {str(e)}")
        raise

with DAG(
    dag_id='silver_then_gold_pipeline',
    default_args=default_args,
    description='Run Silver ADF pipeline, then Gold ADF pipeline with error logging',
    schedule=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['adf', 'silver', 'gold'],
) as dag:
    adf_conn_id = Variable.get("adf_connection_id", default_var="azure_data_factory_default")

    # 1. Trigger Silver pipeline
    run_silver = AzureDataFactoryRunPipelineOperator(
        task_id="run_silver_pipeline",
        pipeline_name="silver_pipeline",
        azure_data_factory_conn_id=adf_conn_id,
        resource_group_name="data_platform",
        factory_name="adf-data-platform",
        parameters={"date": "{{ dag_run.conf['date'] }}"}, # passing date manually for now
    )

    # 2. Wait for Silver to complete
    wait_silver = AzureDataFactoryPipelineRunStatusSensor(
        task_id="wait_silver_pipeline",
        run_id="{{ task_instance.xcom_pull(task_ids='run_silver_pipeline') }}",
        azure_data_factory_conn_id=adf_conn_id,
        expected_statuses=["Succeeded"],
        resource_group_name="data_platform",
        factory_name="adf-data-platform",
        timeout=3600,
        poke_interval=60,
    )

    # 3. Log Silver pipeline run details
    log_silver_details = PythonOperator(
        task_id="log_silver_run_details",
        python_callable=log_adf_run_details,
        op_kwargs={
            "task_id": "run_silver_pipeline",
            "run_id": "{{ task_instance.xcom_pull(task_ids='run_silver_pipeline') }}",
            "adf_conn_id": adf_conn_id,
        },
    )

    # 4. Trigger Gold pipeline
    run_gold = AzureDataFactoryRunPipelineOperator(
        task_id="run_gold_pipeline",
        pipeline_name="gold_pipeline",
        azure_data_factory_conn_id=adf_conn_id,
        resource_group_name="data_platform",
        factory_name="adf-data-platform",
        parameters={"date": "{{ dag_run.conf['date'] }}"}, # passing date manually for now
    )

    # 5. Wait for Gold to complete
    wait_gold = AzureDataFactoryPipelineRunStatusSensor(
        task_id="wait_gold_pipeline",
        run_id="{{ task_instance.xcom_pull(task_ids='run_gold_pipeline') }}",
        azure_data_factory_conn_id=adf_conn_id,
        expected_statuses=["Succeeded"],
        resource_group_name="data_platform",
        factory_name="adf-data-platform",
        timeout=3600,
        poke_interval=60,
    )

    # 6. Log Gold pipeline run details
    log_gold_details = PythonOperator(
        task_id="log_gold_run_details",
        python_callable=log_adf_run_details,
        op_kwargs={
            "task_id": "run_gold_pipeline",
            "run_id": "{{ task_instance.xcom_pull(task_ids='run_gold_pipeline') }}",
            "adf_conn_id": adf_conn_id,
        },
    )

    # 7. Notify on failure with error details
    notify_failure = EmailOperator(
        task_id="notify_failure",
        to="dataengineerpatform@gmail.com",
        subject="ADF Pipeline Failure",
        html_content=(
            "Pipeline {{ task_instance.xcom_pull(task_ids='run_silver_pipeline') }} or "
            "{{ task_instance.xcom_pull(task_ids='run_gold_pipeline') }} failed. "
            "Check Airflow logs for details."
        ),
        trigger_rule="one_failed",
    )

    # Set dependencies
    run_silver >> wait_silver >> log_silver_details >> run_gold >> wait_gold >> log_gold_details >> notify_failure