# [← Back to Index](index.md)
# 🚀 Getting Started

Welcome to Slow Query Doctor!

For a quick overview, see the [Project README](../README.md).

## Installation

### Option A: Using uv (Recommended - Fast & Modern)

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/iqtoolkit/slow-query-doctor.git
cd slow-query-doctor
make setup
```

### Option B: Traditional Python (Fallback)

```bash
git clone https://github.com/iqtoolkit/slow-query-doctor.git
cd slow-query-doctor
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

If you want to use local LLMs, see [Ollama Local Setup](ollama-local.md) for installation and usage instructions.



## Basic Usage

### PostgreSQL Analysis
See [PostgreSQL Examples](pg_examples.md) for all CLI and log analysis examples.

### MongoDB Analysis

MongoDB analysis uses the built-in profiler to collect slow operation data in real-time:

#### 1. Enable MongoDB Profiling
```bash
# Connect to MongoDB
mongosh "mongodb://localhost:27017/myapp"

# Enable profiling for operations slower than 100ms
db.setProfilingLevel(2, {slowms: 100})

# Verify profiling is enabled
db.getProfilingStatus()
```

#### 2. Run Analysis
```bash
# Basic analysis with connection string
uv run python -m slowquerydoctor mongodb --connection-string "mongodb://localhost:27017" --output ./reports

# Advanced analysis with configuration file
cp docs/examples/.mongodb-config.yml.example .mongodb-config.yml
# Edit .mongodb-config.yml for your environment
uv run python -m slowquerydoctor mongodb --config .mongodb-config.yml --output ./reports

# Generate multiple report formats
uv run python -m slowquerydoctor mongodb \
  --connection-string "mongodb://localhost:27017" \
  --output ./reports \
  --format json html markdown
```

#### 3. View Reports
- **JSON Report**: Machine-readable analysis data (`mongodb_analysis.json`)
- **HTML Report**: Interactive dashboard with charts (`mongodb_report.html`)
- **Markdown Report**: Human-readable summary (`mongodb_analysis.md`)

See [MongoDB Guide](mongodb-guide.md) for complete setup and usage instructions.

## Configuration File

You can use a `.slowquerydoctor.yml` file to set defaults for log format, thresholds, and output. See [Configuration](configuration.md).

## Dependencies

If installing manually, ensure you have `pyyaml`, `pandas`, and `tqdm` for all features.
