.SILENT:
CLUSTER_NAME=task-orchestration-platform
DOCKER_IMAGE_NAME=task-scripts
AWS_ACCESS_KEY=
AWS_SECRET_ACCESS_KEY_ID=

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

docker-build-and-upload:
	docker build . -t ${DOCKER_IMAGE_NAME}
	docker tag ${DOCKER_IMAGE_NAME}:latest localhost:5000/${DOCKER_IMAGE_NAME}:latest
	docker push localhost:5000/${DOCKER_IMAGE_NAME}:latest	

.PHONY: create-airflow-aws-connection
create-airflow-aws-connection:
	kubectl exec -it -n airflow $(shell kubectl get pods -n airflow | grep scheduler | awk '{print $1}') -c scheduler -- sh \
		-c "airflow connections add 'aws_default'  --conn-type aws --conn-extra '{\"aws_access_key_id\":\"${AWS_ACCESS_KEY}\", \"aws_secret_access_key\": \"${AWS_SECRET_ACCESS_KEY_ID}\"}'"

proxy:
	kubectl port-forward svc/airflow-webserver 8080:8080 -n airflow

delete-cluster:
	kind delete cluster --name ${CLUSTER_NAME}

up: create-cluster create-registry create-namespace apply-manifests install-airflow docker-build-and-upload

down: delete-cluster