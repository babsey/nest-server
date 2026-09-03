PYTHON_VERSIONS := 3.10 3.11 3.12 3.13 3.14
TEST_PY_TARGETS := $(addprefix test-py,$(PYTHON_VERSIONS))

.PHONY: sync test coverage lint format clean test-all

sync:
	uv sync

test:
	uv run --env-file .env pytest -v

coverage:
	uv run --env-file .env coverage run --source=./src/nest_server -m pytest
	uv run coverage report

lint:
	uv run ruff check .

format:
	uv run ruff format --check .

clean:
	rm -rf .venv .venv-* dist *.egg-info .pytest_cache .mypy_cache .ruff_cache .coverage

test-all: $(TEST_PY_TARGETS)

test-py%:
	UV_PROJECT_ENVIRONMENT=.venv-$* uv run --python $* --env-file .env pytest
