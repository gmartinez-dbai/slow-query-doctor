# Table of Contents

- [1. Enable Slow Query Logging in PostgreSQL](#1-enable-slow-query-logging-in-postgresql)
- [2. Find Your Log Files](#2-find-your-log-files)
- [3. Generate Example Slow Queries](#3-generate-example-slow-queries)
- [4. Collect and Analyze Logs](#4-collect-and-analyze-logs)
- [5. Supported Log Formats](#5-supported-log-formats)
- [6. Example Output](#6-example-output)
- [7. Troubleshooting](#7-troubleshooting)
# [← Back to Index](index.md)
# Slow Query Doctor: Setup & Example Usage

This page provides a complete guide for setting up PostgreSQL slow query logging, generating example logs, and analyzing them with Slow Query Doctor.

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

```sql
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
python -m slowquerydoctor sample_logs/postgresql-2025-10-31_122408.log.txt
```

### With Verbose Output

```sh
python -m slowquerydoctor sample_logs/postgresql-2025-10-31_122408.log.txt --verbose
```

### Specify Output Report Path

```sh
python -m slowquerydoctor sample_logs/postgresql-2025-10-31_122408.log.txt --output reports/my_report.md
```

### Analyze Top N Slow Queries

```sh
python -m slowquerydoctor sample_logs/postgresql-2025-10-31_122408.log.txt --top-n 10
```

### Using Ollama for Local AI Recommendations

To use Ollama instead of OpenAI for AI-powered recommendations:

1. **Install and start Ollama** (see [Ollama Local Setup](ollama-local.md)):
   ```sh
   # Install from https://ollama.com/download
   ollama serve
   ```

2. **Pull a model**:
   ```sh
   ollama pull llama2
   ```

3. **Create or update `.slowquerydoctor.yml`** in your project directory:
   ```yaml
   llm_provider: ollama
   ollama_model: llama2
   top_n: 5
   output: reports/report.md
   ```

4. **Run the analysis** (no API key needed):
   ```sh
   python -m slowquerydoctor sample_logs/postgresql-2025-10-31_122408.log.txt
   ```

Ollama runs completely locally—no data leaves your machine. For custom Ollama hosts:
```yaml
llm_provider: ollama
ollama_model: llama2
ollama_host: http://192.168.1.100:11434
```

---

## 5. Supported Log Formats

- **Plain PostgreSQL logs** (default)
- **CSV**: `--log-format csv`
- **JSON**: `--log-format json`

---

## 6. Example Output

After running, you'll see a progress bar and periodic messages like:

```
Parsing log entries:  45%|███████████████▌         | 900/2000 [00:01<00:01, 800.00entry/s]
Examined 100 log entries...
Examined 200 log entries...
...
✅ Report saved to: reports/report.md
```

The generated report includes:
- Top slow queries
- Query statistics
- AI-powered recommendations

### Execution Debug Screenshot

![Verbose CLI run showing progress output and debug details](img/2025-11-01_12-50-27.png)

> The screenshot is tall so you may need to scroll to view the full debugging session capture.

---

## 7. Troubleshooting

- If you see `No slow query entries matched the expected pattern`, check your PostgreSQL log settings and ensure slow query logging is enabled.
- For large logs, the progress bar and periodic messages help track parsing progress.

---
