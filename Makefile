all: test

.PHONY: test test-unit test-integration test-coverage lint format

test:
	pytest

test-unit:
	pytest -v tests/unit

test-integration:
	pytest -v tests/integration

test-coverage:
	pytest --cov=src --cov-report=term-missing --cov-report=xml --cov-report=html tests/

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

run:
	uvicorn src.api_layer.core.app:app --reload