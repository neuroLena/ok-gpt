#################################################################################
# GLOBALS                                                                       #
#################################################################################

PYTHON_INTERPRETER = python3
PIP = ./venv/bin/pip3 

#################################################################################
# COMMANDS                                                                      #
#################################################################################

env_base: requirements_base.txt
	$(PYTHON_INTERPRETER) -m venv venv
	$(PIP) install -U pip setuptools wheel
	$(PIP) install -r requirements_base.txt

freeze:
	$(PIP) freeze > requirements.txt

env: requirements.txt
	$(PYTHON_INTERPRETER) -m venv venv
	$(PIP) install -U pip setuptools wheel
	$(PIP) install -r requirements.txt

install: env
	mkdir -p logs
	# jupyter contrib nbextension install --user
	# jupyter nbextension enable toc2/main
	# jupyter nbextension enable collapsible_headings/main

## Test python environment is setup correctly
test_env:
	$(PYTHON_INTERPRETER) test_environment.py

## Run tests using pytest
test:
	pytest tests/

## Run service locally
run:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

format:
	black src
	isort src

lint:
	## pylint --disable=R,C,E1101,W0401,W0614,W0703 src
	flake8 src

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

## Remove python virtual environment
rm_env:
	rm -rf venv

#################################################################################
# PIPELINE COMMANDS                                                             #
#################################################################################

## Ingest raw input data, do some basic cleaning and preprocessing
raw_data:
	$(PYTHON_INTERPRETER) src/data/ingest_raw.py

## Split the input data into train, test sets
train_test_data:
	$(PYTHON_INTERPRETER) src/data/build_dataset.py

## Train model and save it 
# train_model:
# 	$(PYTHON_INTERPRETER) src/models/train_model.py

## Evaluate model performance on test data	
# test_model:
# 	$(PYTHON_INTERPRETER) src/models/test_model.py

## Reproduce the whole pipeline
pipeline: train_model test_model

#################################################################################
# PROJECT COMMANDS                                                              #
#################################################################################

IMAGE_TAG = "0.1.0"
IMAGE_NAME = "pessimistic-inner-spotter"
CONTAINER_NAME = "inference"

notebook:
	jupyter notebook --ip 0.0.0.0 --no-browser .

deploy:
	# git push heroku main

build_docker:
	docker build . -t ${IMAGE_NAME}:${IMAGE_TAG}

run_docker:
	docker run -p 8000:8000 \
		--name ${CONTAINER_NAME} \
		--rm ${IMAGE_NAME}:${IMAGE_TAG} 

stop_docker:
	docker stop ${CONTAINER_NAME}

## Deploy Docker container to AWS ECS
deploy_docker:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com