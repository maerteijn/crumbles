.PHONY: clean versions install lint test cov format dist publish-release-pypi-test publish_release-pypi

default: clean install

clean:
	find . -name '__pycache__' -exec rm -rf {} +
	rm -Rf build/

versions:
	pip-compile --extra dev --no-emit-index-url --upgrade -o requirements-dev.txt pyproject.toml

install:
	pip install -r requirements-dev.txt -e .[dist]

lint:
	ruff check src tests
	mypy .

test:
	pytest

cov:
	pytest --cov=crumbles --cov-report=html --cov-report=term

format:
	ruff check src tests --fix
	ruff format

dist:
	pyproject-build .

publish-release-pypi-test: dist
	twine upload --repository testpypi dist/*

publish_release-pypi: build_release
	twine upload dist/*

