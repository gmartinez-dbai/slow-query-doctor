# [← Back to Index](index.md)
# PostgreSQL: Setup & Example Usage

This page provides a complete guide for setting up PostgreSQL slow query logging, generating example logs, and analyzing them with Slow Query Doctor.

---

## Table of Contents

- [1. Enable Slow Query Logging in PostgreSQL](#1-enable-slow-query-logging-in-postgresql)
- [2. Find Your Log Files](#2-find-your-log-files)
- [3. Generate Example Slow Queries](#3-generate-example-slow-queries)
- [4. Collect and Analyze Logs](#4-collect-and-analyze-logs)
- [5. Supported Log Formats](#5-supported-log-formats)
- [6. Example Output](#6-example-output)
- [7. Troubleshooting](#7-troubleshooting)

---

## 1. Enable Slow Query Logging in PostgreSQL

Edit your `postgresql.conf` (commonly at `/etc/postgresql/*/main/postgresql.conf` or `/usr/local/var/postgres/postgresql.conf`):

```conf
logging_collector = on
log_directory = 'log'                # or an absolute path
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000    # log queries slower than 1 second (adjust as needed)
log_statement = 'none'
log_duration = off
log_line_prefix = '%m [%p] %u@%d '
log_destination = 'stderr'
```

Restart PostgreSQL after making changes:

```sh
sudo systemctl restart postgresql
# or
pg_ctl restart
```

### Enable for Current Session (optional)

```sql
SET log_min_duration_statement = 1000;
```

---

## 2. Find Your Log Files

Check the `log_directory` you set above. Common locations:
- `/var/log/postgresql/`
- `/usr/local/var/postgres/log/`
- `/opt/homebrew/var/postgresql@*/log/`

---

## 3. Generate Example Slow Queries

Run slow queries in your database to generate log entries. For example:

```text
SELECT * FROM employees ORDER BY random() LIMIT 10000;
SELECT COUNT(*) FROM sales WHERE amount > 1000;
```

---

## 4. Collect and Analyze Logs

Copy the relevant log file to your project directory's `sample_logs/` folder (create it if it doesn't exist). For example:

```sh
mkdir -p sample_logs
cp /var/log/postgresql/postgresql-2025-10-31_*.log ./sample_logs/
```

**Sample log file:**

- `sample_logs/postgresql-2025-10-31_122408.log.txt` (plain text, multi-line queries supported)

### Analyze with Slow Query Doctor

```sh
# With uv (recommended)
uv run python -m slowquerydoctor sample_logs/postgresql-2025-10-31_122408.log.txt

# Traditional approach
python -m slowquerydoctor sample_logs/postgresql-2025-10-31_122408.log.txt
```

### With Verbose Output

```sh
# With uv (recommended)
uv run python -m slowquerydoctor sample_logs/postgresql-2025-10-31_122408.log.txt --verbose

# Traditional approach
python -m slowquerydoctor sample_logs/postgresql-2025-10-31_122408.log.txt --verbose
```

### Specify Output Report Path

```sh
# With uv (recommended)
uv run python -m slowquerydoctor sample_logs/postgresql-2025-10-31_122408.log.txt --output reports/my_report.md

# Traditional approach
python -m slowquerydoctor sample_logs/postgresql-2025-10-31_122408.log.txt --output reports/my_report.md
```

---

## 5. Supported Log Formats

Slow Query Doctor currently supports the following PostgreSQL log formats:

- Plain text PostgreSQL logs (default)
- CSV logs (`log_destination = 'csvlog'`)
- JSON logs (extensions and custom setups)

Ensure your logs include durations and statements for accurate analysis.

---

## 6. Example Output

You can generate a Markdown report summarizing top slow queries, their durations, frequency, and AI-powered recommendations. See the main README for a detailed sample report.

---

## 7. Troubleshooting

- Ensure `log_min_duration_statement` is set appropriately (e.g., `1000` for 1s)
- Confirm log file path and permissions
- Use `--verbose` to get more details during analysis
