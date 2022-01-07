.SILENT:
CLUSTER_NAME=taks-orchestration-platform

create-cluster:
	kind create cluster --config=kind-cluster.yml --name ${CLUSTER_NAME}

create-namespace:
	kubectl create namespace airflow

delete-cluster:
	kind delete cluster --name ${CLUSTER_NAME}

up: create-cluster create-namespace

down: delete-cluster