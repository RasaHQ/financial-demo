# Notes on Rasa `2.x / 1.x`

1. The `main` branch of this repo is compatible with Rasa Open Source **version 2.x**
2. The bot for **Rasa 1.x** can be found in the [rasa-1 branch](https://github.com/RasaHQ/financial-demo/tree/rasa-1).



# Financial Services Example Bot

This is an example chatbot demonstrating how to build AI assistants for financial services and banking. This starter pack can be used as a base for your own development or as a reference guide for implementing common banking-industry features with Rasa. It includes pre-built intents, actions, and stories for handling conversation flows like checking spending history and transferring money to another account.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

  - [Install dependencies](#install-dependencies)
  - [Run the bot](#run-the-bot)
  - [Overview of the files](#overview-of-the-files)
  - [Things you can ask the bot](#things-you-can-ask-the-bot)
  - [Handoff](#handoff)
    - [Try it out](#try-it-out)
    - [How it works](#how-it-works)
    - [Bot-side configuration](#bot-side-configuration)
  - [Testing the bot](#testing-the-bot)
  - [Rasa X Deployment](#rasa-x-deployment)
  - [Action Server Image](#action-server-image)
- [CI/CD](#cicd)
  - [Summary](#summary)
  - [GitHub Secrets](#github-secrets)
      - [AWS IAM User API Keys:](#aws-iam-user-api-keys)
      - [AWS Elastic IP:](#aws-elastic-ip)
      - [Rasa Enterprise License:](#rasa-enterprise-license)
      - [Helm chart Credentials](#helm-chart-credentials)
  - [AWS Preparation](#aws-preparation)
    - [IAM User API Keys](#iam-user-api-keys)
    - [SSH Key Pair](#ssh-key-pair)
    - [Local AWS CLI](#local-aws-cli)
      - [Install AWS CLI v2](#install-aws-cli-v2)
      - [Configure your AWS CLI](#configure-your-aws-cli)
    - [ECR repository & S3 bucket](#ecr-repository--s3-bucket)
  - [EKS production cluster](#eks-production-cluster)
    - [Preparation](#preparation)
      - [Install eksctl](#install-eksctl)
      - [Install kubectl](#install-kubectl)
      - [Install helm](#install-helm)
      - [Install jp](#install-jp)
      - [Set environment variables](#set-environment-variables)
    - [Create the EKS cluster](#create-the-eks-cluster)
    - [Configure `kubeconfig`](#configure-kubeconfig)
    - [Install/Upgrade Rasa Enterprise](#installupgrade-rasa-enterprise)
      - [Build & push action server docker image](#build--push-action-server-docker-image)
      - [Install/Upgrade Rasa Enterprise](#installupgrade-rasa-enterprise-1)
    - [Train, test & upload model to S3](#train-test--upload-model-to-s3)
    - [Deploy, Tag & Smoketest the trained model](#deploy-tag--smoketest-the-trained-model)
    - [DNS](#dns)
  - [Appendix A: The AWS EKS cluster](#appendix-a-the-aws-eks-cluster)
  - [Appendix B: Manual Cleanup of AWS resources](#appendix-b-manual-cleanup-of-aws-resources)
  - [Appendix C: OCTANT](#appendix-c-octant)
    - [Install Octant](#install-octant)
      - [Install on Ubuntu](#install-on-ubuntu)
    - [Run Octant](#run-octant)
  - [Appendix D: AWS EKS references](#appendix-d-aws-eks-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Install dependencies

Run:
```bash
pip install -r requirements.txt
```

To install development dependencies:

```bash
pip install -r requirements-dev.txt
pre-commit install
python -m spacy download en_core_web_md en
python -m spacy link en_core_web_md en
```

> With pre-commit installed, the `black` and `doctoc` hooks will run on every `git commit`.
> If any changes are made by the hooks, you will need to re-add changed files and re-commit your changes.

## Run the bot

Use `rasa train` to train a model.

Then, to run, first set up your action server in one terminal window, listening on port 5056:
```bash
rasa run actions --port 5056
```

Note that port 5056 is used for the action server, to avoid a conflict when you also run the helpdesk bot as described below in the `handoff` section.

In another window, run the duckling server (for entity extraction):

```bash
docker run -p 8000:8000 rasa/duckling
```

Then to talk to the bot, run:
```
rasa shell --debug
```

Note that `--debug` mode will produce a lot of output meant to help you understand how the bot is working
under the hood. To simply talk to the bot, you can remove this flag.


You can also try out your bot locally using Rasa X by running
```
rasa x
```

Refer to our guided workflow in the [Wiki page](https://github.com/RasaHQ/financial-demo/wiki/Using-Rasa-X-with-the-Financial-Demo) for how to get started with Rasa X in local mode.


## Overview of the files

`data/nlu/nlu.yml` - contains NLU training data

`data/nlu/rules.yml` - contains rules training data

`data/stories/stories*.yml` - contains stories training data

`actions.py` - contains custom action/api code

`domain.yml` - the domain file, including bot response templates

`config.yml` - training configurations for the NLU pipeline and policy ensemble

`tests/` - end-to-end tests


## Things you can ask the bot

The bot currently has five skills. You can ask it to:
1. Transfer money to another person
2. Check your earning or spending history (with a specific vendor or overall)
3. Answer a question about transfer charges
4. Pay a credit card bill
5. Tell you your account balance

It also has a limited ability to switch skills mid-transaction and then return to the transaction at hand.

For the purposes of illustration, the bot recognises the following fictional credit card accounts:

- `emblem`
- `justice bank`
- `credit all`
- `iron bank`

It recognises the following payment amounts (besides actual currency amounts):

- `minimum balance`
- `current balance`

It recognises the following vendors (for spending history):

- `Starbucks`
- `Amazon`
- `Target`

You can change any of these by modifying `actions.py` and the corresponding NLU data.

If configured, the bot can also hand off to another bot in response to the user asking for handoff. More [details on handoff](#handoff) below.

## Handoff

This bot includes a simple skill for handing off the conversation to another bot or a human.
This demo relies on [this fork of chatroom](https://github.com/RasaHQ/chatroom) to work, however you
could implement similar behaviour in another channel and then use that instead. See the chatroom README for
more details on channel-side configuration.


Using the default set up, the handoff skill enables this kind of conversation with two bots:

<img src="./handoff.gif" width="200">


### Try it out

The simplest way to use the handoff feature is to do the following:

1. Clone [chatroom](https://github.com/RasaHQ/chatroom) and [Helpdesk-Assistant](https://github.com/RasaHQ/helpdesk-assistant) alongside this repo
2. In the chatroom repo, install the dependencies:
```bash
yarn install
```
3. In the chatroom repo, build and serve chatroom:
```bash
yarn build
yarn serve
```
4. In the Helpdesk-Assistant repo, install the dependencies and train a model (see the Helpdesk-Assistant README)
5. In the Helpdesk-Assistant repo, run the rasa server and action server at the default ports (shown here for clarity)
   In one terminal window:
    ```bash
    rasa run --enable-api --cors "*" --port 5005 --debug
    ```
    In another terminal window:
    ```bash
    rasa run actions --port 5055 --debug
    ```
6. In the Financial-Demo repo (i.e. this repo), run the rasa server and action server at **the non-default ports shown below**
   In one terminal window:
    ```bash
    rasa run --enable-api --cors "*" --port 5006 --debug
    ```
    In another terminal window:
    ```bash
    rasa run actions --port 5056 --debug
    ```
7. Open `chatroom_handoff.html` in a browser to see handoff in action


### How it works

Using chatroom, the general approach is as follows:

1. User asks original bot for a handoff.
2. The original bot handles the request and eventually
   sends a message with the following custom json payload:
    ```
        {
            "handoff_host": "<url of handoff host endpoint>",
            "title": "<title for bot/channel handed off to>"
            }
    ```
    This message is not displayed in the Chatroom window.
3. Chatroom switches the host to the specified `handoff_host`
4. The original bot no longer receives any messages.
5. The handoff host receives the message `/handoff{"from_host":"<original bot url">}`
6. The handoff host should be configured to respond to this message with something like,
   "Hi, I'm <so and so>, how can I help you??"
7. The handoff host can send a message in the same format as specified above to hand back to the original bot.
   In this case the same pattern repeats, but with
   the roles reversed. It could also hand off to yet another bot/human.

### Bot-side configuration

The "try it out" section doesn't require any further configuration; this section is for those
who want to change or further understand the set up.

For this demo, the user can ask for a human, but they'll be offered a bot (or bots) instead,
so that the conversation looks like this:


For handoff to work, you need at least one "handoff_host". You can specify any number of handoff hosts in the file `actions/handoff_config.yml`.
```
handoff_hosts:
    helpdesk_assistant:
      title: "Helpdesk Assistant"
      url: "http://localhost:5005"
    ## you can add more handoff hosts to this list e.g.
    # moodbot:
    #   title: "MoodBot"
    #   url: "http://localhost:5007"
```

Handoff hosts can be other locally running rasa bots, or anything that serves responses in the format that chatroom
accepts. If a handoff host is not a rasa bot, you will of course want to update the response text to tell the user
who/what they are being handed off to.

The [Helpdesk-Assistant](https://github.com/RasaHQ/helpdesk-assistant) bot has been set up to handle handoff in exactly the same way as Helpdesk-Assistant,
so the simplest way to see handoff in action is to clone Financial-Demo alongside this repo.

If you list other locally running bots as handoff hosts, make sure the ports on which the various rasa servers & action servers are running do not conflict with each other.


## Testing the bot

You can test the bot on the test conversations by:

- start duckling
- running  `rasa test`.

This will run [end-to-end testing](https://rasa.com/docs/rasa/user-guide/testing-your-assistant/#end-to-end-testing) on the conversations in `tests/test_stories.yml`.

All tests must pass.



## Rasa X Deployment

To [deploy financial-demo](https://rasa.com/docs/rasa/user-guide/how-to-deploy/), it is highly recommended to make use of the [one line deploy script](https://rasa.com/docs/rasa-x/installation-and-setup/one-line-deploy-script/) for Rasa X. 

As part of the deployment, you'll need to set up [git integration](https://rasa.com/docs/rasa-x/installation-and-setup/integrated-version-control/#connect-your-rasa-x-server-to-a-git-repository) to pull in your data and configurations, and build or pull an action server image.


## Action Server Image

You will need to have docker installed in order to build the action server image. If you haven't made any changes to the action code, you can also use the [public image on Dockerhub](https://hub.docker.com/r/rasa/financial-demo) instead of building it yourself.

To build & tag the image, run:

```bash
export ACTION_SERVER_DOCKERPATH=<dockerID>/<name-of-image>:<tag-of-image>
make docker-build
```

Run the action server container:

```bash
make docker-run
```

Perform a smoke test on the health endpoint:

```bash
make docker-test
```

Once you have confirmed that the container is working, push the container image to a registry:

```bash
# login to a container registry with your credentials
docker login  

# check the registry logged into
docker system info | grep Registry

# push the action server image
make docker-push
```

# CI/CD

## Summary

As explained in the [Setting up CI/CD](https://rasa.com/docs/rasa/setting-up-ci-cd) section of the Rasa documentation, Continous Integration (**CI**) is the practice of merging in code changes frequently and automatically testing changes as they are committed. Continuous Deployment (**CD**) means automatically deploying integrated changes to a staging or production environment. Together, they allow you to make more frequent improvements to your assistant and efficiently test and deploy those changes.

A CI/CD pipeline is used to test, build and deploy the financial-demo bot to AWS EKS.

The pipeline uses GitHub Actions, defined in  `.github/workflows/cicd.yml`. It includes these jobs:

![](images/cicd.png)

**[params](https://github.com/RasaHQ/financial-demo/blob/d40467b4fb2a7d4fb072b86a2828a8cec662eb63/.github/workflows/cicd.yml#L26)**

- Defines parameters for use by downstream jobs

**[params_summary](https://github.com/RasaHQ/financial-demo/blob/d40467b4fb2a7d4fb072b86a2828a8cec662eb63/.github/workflows/cicd.yml#L125)**

- Prints the value of the parameters.

**[action_server](https://github.com/RasaHQ/financial-demo/blob/d40467b4fb2a7d4fb072b86a2828a8cec662eb63/.github/workflows/cicd.yml#L156)**

- Builds & Tests the docker image of the action server with tag: `<branch-name>`
- Uploads the docker image to the AWS ECR repository: `financial-demo`

**[rasa_model](https://github.com/RasaHQ/financial-demo/blob/d40467b4fb2a7d4fb072b86a2828a8cec662eb63/.github/workflows/cicd.yml#L203)**

- Trains & Tests the rasa model with name: `models/<branch-name>.tar.gz
- Uploads the trained model to the AWS S3 bucket: `rasa-financial-demo` 

**[aws_eks_create_test_cluster](https://github.com/RasaHQ/financial-demo/blob/d40467b4fb2a7d4fb072b86a2828a8cec662eb63/.github/workflows/cicd.yml#L242)**

- If not existing yet, creates an AWS EKS cluster with name: `financial-demo-<branch-name>`

**[deploy_to_test_cluster](https://github.com/RasaHQ/financial-demo/blob/d40467b4fb2a7d4fb072b86a2828a8cec662eb63/.github/workflows/cicd.yml#L266)**

- Installs/Updates Rasa Enterprise, with the docker image created by the **action_server** job.
- Deploys the rasa model, trained by the **rasa_model** job.
- Performs smoke tests to ensure basic operations are all OK.

**[deploy_to_prod_cluster](https://github.com/RasaHQ/financial-demo/blob/d40467b4fb2a7d4fb072b86a2828a8cec662eb63/.github/workflows/cicd.yml#L353)**

- Runs when pushing to the `main` branch, and all previous steps are successful.
- Installs/Updates Rasa Enterprise, with the docker image created by the **action_server** job.
- Deploys the rasa model, trained by the **rasa_model** job.
- Performs smoke tests to ensure basic operations are all OK.



## GitHub Secrets

Secrets can be added to your GitHub repository by going to `Settings > Secrets` and selecting `New repository secret`. 

When entering values, be sure to omit quotes.

#### AWS IAM User API Keys:

To configure the aws cli in Github Actions, create IAM User API Keys as described below, and add them as GitHub secrets to the repository:

- AWS_ACCESS_KEY_ID = `Access key ID`
- AWS_SECRET_ACCESS_KEY = `Secret access key` 

#### AWS Elastic IP:

Create an Elastic IP as described below, and add it as a GitHub Secret to the repo:

- AWS_ELASTIC_IP = `PublicIp`

#### Rasa Enterprise License:

To define a pull secret in Github Actions for the private GCR repo, you'll need to retrieve the private values from your Rasa Enterprise license file ([docs](https://rasa.com/docs/rasa-x/installation-and-setup/install/helm-chart#5-configure-rasa-x-image)) and add them as GitHub secrets to the repository:

- GCR_AUTH_JSON_PRIVATE_KEY_ID = `private_key_id`
- GCR_AUTH_JSON_PRIVATE_KEY = `private_key`
- GCR_AUTH_JSON_CLIENT_EMAIL = `client_email`
- GCR_AUTH_JSON_CLIENT_ID = `client_id`

An alternative approach to GCR repo authentication would be with the [gcloud credential helper](https://cloud.google.com/container-registry/docs/advanced-authentication#gcloud-helper).

#### Helm chart Credentials

To use safe_credentials in Github Actions through `values.yml` ([docs](https://rasa.com/docs/rasa-x/installation-and-setup/install/helm-chart#3-configure-credentials)), add following GitHub Secrets to the repo, replacing each `<safe credential>` with a different alphanumeric string and choosing a `<username>` for the initial user. 

*(Please use **safe credentials** to avoid data breaches)*

- GLOBAL_POSTGRESQL_POSTGRESQLPASSWORD = `<safe credential>`
- GLOBAL_REDIS_PASSWORD = `<safe credential>`
- RABBITMQ_RABBITMQ_PASSWORD = `<safe credential>`
- RASAX_INITIALUSER_USERNAME = `<username>`
- RASAX_INITIALUSER_PASSWORD = `<safe credential>`
- RASAX_JWTSECRET = `<safe credential>`
- RASAX_PASSWORDSALT = `<safe credential>`
- GLOBAL_POSTGRESQL_POSTGRESQLPASSWORD = `<safe credential>`
- GLOBAL_POSTGRESQL_POSTGRESQLPASSWORD = `<safe credential>`



## AWS Preparation

The CI/CD pipeline of financial-demo uses AWS for all the storage & compute resources.

After cloning or forking the financial-demo GitHub repository you must set up the following items before the pipeline can run.

### IAM User API Keys

The CI/CD pipeline uses the [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html#cliv2-linux-install).

The [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html#cliv2-linux-install) needs a set of IAM User API keys for authentication & authorization:

In your AWS Console, go to the IAM dashboard to create a new set of API keys:

  - Click on Users

  - Click on Add user

    - User name = findemo  *(The actual name is not important, we will never use this name directly)*

      Choose "**programmatic access**." This allows you to use the aws cli to interact with AWS.

    - Click on Next: Permissions

      - Click on *Attach existing policies directly*

        For IAM access, you can choose “**AdministratorAccess**”, or limit access to only what is needed by the CD pipeline.

    - Click on Next: Tags

    - Click on Next: Review

    - Click on Create user

    - Store in a safe location: `Access key ID` & `Secret access key`


### SSH Key Pair

To SSH into the EC2 worker nodes of the EKS cluster, you'll need an SSH Key Pair

- In your AWS Console, go to **EC2 > Key Pairs**, and create a Key Pair with the name `findemo`, and download the file `findemo.pem` which contains the private SSH key. 
  **Note that the name `findemo` is important, since it is used by the CI/CD pipeline when the cluster is created.**

### Local AWS CLI

Before the CI/CD pipeline can run, you will use the AWS CLI locally to create some resources and need to install & configure the CLI locally.

#### Install AWS CLI v2

See the [installation instructions](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html).

#### Configure your AWS CLI

```bash
# AWS CLI version 2.1.26 or later
aws --version

# Configure AWS CLI
aws configure
AWS Access Key ID [None]: -----          # See above: IAM User API Keys
AWS Secret Access Key [None]: -------    # See above: IAM User API Keys
Default region name [None]: us-west-2    # The CI/CD pipeline uses us-west-2 
Default output format [None]: 

# Check your configuration
aws configure list [--profile profile-name]

# verify it works
aws s3 ls
```

### ECR repository & S3 bucket

The CI pipeline creates two artifacts:

- An action server docker **image**, which is pushed to an **AWS ECR** repository.
- A trained rasa **model**, which is copied to an **AWS S3** bucket

Run these commands to create the storage for these artifacts. These commands run the AWS CLI and create an ECR repository and an S3 bucket:

```bash
# create ECR repository with name `financial-demo`
make aws-ecr-create-repository

# create S3 bucket with name `rasa-financial-demo`
make aws-s3-create-bucket
```



## EKS production cluster

If the production cluster is already set up, you can skip this section.

This section describes the initial deployment of the financial-demo bot on an EKS production cluster. 

This initial deployment is done manually. After that, the deployment is maintained & upgraded automatically by the CI/CD pipeline.

### Preparation

Before you can create the EKS cluster, you must install  `eksctl`, `kubectl`, `helm`, `jp`, and define some environment variables.

#### Install eksctl

See the [installation instructions](https://docs.aws.amazon.com/eks/latest/userguide/eksctl.html)

If you use Ubuntu, you can issue the command:

```bash
make install-eksctl
```

#### Install kubectl

See the [installation instructions](https://kubernetes.io/docs/tasks/tools/#kubectl)

If you use Ubuntu, you can issue the command:

```bash
make install-kubectl
```

#### Install helm

See the [installation instructions](https://helm.sh/docs/intro/install/)

If you use Ubuntu, you can issue the command:

```bash
make install-helm
```

#### Install jp

See the [installation instructions](https://github.com/jmespath/jp#installing)

If you use Ubuntu, you can issue the command:

```bash
make install-jp
```

#### Set environment variables

There are many ways to set the required environment variables in your local environment. 

One way is to create a file  `./secret/envs_export`, with this content:

```bash
# source this file to set the environment variables the same as the GitHub secrets.
export GCR_AUTH_JSON_PRIVATE_KEY_ID=...
export GCR_AUTH_JSON_PRIVATE_KEY='-----BEGIN PRIVATE KEY-...-END PRIVATE KEY-----\n'
export GCR_AUTH_JSON_CLIENT_EMAIL='...'
export GCR_AUTH_JSON_CLIENT_ID=...
export GLOBAL_POSTGRESQL_POSTGRESQLPASSWORD=...
export GLOBAL_REDIS_PASSWORD=...
export RABBITMQ_RABBITMQ_PASSWORD=...
export RASAX_INITIALUSER_USERNAME=admin
export RASAX_INITIALUSER_PASSWORD=...
export RASAX_JWTSECRET=...
export RASAX_PASSWORDSALT=...
export RASAX_TOKEN=...
export RASA_TOKEN=...
export AWS_ELASTIC_IP=...
```

Then, create the environment variables with the command:

```bash
source ./secret/envs_export
```

### Create the EKS cluster

Create the EKS production cluster, with name `financial-demo-<current branch name>`:

```bash
make aws-eks-cluster-create AWS_EKS_CLUSTER_NAME=financial-demo-production
```

Some other useful 'Makefile functions' to interact with the EKS cluster:

```bash
make aws-eks-cluster-list-all
make aws-eks-cluster-describe AWS_EKS_CLUSTER_NAME=financial-demo-production
make aws-eks-cluster-describe-stacks AWS_EKS_CLUSTER_NAME=financial-demo-production
make aws-eks-cluster-delete AWS_EKS_CLUSTER_NAME=financial-demo-production
```

### Configure `kubeconfig`

Add the EKS  cluster information to `~/.kube/config`, and set the `current-context` to that cluster:

```bash
make aws-eks-cluster-update-kubeconfig AWS_EKS_CLUSTER_NAME=financial-demo-production

# make sure kubectl is now looking at the correct EKS cluster
make kubectl-config-current-context
```

### Install/Upgrade Rasa Enterprise

#### Build & push action server docker image

Build, run, test & push the action docker server image, with name:

- `<ECR URI>/financial-demo:<current branch name>`

```bash
# Verify that the correct rasa-sdk is selected in `Dockerfile`
# ==> FROM rasa/rasa-sdk:....
#
# Then, build the image with:
make docker-build

make docker-run
make docker-test
make docker-stop

# Login & push the docker image to the AWS ECR repository
make aws-ecr-docker-login
make docker-push
```

#### Install/Upgrade Rasa Enterprise

Install/Upgrade Rasa Enterprise, using the action server docker image that was uploaded to the ECR repository:

```bash
# make sure kubectl is looking at the correct EKS cluster
# -> if not, configure kubeconfig as described above
make kubectl-config-current-context  AWS_EKS_CLUSTER_NAME=financial-demo-production

# create namespace `my-namespace`
make aws-eks-namespace-create

# create/refresh gcr-pull-secret, for Rasa Enterprise image
make pull-secret-gcr-create

# create/refresh ecr-pull-secret, for action server image
make pull-secret-ecr-create

# Verify that:
#
# the correct Rasa Enterprise version is selected in `Makefile`
# ==> RASAX_TAG := ......
# 
# the correct rasa version is selected in `requirements.txt`
# ==> rasa[spacy]==....
#
# Install/Upgrade Rasa Enterprise with the action server
make rasa-enterprise-install

# Check Rasa Enterprise Health
make rasa-enterprise-check-health

# To troubleshoot, highly recommended to use OCTANT, see Appendix C
```

### Train, test & upload model to S3

```bash
# Train the model: `models/<current branch>.tar.gz`
make rasa-train

# In another window, start duckling server
docker run -p 8000:8000 rasa/duckling

# Run the end-to-end tests
make rasa-test

# Upload `models/<current branch>.tar.gz` to S3
# Note: This does not mean the model is deployed to Rasa Enterprise,
#       which is done in the next step.
make aws-s3-upload-rasa-model
```

### Deploy, Tag & Smoketest the trained model

```bash
# Configure ~/.kube/config and set current_context
make aws-eks-cluster-update-kubeconfig  AWS_EKS_CLUSTER_NAME=financial-demo-production

# Deploy rasa model
make aws-s3-download-rasa-model
make rasa-enterprise-model-delete
make rasa-enterprise-model-upload
make rasa-enterprise-model-tag

# Wait about 1 minute, so rasa-production can download, upack & load the model
# Smoketest
make rasa-enterprise-smoketest
```

### DNS

Optionally, if you want to access Rasa Enterprise at your own (sub)-domain name, define a DNS record of type CNAME with your domain service provider:

- **name of sub-domain**:  `aws-financial-demo`  

  *==> This example name will resolve to `aws-financial-demo.my-domain.com`*

- **Type**: `CNAME`

- **Content**: `--------.us-west-2.elb.amazonaws.com` 

  *==> This is the hostname of the External Application Load Balancer that AWS EKS created during the deployment. You can get this hostname with the command:*

  ```bash
  make rasa-enterprise-get-loadbalancer-hostname
  ```

- **TTL (Time to Live)**: 1 Hour

- **Priority**: 

It might take some time for things to propagate, but you can verify it with commands like nslookup & dig:

```bash
########################################################################
# use `nslookup -type`
nslookup -type=CNAME aws-financial-demo.my-domain.com
aws-financial-demo.my-domain.com canonical name = ---.us-west-2.elb.amazonaws.com.

########################################################################
# use `dig`
dig CNAME aws-financial-demo.my-domain.com
...
;; ANSWER SECTION:
aws-financial-demo.my-domain.com. ---- IN CNAME ---.us-west-2.elb.amazonaws.com.

```

Once propagated, you can access Rasa Enterprise at **http://aws-financial-demo.my-domain.com**



## Appendix A: The AWS EKS cluster

We use *eksctl* to create the clusters. It creates many AWS resources with CloudFormation templates. 

Some of these AWS resources are:

- A VPC with
  - Public & private subnets
  - Internet & NAT Gateways
  - Route Tables
- An IAM EKS service role
- An EKS Cluster Control Plane
- An EKS Managed nodegroup of EC2 instances

The cluster context is also added to the `~/.kube/config` file.

The VPC created looks something like this:

![](images/financial-demo-eks-test-vpc.png)

The EKS Control Plane interacts with the the EKS Data Plane (the nodes), like this:

![img](https://d2908q01vomqb2.cloudfront.net/fe2ef495a1152561572949784c16bf23abb28057/2020/04/10/subnet_pubpri.png)



## Appendix B: Manual Cleanup of AWS resources

Sometimes things do not clean up properly and you will need to do a manual cleanup in the **AWS console**:

**CloudFormation**: Try to delete all the stacks in reverse order as they were created by the eksctl command.

When a stack fails to delete due to dependencies, you have two options:

  - Select to retain the resources that have dependency errors. (**NOT RECOMMENDED**)

    The stack delete operation will simply skip deleting them. This is NOT recommended, because you will clutter up your AWS account with many unused resources.

  - Manually delete the resources that the stack is not able to delete. (**RECOMMENDED**)

    You can do this by drilling down into the **CloudFormation stack delete events** messages and deleting items bottom-up the dependency tree.

    One example of a bottom-up delete sequence is when deletion of the VPC fails:

    - **EC2 > Load Balancers**: first, delete the ELB load balancers
    - **VPC > Subnets**: then, delete the subnets 
      - This will also delete the EC2 > Network interfaces, named `eni-xxxx`
      - You cannot delete Subnets until the ELB load balancers are deleted
    - **VPC > Your VPCs**: finally, delete the VPC 
      - This will also delete all associated:
        - security groups (`sg-xxx`)
        - internet gateways (`igw-xxx`)
        - subnets (`subnet-xxx`)

  - After cleaning up, try again to delete the **AWS CloudFormation** stack.

  - If it still does not delete, iterate the manual cleanups until it does.

    Again, this can be a painful process, but once the CloudFormation stacks delete properly without retaining/skipping anything, you are guaranteed that you have cleaned up all the resources created by the CI/CD pipeline.

## Appendix C: OCTANT

[Octant](https://octant.dev/) is a useful open sourced tool for visualizing workloads inside the cluster and troubleshooting issues when they arise.

### Install Octant

[Installation instructions](https://github.com/vmware-tanzu/octant#installation)

#### Install on Ubuntu

```bash
cd ~
mkdir octant
cd octant
wget https://github.com/vmware-tanzu/octant/releases/download/v0.20.0/octant_0.20.0_Linux-64bit.deb
sudo dpkg -i octant_0.20.0_Linux-64bit.deb
```

### Run Octant

```bash
# #################################################### #
# Configure kubectl to look at the correct EKS cluster #
# #################################################### #

# -> for a feature branch test cluster
git checkout my-feature-branch

# -> for the production cluster
git branch production # create temporary, local `production` branch
git checkout production

# Configure kubeconfig for the correct EKS cluster
make aws-eks-cluster-update-kubeconfig

# make sure kubectl is now looking at the correct EKS cluster
make kubectl-config-current-context

# #################################################### #
# Run Octant on default port 7777 and open the browser #
# #################################################### #
OCTANT_LISTENER_ADDR=0.0.0.0:7777 octant &

# Within octant, select the namespace `my-namespace`
```

## Appendix D: AWS EKS references

There are two commands to create AWS EKS clusters;  `eksctl` & `aws eks`.  

- The `eksctl` cli is the most complete, and it is what we ended up using.

- The `aws eks` cli does not support to launch worker nodes to the cluster control plane. This has to be done manually from the AWS Console, which makes it unsuited for a CI/CD pipeline where everything needs to be done via scripting (=> infrastructure as code).

The following references are useful for learning about AWS EKS, and it is highly recommended to manually build test-clusters with both the `eksctl` & `aws eks` commands to help demystify the AWS resources that are being generated:

- [eksctl – the EKS CLI](https://aws.amazon.com/blogs/opensource/eksctl-eks-cli/)
- [Getting started with Amazon EKS - eksctl](https://docs.aws.amazon.com/eks/latest/userguide/getting-started-eksctl.html)
- [Blog: EKS Cluster with One Command](https://aws.amazon.com/blogs/opensource/eksctl-eks-cluster-one-command/)
- [Blog: Demystifying cluster networking for EKS worker nodes](https://aws.amazon.com/blogs/containers/de-mystifying-cluster-networking-for-amazon-eks-worker-nodes/)
- https://docs.aws.amazon.com/eks/latest/userguide/create-public-private-vpc.html
- https://docs.aws.amazon.com/eks/latest/userguide/eks-compute.html
- https://logz.io/blog/amazon-eks-cluster/amp/
- https://www.eksworkshop.com/
- [aws eks - Command Reference](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/eks/index.html)  (Not used)
