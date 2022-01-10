import os
import yaml
import json
import glob


from airflow import DAG
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.hooks.base_hook import BaseHook

AWS_CREDENTIALS = json.loads(BaseHook.get_connection("aws_default").get_extra())
JOB_IMAGE_NAME = "localhost:5000/tasks:latest"


def create_dag(dag_config):
    default_args = {
        "owner": dag_config.get("owner_name"),
        "depends_on_past": dag_config.get("depends_on_path"),
        "start_date": datetime.now(),
        "email": dag_config.get("owner_email"),
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    }

    dag = DAG(
        dag_id=dag_config.get("dag_name"),
        default_args=default_args,
        schedule_interval=dag_config.get("schedule_interval"),
        is_paused_upon_creation=dag_config.get("is_paused_upon_creation"),
    )

    with dag:
        start_task = DummyOperator(task_id="start_pipeline", dag=dag)
        done_task = DummyOperator(task_id="done_pipeline", dag=dag)

        for file_tasks in dag_config.get("files"):

            download_file_task = KubernetesPodOperator(
                namespace="airflow",
                image=JOB_IMAGE_NAME,
                image_pull_policy="Always",
                cmds=["python3", "./jobs/download_file.py"],
                arguments=[
                    "--file-uri",
                    file_tasks.get("file_uri"),
                    "--output-path",
                    file_tasks.get("s3_output_path"),
                    "--file-name",
                    file_tasks.get("file_name"),
                ],
                env_vars={
                    "AWS_ACCESS_KEY_ID": AWS_CREDENTIALS.get("aws_access_key_id"),
                    "AWS_SECRET_ACCESS_KEY": AWS_CREDENTIALS.get(
                        "aws_secret_access_key"
                    ),
                    "AWS_DEFAULT_REGION": "us-east-1",
                },
                name="download-file",
                task_id="download-file",
                get_logs=True,
            )

            print_file_content_task = KubernetesPodOperator(
                namespace="airflow",
                image=JOB_IMAGE_NAME,
                image_pull_policy="Always",
                cmds=["python3", "./jobs/log_records.py"],
                arguments=[
                    "--file-path",
                    f"{file_tasks.get('s3_output_path')}/{file_tasks.get('file_name')}",
                    "--compression",
                    file_tasks.get("compression_type"),
                ],
                env_vars={
                    "AWS_ACCESS_KEY_ID": AWS_CREDENTIALS.get("aws_access_key_id"),
                    "AWS_SECRET_ACCESS_KEY": AWS_CREDENTIALS.get(
                        "aws_secret_access_key"
                    ),
                    "AWS_DEFAULT_REGION": "us-east-1",
                },
                name="log-records",
                task_id="log-records",
                get_logs=True,
            )

            start_task.set_downstream(download_file_task)
            download_file_task.set_downstream(print_file_content_task)
            print_file_content_task.set_downstream(done_task)

    return dag


def read_yaml(filename_path: str):
    with open(filename_path) as _file:
        pipeline_config = yaml.load(_file, Loader=yaml.FullLoader)
    return pipeline_config


config_files = list(
    glob.iglob(
        os.path.dirname(os.path.abspath(__file__)) + "/configs/*.yml", recursive=True
    )
)

for config_path in config_files:
    config = read_yaml(config_path)
    dag_id = config.get("dag_name")
    globals()[dag_id] = create_dag(config)
