.PHONY: help install install-dev test lint format clean build upload

help:
	@echo "Available commands:"
	@echo "  make install      Install the package"
	@echo "  make install-dev  Install with development dependencies"
	@echo "  make test         Run tests"
	@echo "  make lint         Run linting"
	@echo "  make format       Format code"
	@echo "  make clean        Clean build artifacts"
	@echo "  make build        Build distribution packages"
	@echo "  make upload       Upload to PyPI (requires credentials)"

install:
	pip install -e .
	playwright install chromium

install-dev:
	pip install -e ".[dev]"
	playwright install chromium
	pre-commit install

test:
	pytest

test-cov:
	pytest --cov=snapwright --cov-report=html --cov-report=term

lint:
	black --check src tests
	flake8 src tests
	mypy src

format:
	black src tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload: build
	python -m twine upload dist/*

# Development helpers
run-examples:
	python examples/basic_usage.py
	python examples/data_extraction.py
	python examples/advanced_usage.py

check: lint test
	@echo "All checks passed!"