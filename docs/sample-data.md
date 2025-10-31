# 📂 Sample Data & Usage

See the [Project README](../README.md#sample-log-files) for a summary.

## Sample Log Files

- Located in the `sample_logs/` directory
- Example: `sample_logs/postgresql-2025-10-28_192816.log.txt`
- `.txt` extension is used to avoid `.gitignore` exclusions


## Example Usage

```bash
python -m slowquerydoctor sample_logs/postgresql-2025-10-28_192816.log.txt --output report.md
# Supports multi-line queries and multiple log formats (plain, CSV, JSON)
```

## Why Use Sample Data?

- Test the tool without setting up your own PostgreSQL logs
- See real-world slow query patterns and AI recommendations
- Validate installation and configuration
