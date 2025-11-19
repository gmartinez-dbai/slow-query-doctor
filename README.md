# 🧠 Iqtoolkit Analyzer

An intelligent database performance analyzer that uses AI to diagnose slow queries and provide actionable optimization recommendations.

## 🎯 **Current Support: PostgreSQL + MongoDB Ready**
**✅ Production Ready**: PostgreSQL slow query analysis with comprehensive AI-powered recommendations  
**✅ Production Ready**: MongoDB slow query analysis with real-time profiler integration and multi-format reporting  
**🚧 Traditional SQL**: MySQL and SQL Server support in v0.4.0 (Q3 2026)

> **🚀 NEW in v0.2.0**: MongoDB support is now fully available! Use `iqtoolkit-analyzer mongodb` to analyze your MongoDB performance with real-time profiler integration, comprehensive indexing recommendations, and multi-format reports.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![OpenAI](https://img.shields.io/badge/AI-OpenAI%20Only%20v0.1.x-orange.svg)
![Ollama](https://img.shields.io/badge/AI-Ollama%20Coming%20v0.2.0-blue.svg)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL%20Ready-336791?logo=postgresql&logoColor=white)
![MongoDB](https://img.shields.io/badge/database-MongoDB%20Ready-47A248?logo=mongodb&logoColor=white)
![MySQL](https://img.shields.io/badge/database-MySQL%20Planned%20v0.4.0-4479A1?logo=mysql&logoColor=white)
![SQL Server](https://img.shields.io/badge/database-SQL%20Server%20Planned%20v0.4.0-CC2927?logo=microsoftssqlserver&logoColor=white)

![Docker](https://img.shields.io/badge/docker-ready-blue.svg)


## 📚 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Quick Start](#-quick-start)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
    - [Try with Sample Data](#try-with-sample-data)
    - [With Your Own Logs](#with-your-own-logs)
- [Sample Log Files](#-sample-log-files)
  - [Available Sample Files](#available-sample-files)
  - [Why .txt Extension?](#why-txt-extension)
  - [Sample Data Features](#sample-data-features)
  - [Sample Query Types Included](#sample-query-types-included)
- [Project Architecture](#-project-architecture)
  - [Data Flow](#data-flow)
- [Configuration](#-configuration)
  - [PostgreSQL Setup](#postgresql-setup)
  - [Environment Variables](#environment-variables)
  - [Configuration File](#configuration-file)
- [Slow Query Log Setup](#-slow-query-log-setup)
- [Sample Output](#-sample-output)
- [Command Line Options](#-command-line-options)
- [Troubleshooting](#-troubleshooting)
  - [Common Issues](#common-issues)
  - [Log File Locations](#log-file-locations)
- [Development](#-development)
  - [Running Tests](#running-tests)
  - [Code Quality](#code-quality)
    - [What does mypy do?](#what-does-mypy-do)
  - [Testing with Sample Data](#testing-with-sample-data)
  - [What is htmlcov and is it excluded?](#what-is-htmlcov-and-is-it-excluded)
- [System Requirements](#-system-requirements)
  - [Dependencies](#dependencies)
- [License](#-license)
  - [Development Setup](#development-setup)
- [Documentation](#-documentation)
- [Roadmap, Technical Debt & Contributing](#-roadmap-technical-debt--contributing)

## 🎯 Overview

Slow Query Doctor automatically analyzes your **PostgreSQL** and **MongoDB** slow query logs and provides intelligent, AI-powered optimization recommendations. It identifies performance bottlenecks, calculates impact scores, and generates detailed reports with specific suggestions for improving database performance.

### 🗄️ **Database & AI Support Status**

**Database Support:**
| Database | Status | Version | Timeline |
|----------|--------|---------|----------|
| **PostgreSQL** | ✅ **Fully Supported** | v0.1.x+ | Available now |
| **MongoDB** | ✅ **Fully Supported** | v0.2.0+ | Available now |
| **MySQL** | 🚧 Planned | v0.4.0 | Q3 2026 |
| **SQL Server** | 🚧 Planned | v0.4.0 | Q3 2026 |

**AI Provider Support:**
| AI Provider | Status | Version | Timeline |
|------------|--------|---------|----------|
| **OpenAI GPT** | ✅ **Current Only** | v0.1.x | Available now |
| **Ollama (Local)** | 🚧 **Default in Future** | v0.2.0+ | Nov 2025 - Q1 2026 |
| **Multiple Providers** | 🚧 Configurable | v0.2.0+ | Nov 2025 - Q1 2026 |

> **📢 MongoDB Ready**: MongoDB slow query analysis is now available! Use the `mongodb` command to analyze your MongoDB performance.
> 
> **📢 Want to influence MySQL/SQL Server development?** Check out our [future database sample directories](docs/sample_logs/) and share your specific requirements!

> **v0.1.6 Release Note**: This is the **final v0.1.x release with new features**. It includes comprehensive architecture documentation and prepares the codebase for multi-database support coming in v0.4.0. All references have been updated from "PostgreSQL-specific" to "database log analyzer" to reflect our roadmap for MySQL and SQL Server support. Future v0.1.x releases (v0.1.7+) will contain **bug fixes only** - all new features move to v0.2.0+.


### Key Features

- 🔍 **Smart Log Parsing**: 
  - **PostgreSQL**: Extracts slow queries from log files, supports multi-line queries and unusual characters
  - **MongoDB**: Real-time profiler integration for live slow query detection
- 📊 **Impact Analysis**: Calculates query impact using duration × frequency scoring
- 🤖 **AI-Powered Recommendations**: 
  - **v0.1.x**: OpenAI GPT models only (requires API key)
  - **v0.2.0+**: Configurable providers (Ollama default, OpenAI optional)  
- 📝 **Comprehensive Reports**: 
  - **PostgreSQL**: Detailed Markdown reports with statistics and recommendations
  - **MongoDB**: Multi-format reports (JSON, HTML, Markdown) with collection-level insights
- 📂 **Sample Data Included**: Ready-to-use sample log files for both PostgreSQL and MongoDB
- 🗂️ **Multiple Formats**: 
  - **PostgreSQL**: Plain, CSV, and JSON log formats
  - **MongoDB**: Direct profiler integration with configurable thresholds
- ⚙️ **Config File Support**: 
  - **PostgreSQL**: Use `.iqtoolkit-analyzer.yml` for analysis options
  - **MongoDB**: Use `.mongodb-config.yml` for connection and profiling settings
- 🔒 **Privacy Evolution**: 
  - **v0.1.x**: OpenAI public API (privacy considerations for sensitive data)
  - **v0.2.0+**: Local Ollama models by default (enterprise-safe)
- 🔧 **Extensible**: Future-ready architecture supports multiple databases and AI providers

## 🚀 Quick Start

> **⚡ Ready to analyze PostgreSQL or MongoDB slow queries right now?** Follow the installation below.  
> **🔮 Planning for MySQL/SQL Server?** [Join the early feedback program](https://github.com/iqtoolkit/slow-query-doctor/discussions) to shape v0.4.0 development!

### Installation

#### Option A: Using uv (Recommended - Fast & Modern)

1. **Install uv** (if not already installed):
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or via pip
pip install uv
```

2. **Clone and setup:**
```bash
git clone https://github.com/iqtoolkit/slow-query-doctor.git
cd slow-query-doctor

# Quick setup with uv
make setup
```

#### Option B: Traditional Python (Fallback)

1. **Clone the repository:**
```bash
git clone https://github.com/iqtoolkit/slow-query-doctor.git
cd slow-query-doctor
```

2. **Create virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
# Or, for full development setup:
pip install -e .[dev,test]
```

#### AI Provider Setup (Both Options)

**Option A: Ollama (Recommended - Local, private, no API key needed) ⭐**
```bash
# Quick setup (see docs/5-minute-ollama-setup.md for details)
curl -LsSf https://ollama.com/install.sh | sh
ollama serve
ollama pull arctic-text2sql-r1:7b  # SQL-specialized model (recommended)

# Copy example config and customize
cp .iqtoolkit-analyzer.yml.example .iqtoolkit-analyzer.yml
# Edit: set llm_provider: ollama
```

**Option B: OpenAI (Cloud, requires API key)**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
# Config will use OpenAI by default if no .iqtoolkit-analyzer.yml exists
```

> **💡 Tip**: Ollama runs completely locally—your queries never leave your machine. Perfect for sensitive production data. See [Ollama Local Setup](docs/ollama-local.md) for details.

### Basic Usage

#### PostgreSQL Analysis
```bash
# With uv (recommended - fast)
uv run python -m slowquerydoctor postgresql sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md

# Or traditional approach
python -m slowquerydoctor postgresql sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md
```

#### MongoDB Analysis
```bash
# Connect to MongoDB and analyze slow queries
uv run python -m slowquerydoctor mongodb --connection-string "mongodb://localhost:27017" --output ./reports

# With configuration file
uv run python -m iqtoolkit_analyzer mongodb --config .mongodb-config.yml --output ./reports

# Traditional approach
python -m slowquerydoctor mongodb --connection-string "mongodb://localhost:27017" --output ./reports
```

#### Advanced Usage Examples
```bash
# PostgreSQL: Analyze top 5 slowest queries (uv)
uv run python -m iqtoolkit_analyzer postgresql sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md --top-n 5

# MongoDB: Generate multiple report formats
uv run python -m iqtoolkit_analyzer mongodb --connection-string "mongodb://localhost:27017" --output ./reports --format json html markdown

# PostgreSQL: Get more detailed AI analysis (uv)
uv run python -m iqtoolkit_analyzer postgresql sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md --max-tokens 200

# MongoDB: Enable verbose debug output
uv run python -m iqtoolkit_analyzer mongodb --connection-string "mongodb://localhost:27017" --output ./reports --verbose

# Traditional approach for any of the above
python -m iqtoolkit_analyzer postgresql sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md --top-n 5
```

#### With Your Own Logs
```bash
# Basic analysis (uv)
uv run python -m iqtoolkit_analyzer /path/to/your/postgresql.log --output analysis_report.md

# Advanced options (uv)
uv run python -m iqtoolkit_analyzer /path/to/your/postgresql.log \
  --output detailed_report.md \
  --top-n 10 \
  --min-duration 1000 \
  --max-tokens 150 \
  --verbose

# Traditional approach
python -m iqtoolkit_analyzer /path/to/your/postgresql.log --output analysis_report.md
```

## 📂 Sample Log Files

The `docs/sample_logs/` directory contains database slow query log examples for testing and demonstration:

### ✅ **Current Support**
- **PostgreSQL**: Real sample logs from 100M record database operations with authentic slow queries → [View samples](docs/sample_logs/postgresql/)
- **MongoDB**: Complete profiler integration with real-time slow query detection and comprehensive optimization recommendations → [View samples](docs/sample_logs/mongodb/)

### 🚧 **Future Support (v0.4.0 - Q3 2026)**
- **MySQL**: Placeholder directory with configuration examples and feedback collection → [View samples](docs/sample_logs/mysql/)
- **SQL Server**: Placeholder directory with Extended Events samples and configuration → [View samples](docs/sample_logs/sqlserver/)

> 🎯 **Early Feedback Opportunities**: 
> - **MySQL Users**: [Share your slow query log formats and challenges](https://github.com/iqtoolkit/slow-query-doctor/issues/new?labels=mysql-feedback&title=MySQL%20Requirements)
> - **SQL Server DBAs**: [Tell us about your Extended Events setup and pain points](https://github.com/iqtoolkit/slow-query-doctor/issues/new?labels=sqlserver-feedback&title=SQL%20Server%20Requirements)

### Available Sample Files

- **`postgresql-2025-10-28_192816.log.txt`**: Contains authentic slow queries from a 100M record database including:
  - **Complex aggregation queries** (15.5+ seconds): Statistical calculations across 40M records
  - **Expensive correlated subqueries** (109+ seconds): Text pattern matching with per-row subqueries  
  - **Mathematical operations with window functions** (209+ seconds): Multiple window functions with trigonometric calculations
  - **Multiple query patterns** that benefit from different optimization strategies (indexes, query rewrites, JOIN optimizations)

### Why `.txt` Extension?

Sample log files use the `.txt` extension instead of `.log` to prevent them from being excluded by `.gitignore` patterns that typically ignore `*.log` files. This ensures the sample data remains available in the repository for testing and demonstration purposes.

### Sample Data Features

- **Real Performance Issues**: Authentic slow queries from actual 100M record database operations
- **Variety of Problems**: Different types of performance bottlenecks (missing indexes, correlated subqueries, expensive window functions)
- **AI-Ready**: Perfect for testing AI recommendation quality with real optimization opportunities
- **Educational**: Great examples for learning PostgreSQL performance optimization techniques
- **Range of Complexity**: From 2-second queries to 209-second extreme cases

### Sample Query Types Included

1. **Aggregation with Mathematical Functions** (15.5s)
   - `AVG`, `STDDEV`, `COUNT` operations on large datasets
   - Range filtering across 40M records
   - Perfect for testing index recommendations

2. **Correlated Subqueries with Pattern Matching** (109s)
   - `LIKE` operations with multiple patterns
   - Correlated subquery executing for each row
   - Demonstrates JOIN optimization opportunities

3. **Window Functions with Mathematical Operations** (209s)
   - Multiple `ROW_NUMBER()`, `RANK()`, `LAG()`, `LEAD()` functions
   - Complex mathematical calculations (`SQRT`, `SIN`, `COS`, `LOG`)
   - Heavy sorting and partitioning operations

## 🏗️ Project Architecture

```
slow-query-doctor/
├── iqtoolkit_analyzer/       # Main package
│   ├── __init__.py          # Package interface
│   ├── parser.py            # Log file parsing
│   ├── analyzer.py          # Query analysis & scoring
│   ├── llm_client.py        # AI/OpenAI integration
│   └── report_generator.py  # Markdown report generation
├── sample_logs/             # Sample PostgreSQL log files
│   └── postgresql-2025-10-28_192816.log.txt  # Real slow query examples
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Data Flow

1. **Parse** → Extract slow queries from database logs (currently PostgreSQL)
2. **Analyze** → Calculate impact scores and normalize queries  
3. **AI Analysis** → Generate optimization recommendations using AI models
4. **Report** → Create comprehensive Markdown analysis report

> **Multi-Database Roadmap**: MySQL and SQL Server support planned for v0.4.0 (Q3 2026)


## ⚙️ Configuration

### 🐘 **PostgreSQL Setup**

See the full guide: [docs/getting-started.md](docs/getting-started.md)

Enable slow query logging in your `postgresql.conf`:

```conf
# Log queries taking longer than 1 second
log_min_duration_statement = 1000

# Enable logging collector
logging_collector = on

# Set log directory (relative to data_directory)
log_directory = 'log'

# Log file naming pattern
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'

# What to log
log_statement = 'none'
log_duration = off
```

Or configure dynamically:
```sql
-- Enable for current session
SET log_min_duration_statement = 1000;

-- Enable globally (requires restart)
ALTER SYSTEM SET log_min_duration_statement = 1000;
SELECT pg_reload_conf();
```
## 🐢 Slow Query Log Setup

For a step-by-step guide to enabling slow query logging, running example queries, and analyzing logs, see:

- [docs/getting-started.md](docs/getting-started.md)

This guide covers:
- Editing postgresql.conf
- Session-level logging
- Running example slow queries
- Collecting and analyzing logs with Slow Query Doctor

### 🍃 **MongoDB Setup**

MongoDB analysis uses the built-in profiler to collect slow operation data. Enable profiling for your databases:

```javascript
// Enable profiling for operations slower than 100ms
db.setProfilingLevel(2, {slowms: 100})

// Check profiling status
db.getProfilingStatus()

// View recent slow operations
db.system.profile.find().limit(5).sort({ts: -1}).pretty()
```

Create a `.mongodb-config.yml` configuration file:

```yaml
# MongoDB Connection
connection:
  connection_string: "mongodb://localhost:27017"
  connection_timeout_ms: 5000
  
# Performance Thresholds
thresholds:
  slow_threshold_ms: 100.0
  very_slow_threshold_ms: 1000.0
  critical_threshold_ms: 5000.0
  
# Analysis Settings
databases_to_monitor: ["myapp", "analytics"]
exclude_databases: ["admin", "config", "local"]

# Report Settings
reporting:
  formats: ["json", "html", "markdown"]
  include_query_samples: true
  max_query_samples: 5
```

For complete MongoDB setup instructions, see: [docs/mongodb-guide.md](docs/mongodb-guide.md)

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | None | For OpenAI provider |
| `OPENAI_MODEL` | GPT model to use | `gpt-4o-mini` | Optional |
| `OPENAI_BASE_URL` | Custom OpenAI endpoint | `https://api.openai.com/v1` | Optional |

### Configuration File

Create a `.iqtoolkit-analyzer.yml` file to customize behavior:

```yaml
# AI Provider Selection
llm_provider: ollama  # or 'openai'
ollama_model: arctic-text2sql-r1:7b
ollama_host: http://localhost:11434  # optional, for custom hosts

# OpenAI (if using)
openai_api_key: sk-xxx  # optional, can use env var instead
openai_model: gpt-4o-mini

# Analysis Options
log_format: csv
top_n: 10
output: reports/report.md
min_duration: 1000

# LLM Configuration
llm_temperature: 0.3
max_tokens: 300
llm_timeout: 30
```

See [Configuration Guide](docs/configuration.md) for all options and [Ollama Local Setup](docs/ollama-local.md) for local AI setup.

## 📊 Sample Output

```markdown
# Slow Query Analysis Report

## Summary
- **Total queries analyzed**: 8
- **Slow queries found**: 4  
- **Total duration**: 336,175.06 ms
- **Most impactful query**: Mathematical operations with window functions

## Top Slow Queries

### Query #1: Mathematical Operations with Window Functions (Impact Score: 209,297.06)
**Duration**: 209,297.06 ms | **Frequency**: 1 | **First seen**: 2025-10-28 20:04:57

```sql
SELECT id, random_number, random_text, created_at,
    SQRT(ABS(random_number)::numeric) as sqrt_abs_number,
    LOG(GREATEST(random_number, 1)::numeric) as log_number,
    SIN(random_number::numeric / 180000.0 * PI()) as sin_degrees,
    ROW_NUMBER() OVER (ORDER BY random_number) as row_num_asc,
    AVG(random_number) OVER (ROWS BETWEEN 1000 PRECEDING AND 1000 FOLLOWING) as moving_avg
FROM large_test_table 
WHERE random_number BETWEEN 250000 AND 750000
  AND (id % 7 = 0 OR id % 11 = 0 OR id % 13 = 0)
ORDER BY SQRT(ABS(random_number)::numeric) DESC
LIMIT 200;
```

**🤖 AI Recommendation:**
This query suffers from expensive mathematical operations and multiple window functions. Create a composite index on `(random_number, id)` and consider materializing complex calculations. The multiple window functions could be optimized by combining operations. Expected improvement: 70-85% faster execution.

### Query #2: Correlated Subquery with Pattern Matching (Impact Score: 109,234.02)
**Duration**: 109,234.02 ms | **Frequency**: 1 | **First seen**: 2025-10-28 19:31:23

```text
SELECT DISTINCT l1.random_number, l1.random_text, l1.created_at,
    (SELECT COUNT(*) FROM large_test_table l2 WHERE l2.random_number = l1.random_number)
FROM large_test_table l1
WHERE l1.random_text LIKE '%data_555%' OR l1.random_text LIKE '%data_777%'
ORDER BY l1.random_number DESC LIMIT 30;
```

**🤖 AI Recommendation:**
Replace the correlated subquery with a JOIN or window function. Create indexes on `random_text` (consider GIN for pattern matching) and `random_number`. The LIKE operations with leading wildcards are expensive - consider full-text search if applicable. Expected improvement: 60-80% faster execution.
```

## 🔧 Command Line Options

### PostgreSQL Analysis
```bash
# With uv (recommended)
uv run python -m slowquerydoctor postgresql [LOG_FILE] [OPTIONS]

# Traditional approach
python -m slowquerydoctor postgresql [LOG_FILE] [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `LOG_FILE` | Path to PostgreSQL log file | Required |
| `--output`, `-o` | Output report file path | `slow_query_report.md` |
| `--top-n`, `-n` | Number of top queries to analyze | `10` |
| `--min-duration` | Minimum duration (ms) to consider | `1000` |
| `--max-tokens` | Max tokens for AI analysis | `150` |
| `--model` | OpenAI model to use | `gpt-4o-mini` |
| `--verbose` | Enable verbose (debug) output for troubleshooting and progress tracking | - |
| `--help`, `-h` | Show help message | - |

### MongoDB Analysis
```bash
# With uv (recommended)
uv run python -m slowquerydoctor mongodb [OPTIONS]

# Traditional approach
python -m slowquerydoctor mongodb [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--connection-string` | MongoDB connection string | Required |
| `--config`, `-c` | Configuration file path (YAML format) | None |
| `--output`, `-o` | Output directory for reports | `./reports` |
| `--format`, `-f` | Report formats: json, markdown, html | `json` |
| `--databases` | Databases to analyze (comma-separated) | All accessible |
| `--verbose` | Enable verbose (debug) output | - |
| `--help`, `-h` | Show help message | - |

## 🐛 Troubleshooting

### Common Issues

#### PostgreSQL Issues

**"No slow queries found"**
```bash
# Check if log file contains duration entries
grep -i "duration:" your_log_file.log

# Verify PostgreSQL logging is enabled
psql -c "SHOW log_min_duration_statement;"
```

**"Permission denied on log file"**
```bash
# Fix file permissions
chmod 644 /path/to/postgresql.log
```

#### MongoDB Issues

**"Connection failed"**
```bash
# Test MongoDB connection
mongosh "mongodb://localhost:27017" --eval "db.adminCommand('ismaster')"

# Check if profiler is enabled
mongosh "mongodb://localhost:27017/mydb" --eval "db.getProfilingStatus()"
```

**"No profiler data found"**
```bash
# Enable MongoDB profiling for slow operations (>100ms)
mongosh "mongodb://localhost:27017/mydb" --eval "db.setProfilingLevel(2, {slowms: 100})"

# Check system.profile collection
mongosh "mongodb://localhost:27017/mydb" --eval "db.system.profile.count()"
```

#### AI/General Issues

**"OpenAI API Error" (v0.1.x Only)**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

> **💡 Alternative**: If you prefer local AI processing for privacy, consider waiting for v0.2.0 with Ollama support (Nov 2025 - Q1 2026).

# Or copy to accessible location
cp /var/log/postgresql/postgresql.log ~/my_log.log
```

### Log File Locations

| Installation Method | Typical Log Location |
|-------------------|---------------------|
| **Homebrew (macOS)** | `/opt/homebrew/var/postgresql@*/log/` |
| **Ubuntu/Debian** | `/var/log/postgresql/` |
| **CentOS/RHEL** | `/var/lib/pgsql/*/data/log/` |
| **Docker** | `/var/lib/postgresql/data/log/` |
| **Windows** | `C:\Program Files\PostgreSQL\*\data\log\` |

## 🧪 Development

### Quick Development Setup
```bash
# Clone and setup with uv (recommended)
git clone https://github.com/iqtoolkit/slow-query-doctor.git
cd slow-query-doctor
make setup

# Or traditional approach
git clone https://github.com/iqtoolkit/slow-query-doctor.git
cd slow-query-doctor
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev,test]
```

### Running Tests
```bash
# With uv (recommended)
make test          # Run all tests
make lint          # Run linting
make format        # Format code

# Traditional approach
pytest tests/ -v
pytest tests/ --cov=slowquerydoctor --cov-report=html
```

### What is htmlcov and is it excluded?
htmlcov is the folder where the HTML coverage report is generated when you run tests with coverage reporting. In this project:

- How it’s generated:
  - Pytest is configured in pyproject.toml to produce coverage reports, including HTML, via addopts:
    --cov=slowquerydoctor --cov-report=term-missing --cov-report=html --cov-report=xml
  - The HTML output directory is configured under [tool.coverage.html] as directory = "htmlcov".
  - You’ll typically get it by running make test (which runs pytest with those flags) or pytest ... --cov-report=html.
- Where to view it:
  - Open htmlcov/index.html in your browser to see per-file and line-level coverage.
- Is it excluded from Git?
  - Yes. .gitignore contains htmlcov/ so the generated report is not committed.
- How to clean it up:
  - make clean removes htmlcov/ along with other build/test artifacts.

### Code Quality
```bash
# With uv and Makefile (recommended)
make format        # Format with black
make lint          # Lint with flake8 + mypy
make validate      # Full validation suite

# Traditional approach
black slowquerydoctor/
flake8 slowquerydoctor/
mypy slowquerydoctor/
```

#### What does mypy do?
Mypy is a static type checker for Python. It analyzes your code without executing it to catch type-related errors early and to make the codebase easier to maintain.

In this repository, mypy helps to:
- Prevent common bugs by verifying function inputs/outputs match their annotations
- Enforce consistent, explicit types (useful in a data-heavy tool like this)
- Improve editor/IDE auto-completion and refactoring safety

How it’s configured here:
- Configuration lives in pyproject.toml under [tool.mypy]
- We enable a relatively strict set of options:
  - disallow-untyped-defs, disallow-incomplete-defs, disallow-untyped-decorators
  - no_implicit_optional, warn_redundant_casts, warn_unused_ignores, warn_no_return, warn_unreachable
  - strict_equality and check_untyped_defs
- Third‑party modules with incomplete type hints (like openai, dotenv) are allowed via ignore_missing_imports overrides.

How to run it:
- Recommended: make lint (runs flake8 then mypy via uv)
- Directly: uv run mypy slowquerydoctor

Common fixes:
- Add or refine type hints: parameters, return types, and local variables when useful
- Use Optional[T] (or | None) when something can be None
- Narrow types with isinstance checks before using values
- For one-off unavoidable cases, use a targeted suppression:  # type: ignore[code]

Type stubs:
- If a dependency lacks types, prefer installing its types (e.g., types-pyyaml)
- If none exist, consider adding minimal annotations around your usage or a local stub package later

### Testing with Sample Data
```bash
# Test the parser
uv run python -c "from slowquerydoctor import parse_postgres_log; print(len(parse_postgres_log('sample_logs/postgresql-2025-10-28_192816.log.txt')))"

# Test full pipeline with sample data
uv run python -m slowquerydoctor sample_logs/postgresql-2025-10-28_192816.log.txt --output test_report.md

# Verify AI recommendations are generated
grep -A 5 "🤖 AI Recommendation" test_report.md
```

## 📋 System Requirements

- **Python**: 3.11 or higher
- **Memory**: 512MB+ available RAM
- **Storage**: 50MB+ free space
- **Network**: Internet connection for OpenAI API
- **Platforms**: macOS, Linux, Windows


### Dependencies

- `openai>=1.0.0` - OpenAI API client
- `python-dotenv>=0.19.0` - Environment variable management
- `pandas>=2.0.0` - Data analysis and CSV/JSON log support
- `pyyaml>=6.0.0` - YAML config file support
- `tqdm>=4.0.0` - Progress bars for large log analysis
- `pytest`, `pytest-cov` - Testing and coverage (dev)
- `black`, `flake8`, `mypy`, `isort`, `pre-commit` - Code quality (dev)
- `argparse` - Command line parsing (built-in)
- `re`, `json`, `logging` - Standard library modules

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup (with uv)
```bash
# Clone your fork
git clone https://github.com/yourusername/slow-query-doctor.git
cd slow-query-doctor

# Complete development environment setup
bash scripts/setup-dev-environment.sh

# Install git hooks for automated version management
bash scripts/setup-hooks.sh

# Verify everything works
make check-version
make test

# Install in development mode (if you didn't run setup script)
uv venv --python 3.11
uv pip install -r requirements.txt
uv pip install -e .[dev]
```
## 📈 Roadmap, Technical Debt & Contributing

**Database Support Roadmap:**
- **v0.1.6** (Nov 2025): Final v0.1.x feature release - Documentation & architecture updates 🔒
- **v0.1.7+**: Bug fixes only (feature freeze for v0.1.x branch)
- **v0.2.0** (Nov 2025 - Q1 2026): Configurable AI providers (Ollama default), enhanced config system, EXPLAIN plans, HTML reports 🔧
- **v0.3.0** (Q2 2026): ML/self-learning features 📋
- **v0.4.0** (Q3 2026): **MySQL and SQL Server support** 📋

**AI Provider Evolution:**
- **v0.1.x CURRENT**: OpenAI GPT models only (requires OPENAI_API_KEY)
- **v0.2.0 COMING**: Configurable providers with Ollama as privacy-first default
- **v0.2.0+ FUTURE**: Extensible to Claude, Gemini, custom endpoints

> **⚠️ Privacy Note for v0.1.x**: Current version sends query data to OpenAI's public API. For sensitive production logs, consider waiting for v0.2.0 with local Ollama support.

**When asked about new features**: 
- **For v0.1.x**: "v0.1.6 is the final feature release. New features go to v0.2.0+ roadmap."
- **For MySQL/SQL Server**: "Added to v0.4.0 roadmap (Q3 2026) - we're focusing on perfecting PostgreSQL analysis first with v0.2.0 configurable AI providers."

## 📚 Documentation

For complete documentation and guides, see our [**Documentation Index**](DOCUMENTATION_INDEX.md) 📖

**Quick Links:**
- 🚀 [Getting Started](docs/getting-started.md) - New user tutorial
- 🤝 [Contributing Guide](CONTRIBUTING.md) - How to contribute
- ⚙️ [Configuration](docs/configuration.md) - Setup and config options  
- 💡 [PostgreSQL Examples](docs/pg_examples.md) - Real usage examples
- ❓ [FAQ](docs/faq.md) - Common questions and troubleshooting

## 🤝 Roadmap, Technical Debt & Contributing

- See [ROADMAP.md](ROADMAP.md) for the full project roadmap, timeline, and community requests.
- See [TECHNICAL_DEBT.md](TECHNICAL_DEBT.md) for known limitations and areas for future improvement.
- See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and code standards.
- See [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) for automated version synchronization.
- See [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) for repository governance and branch protection rules.
- See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system architecture and extension points.

**Made with ❤️ for Database performance optimization**