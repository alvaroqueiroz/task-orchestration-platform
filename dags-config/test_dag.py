import json
from airflow import DAG
from kubernetes.client import models as k8s
from datetime import datetime, timedelta
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
from airflow.operators.dummy_operator import DummyOperator


volume_mount = k8s.V1VolumeMount(
    name='test-volume', mount_path='/opt/airflow', sub_path=None, read_only=True
)

volume = k8s.V1Volume(
    name='test-volume',
    persistent_volume_claim=k8s.V1PersistentVolumeClaimVolumeSource(claim_name='test-volume'),
)


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
        "--file-uri", "https://ifood-data-architect-test-source.s3-sa-east-1.amazonaws.com/consumer.csv.gz",
        "--output-path", "/opt/airflow/files/consumer.csv.gz"
    ],
    labels={"foo": "bar"},
    name="download-file",
    task_id="download-file",
    volumes=[volume],
    volume_mounts=[volume_mount],
    get_logs=True,
    dag=dag
)

print_file_content_task = KubernetesPodOperator(
    namespace="airflow",
    image="localhost:5000/task-scripts",
    image_pull_policy='Always',
    cmds=["python3", "./scripts/read_s3_file.py"],
    arguments=[
        "--file-path", "/opt/airflow/files/consumer.csv.gz",
        "--compression", "gzip"
    ],
    labels={"foo": "bar"},
    name="read-s3-file",
    task_id="read-s3-file",
    volumes=[volume],
    volume_mounts=[volume_mount],
    get_logs=True,
    dag=dag,
)

start_task.set_downstream(download_file_task)
download_file_task.set_downstream(print_file_content_task)
print_file_content_task.set_downstream(done_task)
