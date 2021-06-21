SHELL := /bin/bash

# Extract rasa version to install from `requirements.txt`
RASA_TAG := $(shell cat requirements.txt | grep 'rasa\[spacy\]' | cut -d'=' -f 3 )-spacy-en
# Make sure to install a compatible Rasa Enterprise:
RASAX_TAG := 0.38.1

ACTION_SERVER_DOCKER_IMAGE_NAME := financial-demo
ACTION_SERVER_DOCKER_IMAGE_TAG := $(shell git branch --show-current)
ACTION_SERVER_DOCKER_CONTAINER_NAME := financial-demo_$(shell git branch --show-current)
ACTION_SERVER_PORT := 5056
ACTION_SERVER_ENDPOINT_HEALTH := health

RASA_MODEL_NAME := $(shell git branch --show-current)
RASA_MODEL_PATH := models/$(shell git branch --show-current).tar.gz

# The CICD pipeline sets these as environment variables 
# Set some defaults for when you're running locally
AWS_REGION := us-west-2

AWS_ECR_URI := 024629701212.dkr.ecr.us-west-2.amazonaws.com
AWS_ECR_REPOSITORY := financial-demo

AWS_S3_BUCKET_NAME := rasa-financial-demo

AWS_IAM_ROLE_NAME := eksClusterRole

#AWS_EKS_VPC_STACK_NAME := eks-vpc-financial-demo-$(shell git branch --show-current)
AWS_EKS_VPC_TEMPLATE := aws/cloudformation/amazon-eks-vpc-private-subnets.yaml
AWS_EKS_KEYPAIR_NAME := findemo
AWS_EKS_CLUSTER_NAME := financial-demo-$(shell git branch --show-current)
AWS_EKS_KUBERNETES_VERSION := 1.19

AWS_EKS_NAMESPACE := my-namespace
AWS_EKS_RELEASE_NAME := my-release

GIT_BRANCH_NAME := $(shell git branch --show-current)

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
	@echo "	aws-cloudformation-eks-get-ARN"
	@echo "		Gets Amazon Resource Name (ARN) of an EKS cluster."
	@echo "	aws-cloudformation-eks-get-CertificateAuthorityData"
	@echo "		Gets CertificateAuthorityData of an EKS cluster."
	@echo "	aws-cloudformation-eks-get-ClusterSecurityGroupId"
	@echo "		Gets Security Group ID of an EKS cluster."
	@echo "	aws-cloudformation-eks-get-Endpoint"
	@echo "		Gets Endpoint (https://...) of an EKS cluster."
	@echo "	aws-cloudformation-eks-get-SecurityGroup"
	@echo "		Gets Security Group ID of nodes in an EKS cluster."
	@echo "	aws-cloudformation-eks-get-ServiceRoleARN"
	@echo "		Gets Amazon Resource Name (ARN) of an EKS cluster Service Role."
	@echo "	aws-cloudformation-eks-get-SharedNodeSecurityGroup"
	@echo "		Gets SharedNodeSecurityGroup of an EKS cluster."
	@echo "	aws-cloudformation-eks-get-SubnetsPrivate"
	@echo "		Gets the private subnets of an EKS cluster."
	@echo "	aws-cloudformation-eks-get-SubnetsPublic"
	@echo "		Gets the public subnets of an EKS cluster."
	@echo "	aws-cloudformation-eks-get-VPC"
	@echo "		Gets the VPC of an EKS cluster."
	@echo "	aws-ecr-create-repository"
	@echo "		Creates an ECR repository to store docker images."
	@echo "	aws-ecr-docker-login"
	@echo "		Logs docker cli into the ECR."
	@echo "	aws-ecr-get-authorization-token"
	@echo "		Gets a short lived authentication token for the ECR."
	@echo "	aws-ecr-get-repositoryUri"
	@echo "		Gets the URI of an ECR repository."
	@echo "	aws-eks-cluster-create"
	@echo "		Creates an EKS cluster with ssh-access & managed nodes, using eksctl."
	@echo "	aws-eks-cluster-delete"
	@echo "		Deletes an EKS cluster."
	@echo "	aws-eks-cluster-describe"
	@echo "		Describes an EKS cluster."
	@echo "	aws-eks-cluster-describe-stacks"
	@echo "		Describes the cloudformation stacks created by the eksctl command."
	@echo "	aws-eks-cluster-exists"
	@echo "		Checks if an EKS cluster exits."
	@echo "	aws-eks-cluster-get-certificateAuthority"
	@echo "		Gets Certificate Authority of an EKS cluster."
	@echo "	aws-eks-cluster-get-endpoint"
	@echo "		Gets Endpoint (https://...) of an EKS cluster.."
	@echo "	aws-eks-cluster-info"
	@echo "		Describes an EKS cluster."
	@echo "	aws-eks-cluster-list-all"
	@echo "		Lists all EKS clusters."
	@echo "	aws-eks-cluster-status"
	@echo "		Gets status of an EKS cluster."
	@echo "	aws-eks-cluster-update-kubeconfig"
	@echo "		Add the EKS  cluster information to ~/.kube/config, and set the current-context to that cluster."
	@echo "	aws-eks-namespace-create"
	@echo "		Creates a namespace in an EKS cluster."
	@echo "	aws-eks-namespace-delete"
	@echo "		Deletes a namespace in an EKS cluster."
	@echo "	aws-iam-role-get-Arn"
	@echo "		Gets the eksClusterRole of an EKS cluster."
	@echo "	aws-s3-create-bucket"
	@echo "		Creates an S3 bucket to store trained rasa models."
	@echo "	aws-s3-delete-bucket"
	@echo "		Deletes an S3 bucket."
	@echo "	aws-s3-download-rasa-model"
	@echo "		Downloads a trained rasa model from an S3 bucket."
	@echo "	aws-s3-upload-rasa-model"
	@echo "		Uploads a trained rasa model to an S3 bucket."
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
	@echo "	rasa-test"
	@echo "		Tests a trained rasa model."
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
	
rasa-test:
	@echo Testing $(RASA_MODEL_PATH)
	rasa test --model $(RASA_MODEL_PATH)
	
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

docker-push:
	@echo pushing image: $(AWS_ECR_URI)/$(ACTION_SERVER_DOCKER_IMAGE_NAME):$(ACTION_SERVER_DOCKER_IMAGE_TAG)
	docker image push $(AWS_ECR_URI)/$(ACTION_SERVER_DOCKER_IMAGE_NAME):$(ACTION_SERVER_DOCKER_IMAGE_TAG)
		
aws-iam-role-get-Arn:	
	@aws iam get-role \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--role-name $(AWS_IAM_ROLE_NAME) \
		--query "Role.Arn"
		
aws-ecr-docker-login:
	@$(eval AWS_ECR_URI := $(shell make aws-ecr-get-repositoryUri))
	@echo logging into AWS ECR registry: $(AWS_ECR_URI)
	aws ecr get-login-password --region $(AWS_REGION) | docker login --username AWS --password-stdin $(AWS_ECR_URI)
	
aws-ecr-create-repository:
	@echo creating ecr repository: $(AWS_ECR_REPOSITORY)
	@echo $(NEWLINE)
	aws ecr create-repository \
		--repository-name $(AWS_ECR_REPOSITORY) \
		--region $(AWS_REGION)

aws-ecr-get-authorization-token:	
	@aws ecr get-authorization-token \
		--no-paginate \
		--output text \
		--region=$(AWS_REGION) \
		--query authorizationData[].authorizationToken | base64 -d | cut -d: -f2
		
aws-ecr-get-repositoryUri:	
	@aws ecr describe-repositories \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--repository-names $(AWS_ECR_REPOSITORY) \
		--query "repositories[].repositoryUri"
		
aws-s3-create-bucket:
	@echo creating s3 bucket: $(AWS_S3_BUCKET_NAME)
	@echo $(NEWLINE)
	aws s3api create-bucket \
		--bucket $(AWS_S3_BUCKET_NAME) \
		--region $(AWS_REGION) \
		--create-bucket-configuration LocationConstraint=$(AWS_REGION)

aws-s3-delete-bucket:
	@echo deleting s3 bucket: $(AWS_S3_BUCKET_NAME)
	aws s3 rb s3://$(AWS_S3_BUCKET_NAME) --force

aws-s3-upload-rasa-model:
	@echo uploading $(RASA_MODEL_PATH) to s3://$(AWS_S3_BUCKET_NAME)/$(RASA_MODEL_PATH)
	aws s3 cp $(RASA_MODEL_PATH) s3://$(AWS_S3_BUCKET_NAME)/$(RASA_MODEL_PATH)

aws-s3-download-rasa-model:
	@echo downloading $(RASA_MODEL_PATH) from s3://$(AWS_S3_BUCKET_NAME)/$(RASA_MODEL_PATH)
	aws s3 cp s3://$(AWS_S3_BUCKET_NAME)/$(RASA_MODEL_PATH) $(RASA_MODEL_PATH) 

aws-cloudformation-eks-get-SubnetsPrivate:	
	@aws cloudformation describe-stacks \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--stack-name eksctl-$(AWS_EKS_CLUSTER_NAME)-cluster \
		--query "Stacks[].Outputs[?OutputKey=='SubnetsPrivate'].OutputValue"
		
aws-cloudformation-eks-get-SubnetsPublic:	
	@aws cloudformation describe-stacks \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--stack-name eksctl-$(AWS_EKS_CLUSTER_NAME)-cluster \
		--query "Stacks[].Outputs[?OutputKey=='SubnetsPublic'].OutputValue"
		
aws-cloudformation-eks-get-ServiceRoleARN:	
	@aws cloudformation describe-stacks \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--stack-name eksctl-$(AWS_EKS_CLUSTER_NAME)-cluster \
		--query "Stacks[].Outputs[?OutputKey=='ServiceRoleARN'].OutputValue"
		
aws-cloudformation-eks-get-Endpoint:	
	@aws cloudformation describe-stacks \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--stack-name eksctl-$(AWS_EKS_CLUSTER_NAME)-cluster \
		--query "Stacks[].Outputs[?OutputKey=='Endpoint'].OutputValue"
		
aws-cloudformation-eks-get-SharedNodeSecurityGroup:	
	@aws cloudformation describe-stacks \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--stack-name eksctl-$(AWS_EKS_CLUSTER_NAME)-cluster \
		--query "Stacks[].Outputs[?OutputKey=='SharedNodeSecurityGroup'].OutputValue"

aws-cloudformation-eks-get-VPC:	
	@aws cloudformation describe-stacks \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--stack-name eksctl-$(AWS_EKS_CLUSTER_NAME)-cluster \
		--query "Stacks[].Outputs[?OutputKey=='VPC'].OutputValue"

aws-cloudformation-eks-get-ClusterSecurityGroupId:	
	@aws cloudformation describe-stacks \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--stack-name eksctl-$(AWS_EKS_CLUSTER_NAME)-cluster \
		--query "Stacks[].Outputs[?OutputKey=='ClusterSecurityGroupId'].OutputValue"

aws-cloudformation-eks-get-CertificateAuthorityData:	
	@aws cloudformation describe-stacks \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--stack-name eksctl-$(AWS_EKS_CLUSTER_NAME)-cluster \
		--query "Stacks[].Outputs[?OutputKey=='CertificateAuthorityData'].OutputValue"

aws-cloudformation-eks-get-SecurityGroup:	
	@aws cloudformation describe-stacks \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--stack-name eksctl-$(AWS_EKS_CLUSTER_NAME)-cluster \
		--query "Stacks[].Outputs[?OutputKey=='SecurityGroup'].OutputValue"

aws-cloudformation-eks-get-ARN:	
	@aws cloudformation describe-stacks \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--stack-name eksctl-$(AWS_EKS_CLUSTER_NAME)-cluster \
		--query "Stacks[].Outputs[?OutputKey=='ARN'].OutputValue"
	
aws-eks-cluster-create:		
	eksctl create cluster \
		--name $(AWS_EKS_CLUSTER_NAME) \
		--region $(AWS_REGION) \
		--version $(AWS_EKS_KUBERNETES_VERSION) \
		--with-oidc \
		--ssh-access \
		--ssh-public-key $(AWS_EKS_KEYPAIR_NAME) \
		--managed

aws-eks-cluster-list-all:		
	eksctl get cluster
		
aws-eks-cluster-info:
	kubectl cluster-info
	
# https://docs.aws.amazon.com/eks/latest/userguide/delete-cluster.html
aws-eks-cluster-delete:
	@[ "${GIT_BRANCH_NAME}" != "main" ]	|| ( echo ">> You are on main branch. Deletion via Makefile not allowed"; exit 1 )
	eksctl delete cluster \
		--name $(AWS_EKS_CLUSTER_NAME) \
		--region $(AWS_REGION) 
	@echo $(NEWLINE)
	@echo See AWS CloudFormation Console. The stack deletion is still in progress...

aws-eks-cluster-exists:
	@aws eks list-clusters \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--query "contains(clusters[*], '$(AWS_EKS_CLUSTER_NAME)')"	
		
aws-eks-cluster-describe:	
	@aws eks describe-cluster \
		--no-paginate \
		--region $(AWS_REGION) \
		--name $(AWS_EKS_CLUSTER_NAME) 
		
aws-eks-cluster-describe-stacks:	
	@eksctl utils describe-stacks \
		--region $(AWS_REGION) \
		--cluster $(AWS_EKS_CLUSTER_NAME) 
		
aws-eks-cluster-status:	
	@aws eks describe-cluster \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--name $(AWS_EKS_CLUSTER_NAME) \
		--query "cluster.status"	

aws-eks-cluster-get-endpoint:
	@aws eks describe-cluster \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--name $(AWS_EKS_CLUSTER_NAME) \
		--query "cluster.endpoint"

aws-eks-cluster-get-certificateAuthority:
	@aws eks describe-cluster \
		--no-paginate \
		--output text \
		--region $(AWS_REGION) \
		--name $(AWS_EKS_CLUSTER_NAME) \
		--query "cluster.certificateAuthority"

aws-eks-cluster-update-kubeconfig:
	@echo Updating kubeconfig for AWS EKS cluster with name: $(AWS_EKS_CLUSTER_NAME)
	@echo $(NEWLINE)
	aws eks update-kubeconfig \
		--region $(AWS_REGION) \
		--name $(AWS_EKS_CLUSTER_NAME)	

aws-eks-namespace-create:
	kubectl create namespace $(AWS_EKS_NAMESPACE) --dry-run=client -o yaml | kubectl apply -f -
	
aws-eks-namespace-delete:
	@[ "${GIT_BRANCH_NAME}" != "main" ]	|| ( echo ">> You are on main branch. Deletion via Makefile not allowed"; exit 1 )
	kubectl delete namespace $(AWS_EKS_NAMESPACE)
	

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

pull-secret-ecr-create:
	@$(eval AWS_ECR_TOKEN := $(shell make aws-ecr-get-authorization-token))
	@$(eval AWS_ECR_URI := $(shell make aws-ecr-get-repositoryUri))
	
	@echo "Creating pull secret for Action Server (in ECR)"
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		delete secret ecr-pull-secret \
		--ignore-not-found

	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		create secret docker-registry ecr-pull-secret \
		--docker-server=https://$(AWS_ECR_URI) \
		--docker-username=AWS \
		--docker-password="$(AWS_ECR_TOKEN)"
		
pull-secret-ecr-delete:
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		delete secret ecr-pull-secret \
		--ignore-not-found
		
rasa-enterprise-install:
	@[ "${GLOBAL_POSTGRESQL_POSTGRESQLPASSWORD}" ]	|| ( echo ">> GLOBAL_POSTGRESQL_POSTGRESQLPASSWORD is not set"; exit 1 )
	@[ "${GLOBAL_REDIS_PASSWORD}" ]					|| ( echo ">> GLOBAL_REDIS_PASSWORD is not set"; exit 1 )
	@[ "${RABBITMQ_RABBITMQ_PASSWORD}" ]			|| ( echo ">> RABBITMQ_RABBITMQ_PASSWORD is not set"; exit 1 )
	@[ "${RASAX_INITIALUSER_USERNAME}" ]			|| ( echo ">> RASAX_INITIALUSER_USERNAME is not set"; exit 1 )
	@[ "${RASAX_INITIALUSER_PASSWORD}" ]			|| ( echo ">> RASAX_INITIALUSER_PASSWORD is not set"; exit 1 )
	@[ "${RASAX_JWTSECRET}" ]						|| ( echo ">> RASAX_JWTSECRET is not set"; exit 1 )
	@[ "${RASAX_PASSWORDSALT}" ]					|| ( echo ">> RASAX_PASSWORDSALT is not set"; exit 1 )
	@[ "${RASAX_TOKEN}" ]							|| ( echo ">> RASAX_TOKEN is not set"; exit 1 )
	@[ "${RASA_TOKEN}" ]							|| ( echo ">> RASA_TOKEN is not set"; exit 1 )
	
	@[ "${RASAX_TAG}" ]								|| ( echo ">> RASAX_TAG is not set"; exit 1 )	
	@[ "${RASA_TAG}" ]								|| ( echo ">> RASA_TAG is not set"; exit 1 )
	@[ "${AWS_ECR_URI}" ]							|| ( echo ">> AWS_ECR_URI is not set"; exit 1 )
	@[ "${ACTION_SERVER_DOCKER_IMAGE_NAME}" ]		|| ( echo ">> ACTION_SERVER_DOCKER_IMAGE_NAME is not set"; exit 1 )
	@[ "${ACTION_SERVER_DOCKER_IMAGE_TAG}" ]		|| ( echo ">> ACTION_SERVER_DOCKER_IMAGE_TAG is not set"; exit 1 )

	helm repo add rasa-x https://rasahq.github.io/rasa-x-helm
	helm repo update

	@echo $(NEWLINE)
	@echo Installing or Upgrading Rasa Enterprise with:
	@echo - RASAX_TAG: $(RASAX_TAG)
	@echo - RASA_TAG: $(RASA_TAG)
	@echo - APP_NAME: $(AWS_ECR_URI)/$(ACTION_SERVER_DOCKER_IMAGE_NAME)
	@echo - APP_TAG: $(ACTION_SERVER_DOCKER_IMAGE_TAG)
	@echo $(NEWLINE)
	@helm --namespace $(AWS_EKS_NAMESPACE) \
		upgrade \
		--install \
		--values ./deploy/values.yml \
		--set rasax.tag=$(RASAX_TAG) \
		--set rasax.initialUser.username=$(RASAX_INITIALUSER_USERNAME) \
		--set rasax.initialUser.password=$(RASAX_INITIALUSER_PASSWORD) \
		--set rasax.passwordSalt=$(RASAX_PASSWORDSALT) \
		--set rasax.token=$(RASAX_TOKEN) \
		--set rasax.jwtSecret=$(RASAX_JWTSECRET) \
		--set rasa.tag=$(RASA_TAG) \
		--set rasa.token=$(RASA_TOKEN) \
		--set rabbitmq.rabbitmq.password=$(RABBITMQ_RABBITMQ_PASSWORD) \
		--set global.postgresql.postgresqlPassword=$(GLOBAL_POSTGRESQL_POSTGRESQLPASSWORD) \
		--set global.redis.password=$(GLOBAL_REDIS_PASSWORD) \
		--set app.name=$(AWS_ECR_URI)/$(ACTION_SERVER_DOCKER_IMAGE_NAME) \
		--set app.tag=$(ACTION_SERVER_DOCKER_IMAGE_TAG) \
		$(AWS_EKS_RELEASE_NAME) \
		rasa-x/rasa-x
	
	@echo $(NEWLINE)	
	@echo Waiting until all deployments are AVAILABLE
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		wait \
		--for=condition=available \
		--timeout=20m \
		--all \
		deployment
		
	@echo $(NEWLINE)	
	@echo Waiting until all pods are READY
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		wait \
		--for=condition=ready \
		--timeout=20m \
		--all \
		pod
	
	@echo $(NEWLINE)	
	@echo Waiting for external IP assignment	
	@./scripts/wait_for_external_ip.sh $(AWS_EKS_NAMESPACE) $(AWS_EKS_RELEASE_NAME)
	
rasa-enterprise-uninstall:
	@echo Uninstalling Rasa Enterprise release $(AWS_EKS_RELEASE_NAME).
	@echo $(NEWLINE)
	@helm --namespace $(AWS_EKS_NAMESPACE) \
		uninstall $(AWS_EKS_RELEASE_NAME)

rasa-enterprise-check-health:
	@$(eval URL := $(shell make rasa-enterprise-get-base-url)/api/health)
	@$(eval PRODUCTION_STATUS := $(shell curl --silent --request GET --url $(URL) | jp production.status))
	@$(eval WORKER_STATUS := $(shell curl --silent --request GET --url $(URL) | jp worker.status))
	@$(eval DB_MIGRATION_STATUS := $(shell curl --silent --request GET --url $(URL) | jp database_migration.status))
	
	@echo Checking health at: $(URL)	
	@curl --silent --request GET --url $(URL) | json_pp

	@[ "${PRODUCTION_STATUS}" = "200" ]	|| ( echo ">> production.status not ok"; exit 1 )
		
	@[ "${WORKER_STATUS}" = "200" ]	|| ( echo ">> worker.status not ok"; exit 1 )
	
	@[ "${DB_MIGRATION_STATUS}" = "completed" ]	|| ( echo ">> database_migration.status not completed (not fatal)" )
		
rasa-enterprise-get-pods:
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		get pods
	
rasa-enterprise-get-secrets-postgresql:
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		get secret $(AWS_EKS_RELEASE_NAME)-postgresql -o yaml | \
		awk -F ': ' '/password/{print $2}' | base64 -d
		
rasa-enterprise-get-secrets-redis:
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		get secret $(AWS_EKS_RELEASE_NAME)-redis -o yaml | \
		awk -F ': ' '/password/{print $2}' | base64 -d
		
rasa-enterprise-get-secrets-rabbit:
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		get secret $(AWS_EKS_RELEASE_NAME)-rabbit -o yaml | \
		awk -F ': ' '/password/{print $2}' | base64 -d

	
rasa-enterprise-get-login:
	@./scripts/wait_for_external_ip.sh $(AWS_EKS_NAMESPACE) $(AWS_EKS_RELEASE_NAME) 1
	
rasa-enterprise-get-access-token:
	@$(eval URL := $(shell make rasa-enterprise-get-base-url)/api/auth)
	@curl --silent --request POST --url $(URL) \
		--header 'Content-Type: application/json' \
		--data '{ "username": "$(RASAX_INITIALUSER_USERNAME)", "password": "$(RASAX_INITIALUSER_PASSWORD)" }' \
		| jp --unquoted access_token
		
rasa-enterprise-get-chat-token:
	@$(eval URL := $(shell make rasa-enterprise-get-base-url)/api/chatToken)
	@$(eval ACCESS_TOKEN := $(shell make rasa-enterprise-get-access-token))
	@curl --silent --request GET --url $(URL) \
		--header 'Authorization: Bearer $(ACCESS_TOKEN)' \
		| jp --unquoted chat_token

rasa-enterprise-model-upload:
	@$(eval URL := $(shell make rasa-enterprise-get-base-url)/api/projects/default/models)
	@$(eval ACCESS_TOKEN := $(shell make rasa-enterprise-get-access-token))
	@$(eval CURL_OUTPUT_FILE := /tmp/curl_output_$(shell date +'%y%m%d_%H%M%S').txt)
	
	@echo "Uploading model:"
	@echo "- Model: $(RASA_MODEL_PATH)"
	@echo "- URL: $(URL)"	
	@curl -k \
		--progress-bar \
		--output $(CURL_OUTPUT_FILE) \
		--request POST \
		--url "$(URL)" \
		-F "model=@$(RASA_MODEL_PATH)" \
		-H "Authorization: Bearer $(ACCESS_TOKEN)"
	
	@cat $(CURL_OUTPUT_FILE) | json_pp

	@echo $(NEWLINE)
	@if [[ $$(cat ${CURL_OUTPUT_FILE} | jp message) == "null" ]]; then \
		echo "Upload was successful"; \
		rm -f ${CURL_OUTPUT_FILE}; \
	else \
		echo "Error: $$(cat ${CURL_OUTPUT_FILE} | jp message)"; \
		rm -f ${CURL_OUTPUT_FILE}; \
		exit 1; \
	fi


rasa-enterprise-model-tag:	
	@$(eval URL := $(shell make rasa-enterprise-get-base-url)/api/projects/default/models/$(RASA_MODEL_NAME)/tags/production)
	@$(eval ACCESS_TOKEN := $(shell make rasa-enterprise-get-access-token))
	
	@echo "Tagging as production the model:"
	@echo "- Model: $(RASA_MODEL_NAME)"
	@echo "- URL: $(URL)"
	
	@curl \
		--request PUT \
		--url "$(URL)" \
		-H "Authorization: Bearer $(ACCESS_TOKEN)"
		
rasa-enterprise-model-delete:	
	@$(eval URL := $(shell make rasa-enterprise-get-base-url)/api/projects/default/models/$(RASA_MODEL_NAME))
	@$(eval ACCESS_TOKEN := $(shell make rasa-enterprise-get-access-token))
	
	@echo "Deleting the model:"
	@echo "- Model: $(RASA_MODEL_NAME)"
	@echo "- URL: $(URL)"
	
	@curl \
		--request DELETE \
		--url "$(URL)" \
		-H "Authorization: Bearer $(ACCESS_TOKEN)"
		
rasa-enterprise-smoketest:
	@$(eval URL := $(shell make rasa-enterprise-get-base-url))
	export BASE_URL=$(URL); \
	python ./scripts/smoketest.py

rasa-enterprise-get-base-url:
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		get service $(AWS_EKS_RELEASE_NAME)-rasa-x-nginx \
		--output jsonpath='{.status.loadBalancer.ingress[0].hostname}' | \
		awk '{v="http://"$$1":80"; print v}'
		
rasa-enterprise-get-loadbalancer-hostname:	
	@kubectl --namespace $(AWS_EKS_NAMESPACE) \
		get service $(AWS_EKS_RELEASE_NAME)-rasa-x-nginx \
		--output jsonpath='{.status.loadBalancer.ingress[0].hostname}'