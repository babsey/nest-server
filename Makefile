PYTHON_VERSIONS := 3.10 3.11 3.12 3.13 3.14
TEST_PY_TARGETS := $(addprefix test-py,$(PYTHON_VERSIONS))

.PHONY: sync test test-cov lint format clean test-all

sync:
	uv sync

test:
	uv run --env-file .env pytest

test-cov:
	uv run --env-file .env pytest -v --cov=./src/nest_server

lint:
	uv run ruff check .

format:
	uv run ruff format --check .

clean:
	rm -rf .venv .venv-* dist *.egg-info .pytest_cache .mypy_cache .ruff_cache .coverage

test-all: $(TEST_PY_TARGETS)

test-py%:
	UV_PROJECT_ENVIRONMENT=.venv-$* uv run --python $* --env-file .env pytest
