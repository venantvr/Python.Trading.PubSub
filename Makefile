.PHONY: help clean test coverage install dev-install format lint typecheck check docs build upload

PYTHON := python3
PIP := pip3
PROJECT_NAME := Python.Trading.PubSub
SOURCES := core business events

# Default target
help:
	@echo "Available targets:"
	@echo "  install        Install the package in production mode"
	@echo "  dev-install    Install the package in development mode with all dependencies"
	@echo "  test           Run tests"
	@echo "  coverage       Run tests with coverage report"
	@echo "  format         Format code using black and isort"
	@echo "  lint           Run linting checks"
	@echo "  typecheck      Run type checking with mypy"
	@echo "  check          Run all checks (format, lint, typecheck, test)"
	@echo "  docs           Build documentation"
	@echo "  build          Build distribution packages"
	@echo "  upload         Upload package to PyPI"
	@echo "  upload-test    Upload package to TestPyPI"
	@echo "  clean          Clean up generated files"
	@echo "  run-server     Run the PubSub server (if available)"

# Installation
install:
	$(PIP) install .

dev-install:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt
	$(PIP) install -e .
	pre-commit install

# Testing
test:
	$(PYTHON) -m pytest tests/ -v

coverage:
	$(PYTHON) -m pytest tests/ --cov=$(SOURCES) --cov-report=html --cov-report=term

test-watch:
	$(PYTHON) -m pytest tests/ -v --watch

# Code Quality
format:
	$(PYTHON) -m black $(SOURCES) tests/
	$(PYTHON) -m isort $(SOURCES) tests/

lint:
	$(PYTHON) -m flake8 $(SOURCES) tests/ --max-line-length=120 --extend-ignore=E203,W503
	$(PYTHON) -m pylint $(SOURCES)

typecheck:
	$(PYTHON) -m mypy $(SOURCES) --ignore-missing-imports

# Combined check
check: format lint typecheck test

# Documentation
docs:
	cd docs && $(MAKE) clean && $(MAKE) html
	@echo "Documentation built in docs/_build/html/"

serve-docs:
	cd docs/_build/html && $(PYTHON) -m http.server

# Build and Distribution
build: clean
	$(PYTHON) -m build

upload: build
	$(PYTHON) -m twine upload dist/*

upload-test: build
	$(PYTHON) -m twine upload --repository testpypi dist/*

# Development helpers
run-server:
	@echo "Starting PubSub server..."
	@if [ -f "server.py" ]; then \
		$(PYTHON) server.py; \
	else \
		echo "Server file not found. Please implement server.py first."; \
	fi

run-example:
	@echo "Running example client..."
	@if [ -f "examples/basic_usage.py" ]; then \
		$(PYTHON) examples/basic_usage.py; \
	else \
		echo "Example file not found. Creating basic example..."; \
		mkdir -p examples; \
		echo "from core.pubsub_client import PubSubClient" > examples/basic_usage.py; \
		echo "" >> examples/basic_usage.py; \
		echo "# Example usage" >> examples/basic_usage.py; \
		echo "if __name__ == '__main__':" >> examples/basic_usage.py; \
		echo "    client = PubSubClient('http://localhost:5000', 'example_client', ['test_topic'])" >> examples/basic_usage.py; \
		echo "    client.register_handler('test_topic', lambda msg: print(f'Received: {msg}'))" >> examples/basic_usage.py; \
		echo "    client.start()" >> examples/basic_usage.py; \
		$(PYTHON) examples/basic_usage.py; \
	fi

# Virtual environment management
venv:
	$(PYTHON) -m venv .venv
	@echo "Virtual environment created. Activate with: source .venv/bin/activate"

requirements:
	$(PIP) freeze > requirements-freeze.txt
	@echo "Requirements frozen to requirements-freeze.txt"

# Clean up
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*~" -delete

clean-all: clean
	rm -rf .venv/

# Development shortcuts
dev: dev-install
	@echo "Development environment ready!"

quick-test:
	$(PYTHON) -m pytest tests/ -x --ff -v

watch:
	find $(SOURCES) tests/ -name "*.py" | entr -c make quick-test

# Docker support (if needed in the future)
docker-build:
	docker build -t $(PROJECT_NAME) .

docker-run:
	docker run -it --rm -p 5000:5000 $(PROJECT_NAME)

# Performance testing
benchmark:
	$(PYTHON) -m pytest tests/performance/ -v --benchmark-only

profile:
	$(PYTHON) -m cProfile -o profile.stats examples/basic_usage.py
	$(PYTHON) -m pstats profile.stats

# Security checks
security:
	$(PIP) install safety bandit
	safety check
	bandit -r $(SOURCES)

# Dependency management
update-deps:
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --upgrade -r requirements.txt

check-deps:
	$(PIP) list --outdated
