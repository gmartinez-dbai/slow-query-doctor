# Makefile for slow-query-doctor

.PHONY: help setup sync-version check-version install test lint format clean hooks validate

# Default target
help:
	@echo "🚀 Slow Query Doctor - Development Commands"
	@echo ""
	@echo "⚠️  IMPORTANT: All commands require '.venv' directory in repo root!"
	@echo "   First time: make setup  (uses uv if available, fallback to pip)"
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
	@echo "  make test-ollama  Test Ollama setup and integration"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean        Remove build artifacts and cache"

# Setup development environment
setup: hooks install
	@if [ ! -d ".venv" ]; then \
		if command -v uv >/dev/null 2>&1; then \
			echo "📦 Creating '.venv' with uv..."; \
			uv venv --python 3.11; \
		else \
			echo "📦 Creating '.venv' with standard venv..."; \
			python -m venv .venv; \
		fi \
	fi
	@echo "📦 Installing development dependencies..."
	@if command -v uv >/dev/null 2>&1; then \
		echo "🚀 Using uv for fast installation"; \
		uv pip install -r requirements.txt; \
		uv pip install -e .[dev]; \
	else \
		echo "🐍 Using pip for installation"; \
		.venv/bin/pip install -r requirements.txt; \
		.venv/bin/pip install -e .[dev]; \
	fi
	@echo "✅ Development environment ready!"

# Install git hooks
hooks:
	@chmod +x scripts/setup-hooks.sh
	@bash scripts/setup-hooks.sh

# Install package in development mode
install:
	@if [ ! -d ".venv" ]; then \
		if command -v uv >/dev/null 2>&1; then \
			echo "📦 Creating '.venv' with uv..."; \
			uv venv --python 3.11; \
		else \
			echo "📦 Creating '.venv' with standard venv..."; \
			python -m venv .venv; \
		fi \
	fi
	@if command -v uv >/dev/null 2>&1; then \
		echo "🚀 Installing with uv..."; \
		uv pip install -r requirements.txt; \
		uv pip install -e .; \
	else \
		echo "🐍 Installing with pip..."; \
		.venv/bin/pip install -r requirements.txt; \
		.venv/bin/pip install -e .; \
	fi

# Version management
sync-version:
	@if [ ! -d ".venv" ]; then \
		if command -v uv >/dev/null 2>&1; then \
			echo "📦 Creating '.venv' with uv..."; \
			uv venv --python 3.11; \
		else \
			echo "📦 Creating '.venv' with standard venv..."; \
			python -m venv .venv; \
		fi \
	fi
	@echo "🔄 Synchronizing versions..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -r requirements.txt > /dev/null 2>&1; \
		uv run python scripts/propagate_version.py; \
	else \
		.venv/bin/pip install -r requirements.txt > /dev/null 2>&1; \
		.venv/bin/python scripts/propagate_version.py; \
	fi

check-version:
	@if [ ! -d ".venv" ]; then \
		if command -v uv >/dev/null 2>&1; then \
			echo "📦 Creating '.venv' with uv..."; \
			uv venv --python 3.11; \
		else \
			echo "📦 Creating '.venv' with standard venv..."; \
			python -m venv .venv; \
		fi \
	fi
	@echo "🔍 Checking version consistency..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -r requirements.txt > /dev/null 2>&1; \
		uv run python scripts/propagate_version.py --verify; \
	else \
		.venv/bin/pip install -r requirements.txt > /dev/null 2>&1; \
		.venv/bin/python scripts/propagate_version.py --verify; \
	fi

# Dependency management
update-requirements:
	@if [ ! -d ".venv" ]; then \
		if command -v uv >/dev/null 2>&1; then \
			echo "📦 Creating '.venv' with uv..."; \
			uv venv --python 3.11; \
		else \
			echo "📦 Creating '.venv' with standard venv..."; \
			python -m venv .venv; \
		fi \
	fi
	@if command -v uv >/dev/null 2>&1; then \
		echo "📦 Updating requirements.txt from pyproject.toml using uv..."; \
		uv lock; \
		uv export --frozen --output-file requirements.txt; \
	else \
		echo "📦 Updating requirements.txt using custom script..."; \
		.venv/bin/pip install -r requirements.txt > /dev/null 2>&1; \
		.venv/bin/python scripts/update_requirements.py; \
	fi

# Code formatting
format:
	@if [ ! -d ".venv" ]; then \
		if command -v uv >/dev/null 2>&1; then \
			echo "📦 Creating '.venv' with uv..."; \
			uv venv --python 3.11; \
		else \
			echo "📦 Creating '.venv' with standard venv..."; \
			python -m venv .venv; \
		fi \
	fi
	@echo "🎨 Formatting code..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -r requirements.txt > /dev/null 2>&1; \
		uv run black slowquerydoctor tests scripts; \
	else \
		.venv/bin/pip install -r requirements.txt > /dev/null 2>&1; \
		.venv/bin/python -m black slowquerydoctor tests scripts; \
	fi
	@echo "✅ Code formatted!"

# Linting
lint:
	@if [ ! -d ".venv" ]; then \
		if command -v uv >/dev/null 2>&1; then \
			echo "📦 Creating '.venv' with uv..."; \
			uv venv --python 3.11; \
		else \
			echo "📦 Creating '.venv' with standard venv..."; \
			python -m venv .venv; \
		fi \
	fi
	@echo "🔍 Running linting..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -r requirements.txt > /dev/null 2>&1; \
		uv run flake8 slowquerydoctor tests scripts --max-line-length=88 --extend-ignore=E203,W503 --exclude=scripts/propagate_version.py; \
		uv run mypy slowquerydoctor --ignore-missing-imports; \
	else \
		.venv/bin/pip install -r requirements.txt > /dev/null 2>&1; \
		.venv/bin/python -m flake8 slowquerydoctor tests scripts --max-line-length=88 --extend-ignore=E203,W503 --exclude=scripts/propagate_version.py; \
		.venv/bin/python -m mypy slowquerydoctor --ignore-missing-imports; \
	fi
	@echo "✅ Linting passed!"

# Run tests
test:
	@if [ ! -d ".venv" ]; then \
		if command -v uv >/dev/null 2>&1; then \
			echo "📦 Creating '.venv' with uv..."; \
			uv venv --python 3.11; \
		else \
			echo "📦 Creating '.venv' with standard venv..."; \
			python -m venv .venv; \
		fi \
	fi
	@echo "🧪 Running tests..."
	@if command -v uv >/dev/null 2>&1; then \
		uv pip install -r requirements.txt > /dev/null 2>&1; \
		uv run pytest tests/ --cov=slowquerydoctor --cov-report=term-missing --cov-report=html; \
	else \
		.venv/bin/pip install -r requirements.txt > /dev/null 2>&1; \
		.venv/bin/python -m pytest tests/ --cov=slowquerydoctor --cov-report=term-missing --cov-report=html; \
	fi
	@echo "✅ Tests completed!"

# Test Ollama setup
test-ollama:
	@echo "🤖 Testing Ollama setup..."
	@if command -v uv >/dev/null 2>&1; then \
		uv run python scripts/test_ollama.py; \
	else \
		.venv/bin/python scripts/test_ollama.py; \
	fi

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