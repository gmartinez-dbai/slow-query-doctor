
# Technical Debt Log

This file tracks known technical debt and areas of improvement that are deferred for future versions.


## v0.1.x - PostgreSQL Focus

- Log parser now supports multi-line queries, unusual characters, and multiple formats (plain, CSV, JSON), but may still have edge cases with highly custom log formats or rare encodings.
- EXPLAIN plan analysis only supports PostgreSQL output.
- Limited support for multi-file analysis.
- Config file support is present, but not all CLI options are yet configurable via YAML.

## Future Versions (v0.4.0+)

- Modular design needed to support MySQL, SQL Server, and Oracle.
- Need to refactor log parsing to handle diverse database log formats.
- Expand EXPLAIN plan parser to support other databases.
- Implement anomaly detection and ML-based learning models.

