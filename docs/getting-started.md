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


## Basic Usage

See [README](../README.md#usage) for full details.

- Analyze a sample log (supports plain, CSV, and JSON formats, including multi-line queries):
  ```bash
  python -m slowquerydoctor sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md
  ```
- Analyze your own log:
  ```bash
  python -m slowquerydoctor /path/to/your/postgresql.log --output analysis_report.md
  ```

## Configuration File

You can use a `.slowquerydoctor.yml` file to set defaults for log format, thresholds, and output. See [Configuration](configuration.md).

## Dependencies

If installing manually, ensure you have `pyyaml`, `pandas`, and `tqdm` for all features.
