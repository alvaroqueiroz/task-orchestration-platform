import json
from airflow import DAG
from kubernetes.client import models as k8s
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.hooks.base_hook import BaseHook


AWS_CREDENTIALS = json.loads(BaseHook.get_connection('aws_default').get_extra())


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime.utcnow(),
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag = DAG(
    "kubernetes_sample",
    default_args=default_args,
    schedule_interval=timedelta(minutes=10),
)


start_task = DummyOperator(task_id="start_pipeline", dag=dag)
done_task = DummyOperator(task_id="done_pipeline", dag=dag)

download_file_task = KubernetesPodOperator(
    namespace="airflow",
    image="localhost:5000/task-scripts",
    image_pull_policy='Always',
    cmds=["python3", "./scripts/download_file.py"],
    arguments=[
        "-f", "https://ifood-data-architect-test-source.s3-sa-east-1.amazonaws.com/consumer.csv.gz",
        "-o", "s3://task-orchestration-platform",
        "-n", "consumer.csv.gz"
    ],
    env_vars={
        'AWS_ACCESS_KEY_ID': AWS_CREDENTIALS.get('aws_access_key_id'),
        'AWS_SECRET_ACCESS_KEY': AWS_CREDENTIALS.get('aws_secret_access_key'),
        'AWS_DEFAULT_REGION': 'us-east-1'
    },
    labels={"foo": "bar"},
    name="download-file",
    task_id="download-file",
    get_logs=True,
    dag=dag
)

print_file_content_task = KubernetesPodOperator(
    namespace="airflow",
    image="localhost:5000/task-scripts",
    image_pull_policy='Always',
    cmds=["python3", "./scripts/print_records.py"],
    arguments=[
        "--file-path", "s3://task-orchestration-platform/consumer.csv.gz",
        "--compression", "gzip"
    ],
    env_vars={
        'AWS_ACCESS_KEY_ID': AWS_CREDENTIALS.get('aws_access_key_id'),
        'AWS_SECRET_ACCESS_KEY': AWS_CREDENTIALS.get('aws_secret_access_key'),
        'AWS_DEFAULT_REGION': 'us-east-1'
    },
    labels={"foo": "bar"},
    name="print-records",
    task_id="print-records",
    get_logs=True,
    dag=dag,
)

start_task.set_downstream(download_file_task)
download_file_task.set_downstream(print_file_content_task)
print_file_content_task.set_downstream(done_task)
