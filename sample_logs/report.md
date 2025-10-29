# PostgreSQL Performance Analysis Report

**Generated:** 2025-10-28 20:04:41

## Summary Statistics

- **Total Queries Analyzed:** 5
- **Unique Query Patterns:** 4
- **Average Duration:** 25825.13 ms
- **Max Duration:** 109234.02 ms
- **P95 Duration:** 90489.32 ms
- **P99 Duration:** 105485.08 ms
- **Total Time Spent:** 129.13 seconds

## Top Slow Queries (by Impact)

### Query #1

```sql
SELECT 
	    id,
	    random_number,
	    random_text,
	    SQRT(random_number::numeric) as sqrt_value,
	    SIN(random_number::numeric / 100000.0) as sin_value,
	    CASE 
	        WHEN random_number % 7 = 0 THEN 'LUCKY_SEVEN'
	        WHEN random_number % 13 = 0 THEN 'UNLUCKY_THIRTEEN'
	        WHEN random_number % 3 = 0 THEN 'DIVISIBLE_BY_THREE'
	        ELSE 'OTHER'
	    END as number_category,
	    ROW_NUMBER() OVER (ORDER BY random_number DESC) as rank_desc
	FROM large_test_table 
	WHERE r
```

- **Average Duration:** 55697.46 ms
- **Max Duration:** 109234.02 ms
- **Frequency:** 2 executions
- **Impact Score:** 111394.92

**AI Recommendation:**

1. **Root Cause of Slowness**: The query likely suffers from slow performance due to the lack of appropriate indexing on the `random_number` and `random_text` columns, leading to a full table scan for filtering and sorting.

2. **Optimization Recommendation**: Create a composite index on `(random_number, LENGTH(random_text))` to optimize the filtering conditions. Additionally, consider adding a separate index on `random_number` for the ORDER BY clause. 

   ```sql
   CREATE INDEX idx_random_number_text ON large_test_table (random_number) WHERE random_number > 950000;
   ```

3. **Estimated Performance Impact**: This optimization could potentially reduce query execution time by 50-70%, depending on the data distribution and the size of `large_test_table`.

---

### Query #2

```sql
SELECT DISTINCT
	    l1.random_number,
	    l1.random_text,
	    l1.created_at,
	    (SELECT COUNT(*) 
	     FROM large_test_table l2 
	     WHERE l2.random_number = l1.random_number) as duplicate_count
	FROM large_test_table l1
	WHERE l1.random_text LIKE '%data_555%'
	   OR l1.random_text LIKE '%data_777%'
	   OR l1.random_text LIKE '%data_999%'
	ORDER BY l1.random_number DESC
	LIMIT 30;
```

- **Average Duration:** 15510.52 ms
- **Max Duration:** 15510.52 ms
- **Frequency:** 1 executions
- **Impact Score:** 15510.52

**AI Recommendation:**

1. **Root Cause of Slowness**: The query is slow primarily due to the use of `LIKE` with leading wildcards (`%data_555%`), which prevents the use of indexes, resulting in a full table scan. Additionally, the correlated subquery for `duplicate_count` is executed for each row in the result set, further degrading performance.

2. **Optimization Recommendation**: 
   - Create a full-text index on `random_text` to improve search performance: 
     ```sql
     CREATE INDEX idx_random_text ON large_test_table USING gin(to_tsvector('english', random_text));
     ```
   - Rewrite the query using a Common Table Expression (CTE) to compute `duplicate_count` once:
     ```sql
     WITH counts AS (
         SELECT random_number, COUNT(*) AS duplicate_count
         FROM large_test_table
         GROUP BY random_number
     )
     SELECT DISTINCT l1.random_number, l1.random_text, l1.created_at, c.duplicate_count
     FROM large_test_table l1
     JOIN counts c ON l1.random_number = c.random_number
     WHERE l1.random_text LIKE '%data_555%' OR l1.random_text LIKE '%data_777%' OR l1.random_text LIKE '%data_999%'
     ORDER BY l1.random_number DESC
     LIMIT 30;
     ```

3. **Estimated Performance Impact**: This optimization could lead to a performance improvement of 50

---

### Query #3

```sql
SELECT DISTINCT
	    id,
	    random_number,
	    random_text,
	    LENGTH(random_text) as text_length,
	    POSITION('data_' in random_text) as data_position,
	    CASE 
	        WHEN random_text LIKE '%data_1%' AND random_text LIKE '%data_2%' THEN 'CONTAINS_1_AND_2'
	        WHEN random_text LIKE '%data_9%' THEN 'CONTAINS_9'
	        WHEN LENGTH(random_text) > 15 THEN 'LONG_TEXT'
	        ELSE 'OTHER'
	    END as text_category,
	    (SELECT COUNT(*) 
	     FROM large_test_table lt2 
	     WHER
```

- **Average Duration:** 2212.36 ms
- **Max Duration:** 2212.36 ms
- **Frequency:** 1 executions
- **Impact Score:** 2212.36

**AI Recommendation:**

1. **Root Cause of Slowness**: The query is slow primarily due to the use of `LIKE` with leading wildcards (`%`), which prevents the use of indexes, resulting in full table scans. Additionally, the correlated subquery for counting duplicates can significantly increase execution time.

2. **Optimization Recommendations**: 
   - **Indexing**: Create a GIN index on `random_text` for full-text search capabilities.
     ```sql
     CREATE INDEX idx_random_text ON large_test_table USING gin(random_text gin_trgm_ops);
     ```
   - **Rewrite the subquery**: Use a `JOIN` instead of a correlated subquery for counting duplicates.

3. **Estimated Performance Impact**: Implementing these changes could lead to a performance improvement of **50-70%**, depending on the data distribution and table size.

---

### Query #4

```sql
SELECT 
	    COUNT(*) as total_records,
	    ROUND(AVG(random_number::numeric), 2) as avg_number,
	    ROUND(STDDEV(random_number::numeric), 2) as stddev_number,
	    COUNT(DISTINCT (random_number % 1000)) as unique_modulo_values,
	    SUM(CASE WHEN random_number % 2 = 0 THEN 1 ELSE 0 END) as even_numbers,
	    SUM(CASE WHEN random_number % 2 = 1 THEN 1 ELSE 0 END) as odd_numbers,
	    ROUND(AVG(LENGTH(random_text)), 2) as avg_text_length
	FROM large_test_table 
	WHERE random_number BETWEEN 3000
```

- **Average Duration:** 7.87 ms
- **Max Duration:** 7.87 ms
- **Frequency:** 1 executions
- **Impact Score:** 7.87

**AI Recommendation:**

1. **Root Cause of Slowness**: The query may be slow due to a lack of appropriate indexing on the `random_number` column, leading to a full table scan, especially if `large_test_table` has a significant number of rows.

2. **Optimization Recommendation**: Create an index on the `random_number` column to speed up the filtering process. Use the following SQL command:  
   ```sql
   CREATE INDEX idx_random_number ON large_test_table (random_number);
   ```

3. **Estimated Performance Impact**: This optimization could reduce query execution time by 30-50%, depending on the table size and data distribution, as it allows PostgreSQL to quickly locate the relevant rows instead of scanning the entire table.

---
