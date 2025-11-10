# 🩺 Slow Query Doctor

An intelligent database performance analyzer that uses AI to diagnose slow queries and provide actionable optimization recommendations.

## 🎯 **Current Support: PostgreSQL Only**
**✅ Ready to use**: PostgreSQL slow query analysis with AI-powered recommendations  
**🚧 Coming Q3 2026**: MySQL and SQL Server support in v0.4.0

> **🚀 Interested in early MySQL/SQL Server testing?** [File an issue](https://github.com/iqtoolkit/slow-query-doctor/issues/new?labels=mysql-feedback,sqlserver-feedback&title=Early%20Testing%20Interest) to get involved before v0.4.0 development starts!

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![OpenAI](https://img.shields.io/badge/AI-OpenAI%20Only%20v0.1.x-orange.svg)
![Ollama](https://img.shields.io/badge/AI-Ollama%20Coming%20v0.2.0-blue.svg)
![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL%20Ready-336791?logo=postgresql&logoColor=white)
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
  - [Testing with Sample Data](#testing-with-sample-data)
- [System Requirements](#-system-requirements)
  - [Dependencies](#dependencies)
- [License](#-license)
  - [Development Setup](#development-setup)
- [Documentation](#-documentation)
- [Roadmap, Technical Debt & Contributing](#-roadmap-technical-debt--contributing)

## 🎯 Overview

Slow Query Doctor automatically analyzes your **PostgreSQL** slow query logs and provides intelligent, AI-powered optimization recommendations. It identifies performance bottlenecks, calculates impact scores, and generates detailed reports with specific suggestions for improving database performance.

### 🗄️ **Database & AI Support Status**

**Database Support:**
| Database | Status | Version | Timeline |
|----------|--------|---------|----------|
| **PostgreSQL** | ✅ **Fully Supported** | v0.1.x+ | Available now |
| **MySQL** | 🚧 Planned | v0.4.0 | Q3 2026 |
| **SQL Server** | 🚧 Planned | v0.4.0 | Q3 2026 |

**AI Provider Support:**
| AI Provider | Status | Version | Timeline |
|------------|--------|---------|----------|
| **OpenAI GPT** | ✅ **Current Only** | v0.1.x | Available now |
| **Ollama (Local)** | 🚧 **Default in Future** | v0.2.0+ | Nov 2025 - Q1 2026 |
| **Multiple Providers** | 🚧 Configurable | v0.2.0+ | Nov 2025 - Q1 2026 |

> **📢 Want to influence MySQL/SQL Server development?** Check out our [future database sample directories](docs/sample_logs/) and share your specific requirements!

> **v0.1.6 Release Note**: This is the **final v0.1.x release with new features**. It includes comprehensive architecture documentation and prepares the codebase for multi-database support coming in v0.4.0. All references have been updated from "PostgreSQL-specific" to "database log analyzer" to reflect our roadmap for MySQL and SQL Server support. Future v0.1.x releases (v0.1.7+) will contain **bug fixes only** - all new features move to v0.2.0+.


### Key Features

- 🔍 **Smart Log Parsing**: Extracts slow queries from database logs, supports multi-line queries and unusual characters
- 📊 **Impact Analysis**: Calculates query impact using duration × frequency scoring
- 🤖 **AI-Powered Recommendations**: 
  - **v0.1.x**: OpenAI GPT models only (requires API key)
  - **v0.2.0+**: Configurable providers (Ollama default, OpenAI optional)
- 📝 **Comprehensive Reports**: Generates detailed Markdown reports with statistics and recommendations
- 📂 **Sample Data Included**: Ready-to-use sample PostgreSQL log files for testing and demonstration
- 🗂️ **Multiple Log Formats**: Supports plain, CSV, and JSON log formats
- ⚙️ **Config File Support**: Use a `.slowquerydoctor.yml` file to customize analysis options
- 🔒 **Privacy Evolution**: 
  - **v0.1.x**: OpenAI public API (privacy considerations for sensitive data)
  - **v0.2.0+**: Local Ollama models by default (enterprise-safe)
- 🔧 **Extensible**: Future-ready architecture supports multiple AI providers

## 🚀 Quick Start

> **⚡ Ready to analyze PostgreSQL slow queries right now?** Follow the installation below.  
> **🔮 Planning for MySQL/SQL Server?** [Join the early feedback program](https://github.com/iqtoolkit/slow-query-doctor/discussions) to shape v0.4.0 development!

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/slow-query-doctor.git
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
pip install .[dev,test]
```

4. **Set up AI provider:**

**Option A: OpenAI (Cloud, requires API key)**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

**Option B: Ollama (Local, private, no API key needed)**
```bash
# Install Ollama from https://ollama.com/download
ollama serve
ollama pull llama2

# Create .slowquerydoctor.yml
cat > .slowquerydoctor.yml << EOF
llm_provider: ollama
ollama_model: llama2
EOF
```

> **💡 Tip**: Ollama runs completely locally—your queries never leave your machine. Perfect for sensitive production data. See [Ollama Local Setup](docs/ollama-local.md) for details.

### Basic Usage

#### Try with Sample Data
```bash
# Analyze the included sample log file
python -m slowquerydoctor sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md

# Analyze top 5 slowest queries
python -m slowquerydoctor sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md --top-n 5

# Get more detailed AI analysis
python -m slowquerydoctor sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md --max-tokens 200

# Enable verbose (debug) output
python -m slowquerydoctor sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md --verbose
```

#### With Your Own Logs
```bash
# Basic analysis
python -m slowquerydoctor /path/to/your/postgresql.log --output analysis_report.md

# Advanced options
python -m slowquerydoctor /path/to/your/postgresql.log \
  --output detailed_report.md \
  --top-n 10 \
  --min-duration 1000 \
  --max-tokens 150 \
  --verbose
```

## 📂 Sample Log Files

The `docs/sample_logs/` directory contains database slow query log examples for testing and demonstration:

### ✅ **Current Support (v0.1.x)**
- **PostgreSQL**: Real sample logs from 100M record database operations with authentic slow queries

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
├── slowquerydoctor/          # Main package
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

### 🐘 **PostgreSQL Setup** (Current Focus)

See the full guide: [docs/getting-started.md](docs/getting-started.md)

Enable slow query logging in your `postgresql.conf`:

```postgresql
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


### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key | None | For OpenAI provider |
| `OPENAI_MODEL` | GPT model to use | `gpt-4o-mini` | Optional |
| `OPENAI_BASE_URL` | Custom OpenAI endpoint | `https://api.openai.com/v1` | Optional |

### Configuration File

Create a `.slowquerydoctor.yml` file to customize behavior:

```yaml
# AI Provider Selection
llm_provider: ollama  # or 'openai'
ollama_model: llama2
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

```sql
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

```bash
python -m slowquerydoctor [LOG_FILE] [OPTIONS]
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

## 🐛 Troubleshooting

### Common Issues

**"No slow queries found"**
```bash
# Check if log file contains duration entries
grep -i "duration:" your_log_file.log

# Verify PostgreSQL logging is enabled
psql -c "SHOW log_min_duration_statement;"
```

**"OpenAI API Error" (v0.1.x Only)**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

> **💡 Alternative**: If you prefer local AI processing for privacy, consider waiting for v0.2.0 with Ollama support (Nov 2025 - Q1 2026).

**"Permission denied on log file"**
```bash
# Fix file permissions
chmod 644 /path/to/postgresql.log

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

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=slowquerydoctor --cov-report=html
```

### Code Quality
```bash
# Format code
black slowquerydoctor/

# Lint code  
flake8 slowquerydoctor/

# Type checking
mypy slowquerydoctor/
```

### Testing with Sample Data
```bash
# Test the parser
python -c "from slowquerydoctor import parse_postgres_log; print(len(parse_postgres_log('sample_logs/postgresql-2025-10-28_192816.log.txt')))"

# Test full pipeline with sample data
python -m slowquerydoctor sample_logs/postgresql-2025-10-28_192816.log.txt --output test_report.md

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

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/slow-query-doctor.git
cd slow-query-doctor

# Complete development environment setup
bash scripts/setup-dev-environment.sh
source venv/bin/activate

# Install git hooks for automated version management
bash scripts/setup-hooks.sh

# Verify everything works
make check-version
make test
python -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .
# Or, for all dev/test dependencies:
pip install .[dev,test]
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
- 💡 [Examples](docs/examples.md) - Real usage examples
- ❓ [FAQ](docs/faq.md) - Common questions and troubleshooting

## 🤝 Roadmap, Technical Debt & Contributing

- See [ROADMAP.md](ROADMAP.md) for the full project roadmap, timeline, and community requests.
- See [TECHNICAL_DEBT.md](TECHNICAL_DEBT.md) for known limitations and areas for future improvement.
- See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines and code standards.
- See [VERSION_MANAGEMENT.md](VERSION_MANAGEMENT.md) for automated version synchronization.
- See [BRANCH_PROTECTION.md](BRANCH_PROTECTION.md) for repository governance and branch protection rules.
- See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system architecture and extension points.

**Made with ❤️ for Database performance optimization**