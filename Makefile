# ClipMind-TUI Makefile

.PHONY: install test lint clean run help build

PYTHON := python3
PIP := pip3

help:
	@echo "ClipMind-TUI - Available targets:"
	@echo "  install    Install the package"
	@echo "  test       Run tests"
	@echo "  lint       Run linter"
	@echo "  clean      Clean build artifacts"
	@echo "  run        Run the TUI application"
	@echo "  build      Build distribution packages"

install:
	$(PIP) install -e .

test:
	$(PYTHON) -m pytest tests/ -v || echo "No tests directory yet"

lint:
	$(PYTHON) -m flake8 clipmind.py --max-line-length=120 || true
	$(PYTHON) -m pylint clipmind.py || true

clean:
	rm -rf build/ dist/ *.egg-info __pycache__ .pytest_cache
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete

run:
	$(PYTHON) clipmind.py

build:
	$(PYTHON) setup.py sdist bdist_wheel
