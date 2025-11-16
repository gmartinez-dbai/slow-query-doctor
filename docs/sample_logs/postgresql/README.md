# PostgreSQL Sample Logs

This directory contains sample PostgreSQL slow query log files that you can use to try Slow Query Doctor, validate parsing, and demo report generation.

## Included Sample Files

The following samples are provided to cover a variety of slow query patterns and durations:

- `postgresql-2025-10-28_192816.log.txt`
  - Mixed workload with JOINs, LIKE filters, sorting, and limit
  - Contains a few long‑running statements suitable for top‑N analysis
- `postgresql-2025-10-31_122408.log.txt`
  - Heavier workload with window functions and aggregations
  - Useful for demonstrating AI recommendations around indexing and query shape
- `postgresql-2025-11-01_000000.log.txt`
  - Additional variety with nested queries and sequential scans

> File names follow the typical PostgreSQL rotation pattern `postgresql-%Y-%m-%d_%H%M%S.log` and use a `.txt` extension to ensure GitHub renders them as plain text.

## How to Analyze These Samples

Using the recommended uv workflow:

```bash
# Generate a report from a sample log
uv run python -m slowquerydoctor docs/sample_logs/postgresql/postgresql-2025-10-28_192816.log.txt \
  --output reports/sample_report.md

# Analyze only the top 5 slowest queries
uv run python -m slowquerydoctor docs/sample_logs/postgresql/postgresql-2025-10-28_192816.log.txt \
  --output reports/top5_report.md \
  --top-n 5

# Increase analysis depth (token budget) and enable verbose output
uv run python -m slowquerydoctor docs/sample_logs/postgresql/postgresql-2025-10-28_192816.log.txt \
  --output reports/detailed_report.md \
  --max-tokens 200 \
  --verbose
```

If you prefer, you can copy one of these files to a local `sample_logs/` folder in the repo root and use the shorter paths shown in the main README.

## Enable PostgreSQL Slow Query Logging (on your system)

To generate your own logs for analysis, enable slow query logging in `postgresql.conf`:

```conf
# Log queries taking longer than 1 second
log_min_duration_statement = 1000

# Enable logging collector
logging_collector = on

# Set log directory (relative to data_directory)
log_directory = 'log'

# Log file naming pattern
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'

# (Optional) Enrich log line prefix for more context
log_line_prefix = '%m [%p] %u@%d %h '
```

Typical log locations by platform can be found in the main README under "Log File Locations".

## Log Format Notes

- Plain text PostgreSQL server logs with slow statements are supported.
- Multi‑line SQL statements are handled.
- The analyzer detects duration, timing windows, and extracts representative queries.

## Contributing Additional Samples

Have interesting anonymized PostgreSQL slow logs to share (e.g., complex window functions, heavy JOIN graphs, or pathological LIKE/ILIKE patterns)? Contributions help improve test coverage and recommendations.

- Open an issue and attach sanitized samples: https://github.com/iqtoolkit/slow-query-doctor/issues
- Please remove or anonymize sensitive identifiers before sharing.

---

Status: ✅ PostgreSQL support is ready to use. MongoDB is in priority development for v0.2.0, and MySQL/SQL Server are planned.
