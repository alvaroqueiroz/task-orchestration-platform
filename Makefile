.SILENT:
CLUSTER_NAME=task-orchestration-platform
DOCKER_IMAGE_NAME=task-scripts

create-cluster:
	kind create cluster --config=kind-cluster.yml --name ${CLUSTER_NAME}

create-registry:
	sh ./registry.sh

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

docker-build:
	docker build . -t ${DOCKER_IMAGE_NAME}
	docker tag ${DOCKER_IMAGE_NAME}:latest localhost:5000/${DOCKER_IMAGE_NAME}:latest

upload-image:
	kind load docker-image ${DOCKER_IMAGE_NAME}:latest --name ${CLUSTER_NAME} 

proxy:
	kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow

delete-cluster:
	kind delete cluster --name ${CLUSTER_NAME}

up: create-cluster create-registry create-namespace apply-manifests install-airflow docker-build upload-image

down: delete-cluster