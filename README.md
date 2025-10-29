# 🩺 Slow Query Doctor

An intelligent PostgreSQL performance analyzer that uses AI to diagnose slow queries and provide actionable optimization recommendations.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![OpenAI](https://img.shields.io/badge/AI-OpenAI%20GPT--4o--mini-orange.svg)

## 🎯 Overview

Slow Query Doctor automatically analyzes your PostgreSQL slow query logs and provides intelligent, AI-powered optimization recommendations. It identifies performance bottlenecks, calculates impact scores, and generates detailed reports with specific suggestions for improving database performance.

### Key Features

- 🔍 **Smart Log Parsing**: Automatically extracts slow queries from PostgreSQL logs
- 📊 **Impact Analysis**: Calculates query impact using duration × frequency scoring
- 🤖 **AI-Powered Recommendations**: Uses OpenAI GPT to provide specific optimization advice
- 📝 **Comprehensive Reports**: Generates detailed Markdown reports with statistics and recommendations
- 📂 **Sample Data Included**: Ready-to-use sample log files for testing and demonstration

## 🚀 Quick Start

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
```

4. **Set up OpenAI API key:**
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### Basic Usage

#### Try with Sample Data
```bash
# Analyze the included sample log file
python -m slowquerydoctor sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md

# Analyze top 5 slowest queries
python -m slowquerydoctor sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md --top-n 5

# Get more detailed AI analysis
python -m slowquerydoctor sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md --max-tokens 200
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
  --max-tokens 150
```

## 📂 Sample Log Files

The `sample_logs/` directory contains real PostgreSQL slow query log examples for testing and demonstration:

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

1. **Parse** → Extract slow queries from PostgreSQL logs
2. **Analyze** → Calculate impact scores and normalize queries  
3. **AI Analysis** → Generate optimization recommendations using GPT
4. **Report** → Create comprehensive Markdown analysis report

## ⚙️ Configuration

### PostgreSQL Setup

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

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | None |
| `OPENAI_MODEL` | GPT model to use | `gpt-4o-mini` |
| `OPENAI_BASE_URL` | Custom OpenAI endpoint | `https://api.openai.com/v1` |

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

**"OpenAI API Error"**
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

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

# Create development environment
python -m venv .venv
source .venv/bin/activate

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt
```

## 🔮 Roadmap

- [ ] **Docker support** with multi-stage builds for easy deployment and CI/CD integration
- [ ] **Multi-database support** (MySQL, SQLite)
- [ ] **Web dashboard** with interactive reports
- [ ] **Historical trend analysis** 
- [ ] **Query plan integration** with EXPLAIN analysis
- [ ] **Custom AI prompts** for domain-specific optimization
- [ ] **Slack/Discord notifications** for critical slow queries
- [ ] **Database schema context** for smarter recommendations

---

**Made with ❤️ for PostgreSQL performance optimization**