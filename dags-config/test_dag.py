import json
from airflow import DAG
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


start = DummyOperator(task_id="run_this_first", dag=dag)

passing = KubernetesPodOperator(
    namespace="airflow",
    image="localhost:5000/task-scripts",
    image_pull_policy='Always',
    cmds=["python3", "./scripts/read_s3_file.py"],
    arguments=[
        "-f", "s3://task-orchestration-platform/files/consumer.csv.gz",
        "-c", "gzip"
    ],
    env_vars={
        'AWS_ACCESS_KEY_ID': AWS_CREDENTIALS.get('aws_access_key_id'),
        'AWS_SECRET_ACCESS_KEY': AWS_CREDENTIALS.get('aws_secret_access_key'),
        'AWS_DEFAULT_REGION': 'us-east-1'
    },
    labels={"foo": "bar"},
    name="read-s3-file",
    task_id="read-s3-file",
    get_logs=True,
    dag=dag,
)

passing.set_upstream(start)
