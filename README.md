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
- ⚡ **Batch Processing**: Efficiently analyzes multiple queries in one run
- 🛠️ **Production Ready**: Robust error handling, logging, and configuration options

## 🚀 Quick Start

### 1. Installation

```bash
git clone https://github.com/gmartinez-dbai/slow-query-doctor.git
cd slow-query-doctor
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configuration

Set your OpenAI API key:

```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

Or create a `.env` file:

```bash
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env
```

### 3. Run Analysis

```bash
python -m slowquerydoctor your_postgres.log
```

## 📖 Detailed Usage

### Basic Usage

```bash
# Analyze default top 5 queries
python -m slowquerydoctor postgres.log

# Analyze top 10 queries with custom output
python -m slowquerydoctor postgres.log --output custom_report.md --top-n 10

# Full example with all options
python -m slowquerydoctor /var/log/postgresql/slow.log \
    --output reports/performance_analysis.md \
    --top-n 15
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `log_file` | Path to PostgreSQL slow query log file | Required |
| `--output` | Output report file path | `reports/report.md` |
| `--top-n` | Number of top queries to analyze | `5` |

### Example Output

The tool generates a comprehensive Markdown report including:

- **Summary Statistics**: Total queries, execution patterns, duration percentiles
- **Top Slow Queries**: Ranked by impact score with full details
- **AI Recommendations**: Specific optimization suggestions for each query

## 🗄️ PostgreSQL Configuration

### Enable Slow Query Logging

To capture slow queries, configure PostgreSQL logging:

```sql
-- Set minimum duration to log (100ms recommended for production)
ALTER SYSTEM SET log_min_duration_statement = 100;

-- Include query details in logs
ALTER SYSTEM SET log_statement = 'all';

-- Apply configuration
SELECT pg_reload_conf();
```

### Alternative: Session-Level Configuration

For testing or temporary analysis:

```sql
-- Enable for current session only
SET log_min_duration_statement = 100;
```

### Log File Location

Find your PostgreSQL log files:

```sql
-- Check current log file location
SHOW log_directory;
SHOW log_filename;

-- Or check data directory
SHOW data_directory;
```

Common locations:
- **Ubuntu/Debian**: `/var/log/postgresql/`
- **CentOS/RHEL**: `/var/lib/pgsql/data/log/`
- **macOS (Homebrew)**: `/usr/local/var/log/`
- **Docker**: Check container logs or mounted volumes

## 🏗️ Architecture

### Project Structure

```
slow-query-doctor/
├── slowquerydoctor/           # Main package
│   ├── __init__.py           # Package initialization
│   ├── __main__.py           # Entry point for -m execution
│   ├── main.py               # CLI interface and orchestration
│   ├── parser.py             # PostgreSQL log parsing logic
│   ├── analyzer.py           # Query analysis and ranking
│   ├── llm_client.py         # OpenAI API integration
│   └── report_generator.py   # Markdown report generation
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── LICENSE                  # MIT License
```

### Data Flow

1. **Parse**: Extract slow queries from PostgreSQL logs
2. **Normalize**: Group similar queries (parameter normalization)
3. **Analyze**: Calculate impact scores and rank queries
4. **Generate AI Recommendations**: Use OpenAI to analyze each query
5. **Report**: Create comprehensive Markdown report

### Key Components

#### Parser (`parser.py`)
- Extracts timestamp, duration, and query text from logs
- Handles various PostgreSQL log formats
- Robust error handling for malformed entries

#### Analyzer (`analyzer.py`)
- Normalizes queries by replacing literals with placeholders
- Groups similar queries for better analysis
- Calculates impact scores: `average_duration × execution_frequency`

#### LLM Client (`llm_client.py`)
- Integrates with OpenAI GPT-4o-mini for cost-effective analysis
- Generates specific optimization recommendations
- Includes query statistics in prompts for context-aware suggestions

#### Report Generator (`report_generator.py`)
- Creates professional Markdown reports
- Includes summary statistics and detailed query analysis
- Embeds AI recommendations with proper formatting

## ⚙️ Configuration Options

### LLM Configuration

The tool uses sensible defaults but can be customized:

```python
from slowquerydoctor.llm_client import LLMConfig, LLMClient

config = LLMConfig(
    model="gpt-4o-mini",      # Model to use
    temperature=0.3,          # Response creativity (0.0-1.0)
    max_tokens=300,          # Maximum response length
    timeout=30               # Request timeout in seconds
)

client = LLMClient(config)
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |

## 📊 Sample Report Output

```markdown
# PostgreSQL Performance Analysis Report

**Generated:** 2025-10-28 10:30:15

## Summary Statistics

- **Total Queries Analyzed:** 1,247
- **Unique Query Patterns:** 23
- **Average Duration:** 156.7 ms
- **Max Duration:** 2,845.3 ms
- **P95 Duration:** 450.2 ms
- **P99 Duration:** 892.1 ms
- **Total Time Spent:** 195.4 seconds

## Top Slow Queries (by Impact)

### Query #1

```sql
SELECT u.*, p.title, p.content FROM users u 
JOIN posts p ON u.id = p.user_id 
WHERE u.created_at > ? ORDER BY u.created_at DESC LIMIT ?
```

- **Average Duration:** 234.5 ms
- **Max Duration:** 567.2 ms  
- **Frequency:** 89 executions
- **Impact Score:** 20,870.5

**AI Recommendation:**

The primary bottleneck is the ORDER BY clause on `users.created_at` without an index. 
Create a composite index: `CREATE INDEX idx_users_created_posts ON users(created_at DESC) 
INCLUDE (id)`. This should reduce execution time by 60-80% and eliminate the expensive 
sort operation. Consider adding `posts(user_id)` index if not already present.

---
```

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/gmartinez-dbai/slow-query-doctor.git
cd slow-query-doctor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Run with pytest (when tests are added)
pytest tests/

# Run specific module
python -m slowquerydoctor --help
```

### Code Style

The project follows standard Python conventions:
- PEP 8 style guide
- Type hints where appropriate
- Comprehensive docstrings
- Descriptive variable names

## 🚨 Troubleshooting

### Common Issues

#### "No slow queries found"
- Verify `log_min_duration_statement` is configured
- Check log file path and permissions
- Ensure PostgreSQL is generating logs in expected format

#### "OpenAI API key not found"
- Set `OPENAI_API_KEY` environment variable
- Verify API key is valid and has sufficient credits
- Check network connectivity to OpenAI API

#### "Error parsing log file"
- Verify log file format matches PostgreSQL slow query format
- Check file encoding (UTF-8 expected)
- Ensure file is not corrupted or truncated

### Log Format Requirements

The tool expects PostgreSQL logs with `log_min_duration_statement` entries in this format:

```
2025-10-28 10:15:30.123 UTC [12345]: [1-1] user=postgres,db=myapp LOG: duration: 156.789 ms statement: SELECT ...
```

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.11 or higher
- **Memory**: 512 MB RAM (for typical log files)
- **Storage**: Varies by log file size
- **Network**: Internet access for OpenAI API

### Supported Platforms
- Linux (Ubuntu 20.04+, CentOS 7+)
- macOS 10.15+
- Windows 10/11

### Dependencies
- `pandas`: Data manipulation and analysis
- `openai`: OpenAI API client
- `python-dotenv`: Environment variable management
- `tqdm`: Progress bars (optional)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Giovanni Martinez**
- GitHub: [@gmartinez-dbai](https://github.com/gmartinez-dbai)

## 🙏 Acknowledgments

- OpenAI for providing the GPT API
- PostgreSQL community for excellent documentation
- Python data science ecosystem (pandas, numpy)

## License

MIT License - Copyright (c) 2025 Giovanni Martinez

## Author

Giovanni Martinez
