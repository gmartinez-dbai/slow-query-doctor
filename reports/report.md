# PostgreSQL Performance Analysis Report

**Generated:** 2025-11-01 12:41:27

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

1. **Root Cause of Slowness**: The use of `ILIKE` with leading wildcards (`%error%` and `%fail%`) prevents the use of any index on the `description` column, resulting in a full table scan.

2. **Optimization Recommendation**: Create a full-text search index on the `description` column. You can do this by using the `tsvector` type to store searchable text and then rewriting the query to use `to_tsvector` and `plainto_tsquery` for improved performance.

   ```sql
   CREATE INDEX idx_description_fulltext ON support_tickets USING GIN(to_tsvector('english', description));
   ```

   Rewrite the query as:
   ```sql
   SELECT * FROM support_tickets WHERE to_tsvector('english', description) @@ plainto_tsquery('error | fail') LIMIT 1000;
   ```

3. **Estimated Performance Impact**: This change could lead to a performance improvement of 70-90%, significantly reducing execution time.

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

1. **Root Cause of Slowness**: The query's performance is likely hindered by the subquery in the JOIN condition, which executes for each row in the `sales` table, causing inefficient row filtering and increased computational overhead.

2. **Optimization Recommendation**: Rewrite the JOIN condition to eliminate the subquery. Instead, precompute the total number of employees and use it in a derived table or a CTE. For example:
   ```sql
   WITH emp_count AS (SELECT COUNT(*) AS total FROM employees)
   SELECT e.id, e.name, SUM(s.total_amount) AS total_sales,
          RANK() OVER (ORDER BY SUM(s.total_amount) DESC) AS sales_rank
   FROM employees e
   JOIN sales s ON e.id = (s.customer_id % (SELECT total FROM emp_count)) + 1
   GROUP BY e.id, e.name
   ORDER BY total_sales DESC LIMIT 100;
   ```

3. **Estimated Performance Impact**: This change could result in a performance improvement of 40-60%, depending on the size of the `sales` table.

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

1. **Root Cause of Slowness**: The subquery `(SELECT COUNT(*) FROM support_tickets t WHERE t.customer_id = c.id)` is executed for each customer, resulting in a Cartesian product effect that significantly increases execution time.

2. **Optimization Recommendation**: Rewrite the query using a `JOIN` with a `GROUP BY` clause to aggregate ticket counts in a single pass. Example:
   ```sql
   SELECT c.id, c.name, COALESCE(t.ticket_count, 0) AS ticket_count
   FROM customers c
   LEFT JOIN (
       SELECT customer_id, COUNT(*) AS ticket_count
       FROM support_tickets
       GROUP BY customer_id
   ) t ON c.id = t.customer_id
   ORDER BY ticket_count DESC LIMIT 100;
   ```

3. **Estimated Performance Impact**: This optimization could lead to a performance improvement of 70-90%, as it reduces the number of subquery executions from one per customer to a single aggregated result.

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

1. **Most likely root cause of slowness**: The query is likely slow due to the lack of appropriate indexing on the `sale_date` column, which is used in the `ORDER BY` clause. Sorting a large dataset without an index can lead to significant performance degradation.

2. **Specific, actionable optimization recommendation**: Create an index on the `sale_date` column in the `sales` table. Additionally, consider creating a composite index on `(customer_id, product_id)` if these columns are frequently used in joins.

   ```sql
   CREATE INDEX idx_sale_date ON sales(sale_date);
   ```

3. **Estimated performance impact**: This optimization could lead to a performance improvement of 30-50%, significantly reducing the query execution time.

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

1. **Most likely root cause of slowness**: The subquery in the `WHERE` clause retrieves up to 10,000 rows from `activity_logs`, which can be inefficient, especially if `activity_logs` lacks proper indexing. This can lead to a full table scan, slowing down the overall execution.

2. **Specific, actionable optimization recommendation**: Add an index on `activity_logs(activity_type)` to speed up the filtering process. Additionally, consider rewriting the query using a `JOIN` instead of a subquery to avoid the potential overhead of the `IN` clause.

   ```sql
   UPDATE employees e
   SET salary = salary * 1.05
   FROM (SELECT employee_id FROM activity_logs WHERE activity_type = 'update' LIMIT 10000) a
   WHERE e.id = a.employee_id;
   ```

3. **Estimated performance impact**: 30-50% faster, depending on the size of `activity_logs` and existing indexes.

---
