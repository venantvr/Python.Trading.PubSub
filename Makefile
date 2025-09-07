.PHONY: help test clean format lint typecheck check install

PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)
PIP := $(if $(wildcard .venv/bin/pip),.venv/bin/pip,pip3)
SOURCES := core business

# Default target
help:
	@echo "Available targets:"
	@echo "  test      Run tests"
	@echo "  format    Format code with black and isort"
	@echo "  lint      Run code linting with flake8"
	@echo "  typecheck Run type checking with mypy"
	@echo "  check     Run format, lint, typecheck and tests"
	@echo "  clean     Clean up generated files"
	@echo "  install   Install dependencies"
	@echo "  update    Update dependencies"

# Testing
test:
	$(PYTHON) -m pytest tests/ -v --tb=short

# Code formatting
format:
	$(PYTHON) -m black $(SOURCES) tests/
	$(PYTHON) -m isort $(SOURCES) tests/

# Linting
lint:
	$(PYTHON) -m flake8 $(SOURCES) tests/

# Type checking
typecheck:
	$(PYTHON) -m mypy $(SOURCES)

# Combined check
check: format lint typecheck test

# Installation
install:
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

# Updates
update:
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) install --upgrade -r requirements-dev.txt

# Clean up
clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache/ .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
