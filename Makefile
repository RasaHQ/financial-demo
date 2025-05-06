SHELL := /bin/bash

# Extract rasa version to install from `requirements.txt`
RASA_TAG := $(shell cat requirements.txt | grep 'rasa\[spacy\]' | cut -d'=' -f 3 )-spacy-en
# Make sure to install a compatible Rasa Enterprise:
RASAX_TAG := 0.40.1
# Make sure to use a compatible rasa-x-helm chart:
RASAX_HELM_CHART_VERSION := 1.16.0

GIT_BRANCH_NAME := $(shell git branch --show-current)

ACTION_SERVER_DOCKER_IMAGE_NAME := financial-demo
ACTION_SERVER_DOCKER_IMAGE_TAG := $(GIT_BRANCH_NAME)
ACTION_SERVER_DOCKER_CONTAINER_NAME := financial-demo_$(GIT_BRANCH_NAME)
ACTION_SERVER_PORT := 5056
ACTION_SERVER_ENDPOINT_HEALTH := health

RASA_MODEL_NAME := $(GIT_BRANCH_NAME)
RASA_MODEL_PATH := models/$(GIT_BRANCH_NAME).tar.gz

help:
	@echo "make"
	@echo "	clean"
	@echo "		Remove Python/build artifacts."
	@echo "	formatter"
	@echo "		Apply black formatting to code."
	@echo "	lint"
	@echo "		Lint code with flake8, and check if black formatter should be applied."
	@echo "	types"
	@echo "		Check for type errors using pytype."
	@echo "	test"
	@echo "		Run unit tests for the custom actions using pytest."
	@echo "	docker-build"
	@echo "		Builds the custom action server image."
	@echo "	docker-clean"
	@echo "		Runs docker-clean-container & docker-clean-image."
	@echo "	docker-clean-container"
	@echo "		Stops & removes container created by docker-run."
	@echo "	docker-clean-image"
	@echo "		Removes image created by docker-buil."
	@echo "	docker-login"
	@echo "		Logs into a docker registry."
	@echo "	docker-push"
	@echo "		Pushes the action server docker image to the ECR repository."
	@echo "	docker-run"
	@echo "		Runs the action server docker image."
	@echo "	docker-stop"
	@echo "		Stops the action server docker container."
	@echo "	docker-test"
	@echo "		Performs a basic test for a running action server docker container."
	@echo "	install-eksctl"
	@echo "		Installs eksctl."
	@echo "	install-helm"
	@echo "		Installs helm."
	@echo "	install-jp"
	@echo "		Installs jp."
	@echo "	install-kubectl"
	@echo "		Installs kubectl."
	@echo "	kubectl-config-current-context"
	@echo "		Gets the current kubectl context (The EKS cluster)."
	@echo "	pull-secret-ecr-create"
	@echo "		Creates an ECR pull secret for action server image."
	@echo "	pull-secret-ecr-delete"
	@echo "		Deletes the ECR pull secret."
	@echo "	pull-secret-gcr-create"
	@echo "		Creates a GCR pull secret for Rasa Enterprise image."
	@echo "	pull-secret-gcr-delete"
	@echo "		Deletes the GCR pull secret."
	@echo "	rasa-enterprise-check-health"
	@echo "		Checks <->/api/health of Rasa Enterprise."
	@echo "	rasa-enterprise-get-access-token"
	@echo "		Gets access token of Rasa Enterprise."
	@echo "	rasa-enterprise-get-base-url"
	@echo "		Gets base URL of Rasa Enterprise."
	@echo "	rasa-enterprise-get-chat-token"
	@echo "		Gets chat token of Rasa Enterprise."
	@echo "	rasa-enterprise-get-loadbalancer-hostname"
	@echo "		Gets the load balancer hostname for Rasa Enterprise."
	@echo "	rasa-enterprise-get-login"
	@echo "		Gets login URL of Rasa Enterprise."
	@echo "	rasa-enterprise-get-pods"
	@echo "		Gets pods of Rasa Enterprise deployed in the EKS cluster."
	@echo "	rasa-enterprise-get-secrets-postgresql"
	@echo "		Gets secrets of PostgreSQL deployed with Rasa Enterprise."
	@echo "	rasa-enterprise-get-secrets-rabbit"
	@echo "		Gets secrets of RabbitMQ deployed with Rasa Enterprise."
	@echo "	rasa-enterprise-get-secrets-redis"
	@echo "		Gets secrets of REDIS deployed with Rasa Enterprise."
	@echo "	rasa-enterprise-install"
	@echo "		Installs or Upgrades Rasa Enterprise using helm."
	@echo "	rasa-enterprise-model-delete"
	@echo "		Deletes a trained rasa model in Rasa Enterprise."
	@echo "	rasa-enterprise-model-tag"
	@echo "		Tags a trained rasa model as the production model in Rasa Enterprise."
	@echo "	rasa-enterprise-model-upload"
	@echo "		Uploads a trained rasa model to Rasa Enterprise."
	@echo "	rasa-enterprise-smoketest"
	@echo "		Performs smoketest to verify Rasa Enterprise is functioning."
	@echo "	rasa-enterprise-uninstall"
	@echo "		Uninstalls Rasa Enterprise."
	@echo "	rasa-test-stories"
	@echo "		Runs DM1 test stories on a trained rasa model."
	@echo "	rasa-test-e2e"
	@echo "		Runs Rasa end-to-end tests on a trained rasa model."
	@echo "	rasa-train"
	@echo "		Trains a rasa model."


clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +
	rm -rf build/
	rm -rf .pytype/
	rm -rf dist/
	rm -rf docs/_build

install-eksctl:
	curl --silent --location "https://github.com/weaveworks/eksctl/releases/download/0.51.0/eksctl_Linux_amd64.tar.gz" | tar xz -C /tmp
	sudo mv /tmp/eksctl /usr/local/bin
	@echo $(NEWLINE)
	eksctl version
	@echo $(NEWLINE)

install-kubectl:
	sudo snap install kubectl --classic
	@echo $(NEWLINE)
	@kubectl version --client --short

install-helm:
	sudo snap install helm --classic
	@echo $(NEWLINE)
	@helm version --short

install-jp:
	sudo apt-get update && sudo apt-get install jp
	@echo $(NEWLINE)
	@jp --version

rasa-train:
	@echo Training $(RASA_MODEL_NAME)
	rasa train --fixed-model-name $(RASA_MODEL_NAME)

rasa-test-stories:
	@echo Testing $(RASA_MODEL_PATH)
	rasa test core -s tests/test_stories.yml --model $(RASA_MODEL_PATH)

rasa-test-e2e:
	@echo Testing $(RASA_MODEL_PATH)
	rasa test e2e --debug --model $(RASA_MODEL_PATH)

formatter:
	black actions

lint:
	flake8 actions
	black --check actions

types:
	pytype --keep-going actions

test:
	pytest tests

docker-build:
	docker build . --file Dockerfile --tag $(AWS_ECR_URI)/$(ACTION_SERVER_DOCKER_IMAGE_NAME):$(ACTION_SERVER_DOCKER_IMAGE_TAG)

docker-run:
	docker run -d -p $(ACTION_SERVER_PORT):5055 --name $(ACTION_SERVER_DOCKER_CONTAINER_NAME) $(AWS_ECR_URI)/$(ACTION_SERVER_DOCKER_IMAGE_NAME):$(ACTION_SERVER_DOCKER_IMAGE_TAG)

docker-test:
	curl http://localhost:$(ACTION_SERVER_PORT)/$(ACTION_SERVER_ENDPOINT_HEALTH)
	@echo $(NEWLINE)

docker-stop:
	docker stop $(ACTION_SERVER_DOCKER_CONTAINER_NAME)

docker-clean-container:
	docker stop $(ACTION_SERVER_DOCKER_CONTAINER_NAME)
	docker rm $(ACTION_SERVER_DOCKER_CONTAINER_NAME)

docker-clean-image:
	docker rmi $(AWS_ECR_URI)/$(ACTION_SERVER_DOCKER_IMAGE_NAME):$(ACTION_SERVER_DOCKER_IMAGE_TAG)

docker-clean: docker-clean-container docker-clean-image

docker-login:
	@echo docker registry: $(DOCKER_REGISTRY)
	@echo docker user: $(DOCKER_USER)
	@echo $(DOCKER_PW) | docker login $(DOCKER_REGISTRY) -u $(DOCKER_USER) --password-stdin

docker-pull:
	@$(eval IMAGE_EXISTS := $(shell make --no-print-directory aws-ecr-image-exists ACTION_SERVER_DOCKER_IMAGE_TAG=$(ACTION_SERVER_DOCKER_IMAGE_TAG) ))

	@if [[ ${IMAGE_EXISTS} == "False" ]]; then \
		echo "$(ACTION_SERVER_DOCKER_IMAGE_NAME):$(ACTION_SERVER_DOCKER_IMAGE_TAG) image does not exist. "; \
	else \
		echo pulling image: $(AWS_ECR_URI)/$(ACTION_SERVER_DOCKER_IMAGE_NAME):$(ACTION_SERVER_DOCKER_IMAGE_TAG); \
		echo pulling image: $(AWS_ECR_URI)/$(ACTION_SERVER_DOCKER_IMAGE_NAME):$(ACTION_SERVER_DOCKER_IMAGE_TAG); \
		docker image pull $(AWS_ECR_URI)/$(ACTION_SERVER_DOCKER_IMAGE_NAME):$(ACTION_SERVER_DOCKER_IMAGE_TAG); \
	fi
	
docker-push:
	@echo pushing image: $(AWS_ECR_URI)/$(ACTION_SERVER_DOCKER_IMAGE_NAME):$(ACTION_SERVER_DOCKER_IMAGE_TAG)
	docker image push $(AWS_ECR_URI)/$(ACTION_SERVER_DOCKER_IMAGE_NAME):$(ACTION_SERVER_DOCKER_IMAGE_TAG)


kubectl-config-current-context:
	kubectl config current-context

pull-secret-gcr-create:
	@[ "${GCR_AUTH_JSON_PRIVATE_KEY_ID}" ]	|| ( echo ">> GCR_AUTH_JSON_PRIVATE_KEY_ID is not set"; exit 1 )
	@[ "${GCR_AUTH_JSON_PRIVATE_KEY}" ]		|| ( echo ">> GCR_AUTH_JSON_PRIVATE_KEY is not set"; exit 1 )
	@[ "${GCR_AUTH_JSON_CLIENT_EMAIL}" ]	|| ( echo ">> GCR_AUTH_JSON_CLIENT_EMAIL is not set"; exit 1 )
	@[ "${GCR_AUTH_JSON_CLIENT_ID}" ]		|| ( echo ">> GCR_AUTH_JSON_CLIENT_ID is not set"; exit 1 )
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		delete secret gcr-pull-secret \
		--ignore-not-found
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		create secret docker-registry gcr-pull-secret \
		--docker-server=gcr.io \
		--docker-username=_json_key \
		--docker-password='$(shell python ./scripts/patch_gcr_auth_json.py)'

pull-secret-gcr-delete:
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		delete secret gcr-pull-secret \
		--ignore-not-found
