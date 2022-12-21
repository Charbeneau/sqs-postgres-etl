ifeq (, $(shell which python))
	$(error "python was not found in $(PATH). For installation instructions go to https://www.python.org/downloads/.")
endif

ifeq (, $(shell which docker))
	$(error "docker was not found in $(PATH). For installation instructions go to https://docs.docker.com/get-docker/.")
endif

ifeq (, $(shell which docker-compose))
	$(error "docker-compose was not found in $(PATH). For installation instructions go to https://docs.docker.com/compose/install/.")
endif


.PHONY: dependencies
install:
	python -m ensurepip --upgrade && pip install -r requirements.txt

install-test:
	pip install -r test-requirements.txt

test:
	pytest

uninstall-all:
	pip freeze | xargs pip uninstall -y

lint:
	python -m black app

.PHONY: docker
start:
	docker-compose up -d

message:
	awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue

db:
	psql -d postgres -U postgres  -p 5432 -h localhost -W

run:
	python app/main.py

stop:
	docker-compose down --remove-orphans

clean:
	docker system prune --all --force --volumes
