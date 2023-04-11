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

## Test python environment is setup correctly
test_env:
	$(PYTHON_INTERPRETER) test_environment.py

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