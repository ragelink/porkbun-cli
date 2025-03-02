.PHONY: install install-dev clean format lint test coverage build publish help

help:
	@echo "Available commands:"
	@echo "  make install      Install package dependencies"
	@echo "  make install-dev  Install development dependencies"
	@echo "  make clean        Clean build artifacts"
	@echo "  make format       Format code with black and isort"
	@echo "  make lint         Run linting checks"
	@echo "  make test         Run tests"
	@echo "  make coverage     Run tests with coverage report"
	@echo "  make build        Build package distribution"
	@echo "  make publish      Publish package to PyPI"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

format:
	isort .
	black .

lint:
	ruff check .
	mypy porkbun
	black . --check
	isort . --check

test:
	pytest tests/

coverage:
	pytest --cov=porkbun tests/ --cov-report=term-missing

build: clean
	python setup.py sdist bdist_wheel

publish: build
	twine upload dist/* 