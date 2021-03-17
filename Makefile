ACTION_SERVER_DOCKERPATH ?= financial-demo:test
ACTION_SERVER_DOCKERNAME ?= financial-demo
ACTION_SERVER_PORT ?= 5056
ACTION_SERVER_ENDPOINT_HEALTH ?= health

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
	@echo "		Builds docker image of the action server"
	@echo "	docker-run"
	@echo "		Runs the docker image of the action server created by `docker-build`"
	@echo "	docker-test"
	@echo "		Tests the health endpoint of the action server"
	@echo "	docker-clean-containers"
	@echo "		Stops & removes the containers created by `docker-run`"
	@echo "	docker-clean-images"
	@echo "		Removes the images created by `docker-build`"
	@echo "	docker-clean"
	@echo "		Runs `docker-clean-containers` and `docker-clean-images`"
	@echo "	docker-push"
	@echo "		Pushes docker images to dockerhub"

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f  {} +
	rm -rf build/
	rm -rf .pytype/
	rm -rf dist/
	rm -rf docs/_build

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
	docker build . --file Dockerfile --tag $(ACTION_SERVER_DOCKERPATH)
	
docker-run:
	docker run -d -p $(ACTION_SERVER_PORT):5055 --name $(ACTION_SERVER_DOCKERNAME) $(ACTION_SERVER_DOCKERPATH)
	
docker-test:
	curl http://localhost:$(ACTION_SERVER_PORT)/$(ACTION_SERVER_ENDPOINT_HEALTH)

docker-clean-containers:
	docker stop $(ACTION_SERVER_DOCKERNAME)
	docker rm $(ACTION_SERVER_DOCKERNAME)
	
docker-clean-images:
	docker rmi $(ACTION_SERVER_DOCKERPATH)

docker-clean: docker-clean-containers docker-clean-images
	
docker-push:
	docker image push $(ACTION_SERVER_DOCKERPATH)