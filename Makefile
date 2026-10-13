PYTHON_VERSIONS := 3.10 3.11 3.12 3.13 3.14
TEST_PY_TARGETS := $(addprefix test-py,$(PYTHON_VERSIONS))

.PHONY: sync pre-commit test coverage lint format clean test-all

sync:
	uv sync

pre-commit:
	uv run pre-commit run --all-files

test:
	uv run --env-file .env.local pytest -v

coverage:
	uv run --env-file .env.local coverage run --source=./src/nest_server -m pytest
	uv run coverage report

lint:
	uv run ruff check .

format:
	uv run ruff format --check .

clean:
	rm -rf .pytest_cache .ruff_cache .venv .venv-* dist *.egg-info htmlcov .coverage

lock-upgrade:
	uv lock --upgrade && uv sync

test-all: $(TEST_PY_TARGETS)

test-py%:
	UV_PROJECT_ENVIRONMENT=.venv-$* uv run --python $* --env-file .env.local pytest
