from airflow import DAG
from airflow.providers.microsoft.azure.operators.data_factory import AzureDataFactoryRunPipelineOperator
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from datetime import datetime
import logging
import pendulum

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
}

with DAG(
    dag_id='silver_adf_trigger_gold',
    default_args=default_args,
    description='Run silver pipeline',
    schedule_interval='40 07 * * *',  # 07:40 CET
    start_date=pendulum.datetime(2023, 1, 1, tz="Europe/Paris"),
    catchup=False,
    tags=['adf', 'silver', 'gold'],
) as dag:

    test_logging = PythonOperator(
        task_id='test_logging',
        python_callable=lambda: logging.info("Hello from Airflow test task"),
    )

    adf_conn_id = Variable.get("adf_connection_id", default_var="azure_data_factory_default")

    # Silver pipeline → simple date param
    trigger_silver_pipeline = AzureDataFactoryRunPipelineOperator(
        task_id='trigger_silver_pipeline',
        pipeline_name='silver_pipeline',
        azure_data_factory_conn_id=adf_conn_id,
        resource_group_name='data_platform',
        factory_name='adf-data-platform',
        deferrable=False,
        parameters={
            "date": "{{ macros.ds_add(ds, 1) }}"   # ds = YYYY-MM-DD (execution date) Macro from doc https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html#macros
        },
    )

    # Gold pipeline → split into Year/Month/Day from execution_date
    trigger_gold_pipeline = AzureDataFactoryRunPipelineOperator(
        task_id='trigger_gold_pipeline',
        pipeline_name='gold_store_procedures_pipeline',
        azure_data_factory_conn_id=adf_conn_id,
        resource_group_name='data_platform',
        factory_name='adf-data-platform',
        deferrable=False,
        parameters={
            "Year": "{{ macros.ds_format(macros.ds_add(ds, 1), '%Y-%m-%d', '%Y') }}",
            "Month": "{{ macros.ds_format(macros.ds_add(ds, 1), '%Y-%m-%d', '%m') }}",
            "Day": "{{ macros.ds_format(macros.ds_add(ds, 1), '%Y-%m-%d', '%d') }}"
        },
    )

    test_logging >> trigger_silver_pipeline >> trigger_gold_pipeline
