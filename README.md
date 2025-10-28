# Slow Query Doctor

AI-powered PostgreSQL slow query analyzer.

## Quick Start

    git clone https://github.com/gmartinez-dbai/slow-query-doctor.git
    cd slow-query-doctor
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    export OPENAI_API_KEY='your-key-here'
    python -m slowquerydoctor sample_postgres.log

## What It Does

- Parses PostgreSQL slow query logs
- Identifies top slow queries by impact
- Generates AI-powered optimization recommendations
- Creates Markdown reports

## Usage

    python -m slowquerydoctor postgres.log --output report.md --top-n 5

## PostgreSQL Setup

Enable slow query logging:

    ALTER SYSTEM SET log_min_duration_statement = 100;
    SELECT pg_reload_conf();

## Requirements

- Python 3.11+
- OpenAI API key
- PostgreSQL with log_min_duration_statement enabled

## Project Structure

    slow-query-doctor/
    ├── slowquerydoctor/
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── main.py
    │   ├── parser.py
    │   ├── analyzer.py
    │   ├── llm_client.py
    │   └── report_generator.py
    ├── requirements.txt
    ├── README.md
    └── LICENSE

## License

MIT License - Copyright (c) 2025 Giovanni Martinez

## Author

Giovanni Martinez
