# PostgreSQL Performance Analysis Report

**Generated:** 2025-11-01 12:35:14

## Summary Statistics

- **Total Queries Analyzed:** 15.0
- **Unique Query Patterns:** 11.0
- **Average Duration:** 512.66 ms
- **Max Duration:** 2626.64 ms
- **P95 Duration:** 2095.05 ms
- **P99 Duration:** 2520.32 ms
- **Total Time Spent:** 7.69 seconds

## Top Slow Queries (by Impact)

### Query #1

```sql
SELECT * FROM support_tickets WHERE description ILIKE '%error%' OR description ILIKE '%fail%' LIMIT 1000;
```

- **Average Duration:** 2626.64 ms
- **Max Duration:** 2626.64 ms
- **Frequency:** 1 executions
- **Impact Score:** 2626.64

**AI Recommendation:**

1. **Root Cause of Slowness**: The use of `ILIKE` with leading wildcards (`%error%` and `%fail%`) prevents the use of any indexes, resulting in a full table scan, which is inefficient for large datasets.

2. **Optimization Recommendation**: Create a full-text search index on the `description` column. This can be done by creating a `GIN` index with a `tsvector` representation of the text. Rewrite the query to use `to_tsvector` and `to_tsquery` for full-text search.

   Example:
   ```sql
   CREATE INDEX idx_description_fulltext ON support_tickets USING GIN (to_tsvector('english', description));
   SELECT * FROM support_tickets WHERE to_tsvector('english', description) @@ to_tsquery('error | fail') LIMIT 1000;
   ```

3. **Estimated Performance Impact**: This optimization could lead to a performance improvement of 70-90%, significantly reducing query execution time.

---

### Query #2

```sql
SELECT e.id, e.name, SUM(s.total_amount) AS total_sales,
	       RANK() OVER (ORDER BY SUM(s.total_amount) DESC) AS sales_rank
	FROM employees e
	JOIN sales s ON e.id = (s.customer_id % (SELECT COUNT(*) FROM employees)) + 1
	GROUP BY e.id, e.name
	ORDER BY total_sales DESC LIMIT 100;
```

- **Average Duration:** 1867.23 ms
- **Max Duration:** 1867.23 ms
- **Frequency:** 1 executions
- **Impact Score:** 1867.23

**AI Recommendation:**

1. **Root Cause of Slowness**: The subquery in the JOIN condition `(s.customer_id % (SELECT COUNT(*) FROM employees)) + 1` is executed for every row in the `sales` table, leading to inefficient row processing and potentially a large Cartesian product before filtering.

2. **Optimization Recommendation**: Rewrite the query to precompute the employee count outside the JOIN. Use a CTE (Common Table Expression) or a derived table to calculate the employee count once, and then reference it in the JOIN condition. Additionally, ensure there are indexes on `sales.customer_id` and `employees.id`.

3. **Estimated Performance Impact**: This optimization could lead to a performance improvement of 50-70%, significantly reducing the execution time.

---

### Query #3

```sql
SELECT c.id, c.name, (
	    SELECT COUNT(*) FROM support_tickets t WHERE t.customer_id = c.id
	) AS ticket_count
	FROM customers c
	ORDER BY ticket_count DESC LIMIT 100;
```

- **Average Duration:** 1751.24 ms
- **Max Duration:** 1751.24 ms
- **Frequency:** 1 executions
- **Impact Score:** 1751.24

**AI Recommendation:**

1. **Most Likely Root Cause of Slowness**: The subquery in the SELECT clause executes for each row in the `customers` table, leading to a performance bottleneck due to multiple scans of the `support_tickets` table.

2. **Specific, Actionable Optimization Recommendation**: Rewrite the query using a JOIN and GROUP BY to aggregate ticket counts in a single scan of the `support_tickets` table. Additionally, create an index on `support_tickets.customer_id` to speed up the count operation.

   ```sql
   SELECT c.id, c.name, COUNT(t.id) AS ticket_count
   FROM customers c
   LEFT JOIN support_tickets t ON t.customer_id = c.id
   GROUP BY c.id, c.name
   ORDER BY ticket_count DESC
   LIMIT 100;
   ```

3. **Estimated Performance Impact**: This optimization could result in a performance improvement of 70-90%, significantly reducing execution time.

---

### Query #4

```sql
SELECT s.id, s.sale_date, s.quantity, s.total_amount, c.name AS customer_name, p.name AS product_name, p.category
	FROM sales s
	JOIN customers c ON s.customer_id = c.id
	JOIN products p ON s.product_id = p.id
	ORDER BY s.sale_date DESC LIMIT 10000;
```

- **Average Duration:** 423.97 ms
- **Max Duration:** 424.83 ms
- **Frequency:** 2 executions
- **Impact Score:** 847.94

**AI Recommendation:**

1. **Root Cause of Slowness**: The query is likely slow due to the lack of proper indexing on the `sale_date` column, which is used in the `ORDER BY` clause. Sorting a large dataset without an index can lead to significant performance degradation.

2. **Optimization Recommendation**: Create an index on the `sale_date` column in the `sales` table:  
   ```sql
   CREATE INDEX idx_sales_sale_date ON sales(sale_date);
   ```

3. **Estimated Performance Impact**: Adding this index could improve query performance by approximately 30-50%, especially if the `sales` table contains a large number of records, as it will allow PostgreSQL to efficiently sort the results.

---

### Query #5

```sql
UPDATE employees SET salary = salary * 1.05 WHERE id IN (
	    SELECT employee_id FROM activity_logs WHERE activity_type = 'update' LIMIT 10000
	);
```

- **Average Duration:** 287.54 ms
- **Max Duration:** 287.54 ms
- **Frequency:** 1 executions
- **Impact Score:** 287.54

**AI Recommendation:**

1. **Root Cause of Slowness**: The subquery in the `WHERE` clause (`SELECT employee_id FROM activity_logs WHERE activity_type = 'update' LIMIT 10000`) can be slow due to a lack of indexing on `activity_type`, leading to a full table scan.

2. **Optimization Recommendation**: Create an index on the `activity_logs` table for the `activity_type` column. Additionally, consider rewriting the query using a `JOIN` instead of a subquery to improve performance:

   ```sql
   UPDATE employees
   SET salary = salary * 1.05
   FROM (SELECT employee_id FROM activity_logs WHERE activity_type = 'update' LIMIT 10000) AS subquery
   WHERE employees.id = subquery.employee_id;
   ```

3. **Estimated Performance Impact**: This optimization could lead to a performance improvement of 50-70%, significantly reducing the average duration of the query.

---
