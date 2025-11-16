# [← Back to Index](index.md)
# ❓ FAQ

For more, see the [Project README](../README.md) and [ROADMAP.md](../ROADMAP.md).

## Common Questions


### Q: What is `htmlcov` and is it excluded from Git?
A: `htmlcov/` is the folder where pytest/coverage.py writes the HTML coverage report. In this project, pytest is configured in `pyproject.toml` to generate HTML coverage (`--cov-report=html`) and the output directory is set to `htmlcov` under `[tool.coverage.html]`. The `htmlcov/` directory is ignored by Git via `.gitignore`, and `make clean` removes it. Open `htmlcov/index.html` in a browser to view the report.

### Q: How do I use local LLMs or fix 'model not found' errors?
A: See [Ollama Local Setup](ollama-local.md) for instructions on installing and running models locally.

### Q: How do I get my PostgreSQL logs?
A: See [Configuration](configuration.md#postgresql-setup) for setup instructions.

### Q: Why does the sample log use `.txt`?
A: To avoid being ignored by `.gitignore` rules for `.log` files.

### Q: How do I contribute?
A: See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### Q: Where can I see upcoming features?
A: See [ROADMAP.md](../ROADMAP.md).

### Q: How do I report a bug or request a feature?
A: Open an issue on GitHub or email gio@gmartinez.net.
