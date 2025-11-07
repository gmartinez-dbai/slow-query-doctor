# MySQL Sample Logs

**Status**: 🚧 Coming in v0.4.0 (Q3 2026)

This directory will contain sample MySQL slow query log files for testing and demonstration purposes.

## Planned MySQL Log Support

### Slow Query Log Format
```sql
# Time: 2025-10-28T19:31:23.123456Z
# User@Host: app_user[app_user] @ [192.168.1.100]
# Thread_id: 12345  Schema: ecommerce_db  QC_hit: No
# Query_time: 15.123456  Lock_time: 0.000123  Rows_sent: 1500  Rows_examined: 45000000
# Rows_affected: 0  Bytes_sent: 125000
SET timestamp=1698526283;
SELECT p.product_id, p.product_name, p.price, AVG(r.rating), COUNT(r.review_id)
FROM products p 
LEFT JOIN reviews r ON p.product_id = r.product_id
WHERE p.category_id IN (1,2,3,4,5,6,7,8,9,10)
  AND p.created_date > '2024-01-01'
GROUP BY p.product_id, p.product_name, p.price
HAVING COUNT(r.review_id) > 100
ORDER BY AVG(r.rating) DESC, COUNT(r.review_id) DESC
LIMIT 50;
```

### Sample Query Types (Planned)
- **Large table scans** without proper indexing
- **Complex JOINs** across multiple large tables  
- **Subqueries in SELECT/WHERE** clauses
- **GROUP BY** operations on large datasets
- **ORDER BY** without covering indexes
- **Full-text searches** without proper MATCH() usage

## Configuration for MySQL Logs

Enable slow query logging in MySQL:

```sql
-- Enable slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL slow_query_log_file = '/var/log/mysql/mysql-slow.log';
SET GLOBAL long_query_time = 1.0;  -- Log queries > 1 second
SET GLOBAL log_queries_not_using_indexes = 'ON';
```

Or in `my.cnf`:
```ini
[mysqld]
slow_query_log = 1
slow_query_log_file = /var/log/mysql/mysql-slow.log
long_query_time = 1.0
log_queries_not_using_indexes = 1
log_slow_admin_statements = 1
```

## Early Feedback Welcome

**If you're a MySQL user**, we'd love to hear from you:
- What MySQL-specific optimization challenges do you face?
- What log formats do you primarily use?
- Which MySQL versions should we prioritize?
- Any specific performance patterns we should detect?

📧 Contact: [Create an issue](https://github.com/iqtoolkit/slow-query-doctor/issues) with label `mysql-feedback`

---

**Timeline**: MySQL support planned for v0.4.0 (Q3 2026)  
**Current Focus**: Perfecting PostgreSQL analysis with v0.2.0 configurable AI providers  
**AI Note**: Current v0.1.x requires OpenAI API key; v0.2.0+ will support local Ollama models