.SILENT:
CLUSTER_NAME=task-orchestration-platform

create-cluster:
	kind create cluster --config=kind-cluster.yml --name ${CLUSTER_NAME}

create-namespace:
	kubectl create namespace airflow

apply-manifests:
	kubectl apply -f variables.yml -n airflow
	kubectl apply -f pv.yml -n airflow
	kubectl apply -f pvc.yml -n airflow

install-airflow:
	helm upgrade --install airflow apache-airflow/airflow -n airflow -f values.yml

upgrade-airflow:
	helm upgrade airflow apache-airflow/airflow -n airflow -f values.yml

proxy:
	kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow

delete-cluster:
	kind delete cluster --name ${CLUSTER_NAME}

up: create-cluster create-namespace apply-manifests install-airflow

down: delete-cluster