# see setup.cfg for additional config settings for tools like pytest and flake8

# install the service
.PHONY: install
install:
	pip install --no-cache-dir .

# install just the dependencies
.PHONY: install-deps
install-deps:
	pip install --no-cache-dir -e .

# install the development dependencies
.PHONY: install-dev
install-dev:
	pip install --no-cache-dir -e .[dev]

# run tests
.PHONY: test
test:
	pytest

# linting (pep8)
.PHONY: lint
lint:
	flake8
	cfn-lint cloudformation.template

# conform all files to pep8 -- MODIFIES FILES IN PLACE
.PHONY: autopep8
autopep8:
	autopep8 --in-place --recursive --aggressive src
