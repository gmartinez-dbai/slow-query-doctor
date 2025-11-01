# PostgreSQL Slow Query Logging Setup for companydb

## 1. Edit postgresql.conf

Find your PostgreSQL config file (commonly at /etc/postgresql/*/main/postgresql.conf or /usr/local/var/postgres/postgresql.conf).

Set or update the following parameters:

```
logging_collector = on
log_directory = 'log'                # or an absolute path
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000    # log queries slower than 1 second (adjust as needed)
log_statement = 'none'
log_duration = off
```

Restart PostgreSQL after making changes:
```
sudo systemctl restart postgresql
# or
pg_ctl restart
```

## 2. Enable for Current Session (optional)

You can also enable slow query logging for your session:

```
SET log_min_duration_statement = 1000;
```

## 3. Find Your Log Files

Check the log_directory you set above. Common locations:
- /var/log/postgresql/
- /usr/local/var/postgres/log/
- /opt/homebrew/var/postgresql@*/log/


## 4. Run Example Slow Queries

See [Usage Examples](../examples.md) for example slow queries to run and analyze.


## 5. Collect and Analyze Logs

Copy the relevant log file to your project directory, e.g.:
```
cp /var/log/postgresql/postgresql-2025-10-31_*.log ./docs/sample_logs/
```


Analyze with Slow Query Doctor (see [Usage Examples](../examples.md) for more):
```
python -m slowquerydoctor docs/sample_logs/postgresql-2025-10-31_*.log --output report.md
```

See [Usage Examples](../examples.md) and the README for more options and advanced usage.

---

## Example and Setup Scripts

- SQL schema: `docs/examples/companydb_schema.sql`
- Data population: `docs/examples/populate_companydb.py`
- Example slow queries: `docs/examples/example_slow_queries.sql`
