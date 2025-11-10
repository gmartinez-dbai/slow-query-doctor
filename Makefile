# Makefile for slow-query-doctor

.PHONY: help setup sync-version check-version install test lint format clean hooks validate

# Default target
help:
	@echo "🚀 Slow Query Doctor - Development Commands"
	@echo ""
	@echo "⚠️  IMPORTANT: All commands require '.venv' directory in repo root!"
	@echo "   First time: bash scripts/setup-dev-environment.sh"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make validate     Check if environment is properly configured"
	@echo "  make setup        Install development dependencies and git hooks"
	@echo "  make hooks        Install git hooks only" 
	@echo "  make install      Install package in development mode"
	@echo ""
	@echo "Version Management:"
	@echo "  make sync-version Update all files to match VERSION file"
	@echo "  make check-version Verify all versions are consistent"
	@echo ""
	@echo "Dependency Management:"
	@echo "  make update-requirements  Regenerate requirements.txt from pyproject.toml"
	@echo ""
	@echo "Code Quality:"
	@echo "  make format       Format code with black"
	@echo "  make lint         Run linting (flake8, mypy)"
	@echo "  make test         Run tests with coverage"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        Remove build artifacts and cache"

# Setup development environment
setup: hooks install
	@if [ ! -d ".venv" ]; then \
		echo "❌ Virtual environment '.venv' not found!"; \
		echo "💡 Create it first: python -m venv .venv && source .venv/bin/activate"; \
		exit 1; \
	fi
	@echo "📦 Installing development dependencies..."
	@source .venv/bin/activate && pip install -r requirements.txt && pip install -e .[dev]
	@echo "✅ Development environment ready!"

# Install git hooks
hooks:
	@chmod +x scripts/setup-hooks.sh
	@bash scripts/setup-hooks.sh

# Install package in development mode
install:
	@if [ ! -d ".venv" ]; then \
		echo "❌ Virtual environment '.venv' not found!"; \
		echo "💡 Create it first: python -m venv .venv && source .venv/bin/activate"; \
		exit 1; \
	fi
	@source .venv/bin/activate && pip install -r requirements.txt && pip install -e .

# Version management
sync-version:
	@if [ ! -d ".venv" ]; then \
		echo "❌ Virtual environment '.venv' not found!"; \
		echo "💡 Create it first: python -m venv .venv && source .venv/bin/activate"; \
		exit 1; \
	fi
	@echo "🔄 Synchronizing versions..."
	@source .venv/bin/activate && pip install -r requirements.txt > /dev/null 2>&1 && python scripts/propagate_version.py

check-version:
	@if [ ! -d ".venv" ]; then \
		echo "❌ Virtual environment '.venv' not found!"; \
		echo "💡 Create it first: python -m venv .venv && source .venv/bin/activate"; \
		exit 1; \
	fi
	@echo "🔍 Checking version consistency..."
	@source .venv/bin/activate && pip install -r requirements.txt > /dev/null 2>&1 && python scripts/propagate_version.py --verify

# Dependency management
update-requirements:
	@if [ ! -d ".venv" ]; then \
		echo "❌ Virtual environment '.venv' not found!"; \
		echo "💡 Create it first: python -m venv .venv && source .venv/bin/activate"; \
		exit 1; \
	fi
	@echo "📦 Updating requirements.txt from pyproject.toml..."
	@source .venv/bin/activate && python scripts/update_requirements.py

# Code formatting
format:
	@if [ ! -d ".venv" ]; then \
		echo "❌ Virtual environment '.venv' not found!"; \
		exit 1; \
	fi
	@echo "🎨 Formatting code..."
	@source .venv/bin/activate && pip install -r requirements.txt > /dev/null 2>&1 && python -m black slowquerydoctor tests scripts
	@echo "✅ Code formatted!"

# Linting
lint:
	@if [ ! -d ".venv" ]; then \
		echo "❌ Virtual environment '.venv' not found!"; \
		exit 1; \
	fi
	@echo "🔍 Running linting..."
	@source .venv/bin/activate && pip install -r requirements.txt > /dev/null 2>&1 && python -m flake8 slowquerydoctor tests --max-line-length=88 --extend-ignore=E203,W503
	@source .venv/bin/activate && python -m mypy slowquerydoctor --ignore-missing-imports
	@echo "✅ Linting passed!"

# Run tests
test:
	@if [ ! -d ".venv" ]; then \
		echo "❌ Virtual environment '.venv' not found!"; \
		exit 1; \
	fi
	@echo "🧪 Running tests..."
	@source .venv/bin/activate && pip install -r requirements.txt > /dev/null 2>&1 && python -m pytest tests/ --cov=slowquerydoctor --cov-report=term-missing --cov-report=html
	@echo "✅ Tests completed!"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning up..."
	@rm -rf build/ dist/ *.egg-info/
	@rm -rf .pytest_cache/ .coverage htmlcov/
	@find . -name "*.pyc" -delete
	@find . -name "__pycache__" -delete
	@echo "✅ Cleaned up!"

# Validate environment setup
validate:
	@chmod +x scripts/validate-environment.sh
	@bash scripts/validate-environment.sh

# Quick development workflow
dev-check: format lint test check-version
	@echo "✅ All development checks passed!"