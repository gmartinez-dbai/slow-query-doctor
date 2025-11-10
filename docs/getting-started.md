# [← Back to Index](index.md)
# 🚀 Getting Started

Welcome to Slow Query Doctor!

For a quick overview, see the [Project README](../README.md).

## Installation


```bash
git clone https://github.com/gmartinez-dbai/slow-query-doctor.git
cd slow-query-doctor
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

If you want to use local LLMs, see [Ollama Local Setup](ollama-local.md) for installation and usage instructions.



## Basic Usage

See [Usage Examples](examples.md) for all CLI and log analysis examples.

## Configuration File

You can use a `.slowquerydoctor.yml` file to set defaults for log format, thresholds, and output. See [Configuration](configuration.md).

## Dependencies

If installing manually, ensure you have `pyyaml`, `pandas`, and `tqdm` for all features.
