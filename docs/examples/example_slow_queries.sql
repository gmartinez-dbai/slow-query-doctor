-- Example slow queries for companydb to trigger slow query logging and showcase all features

-- 1. Large aggregation (total sales per product)
SELECT product_id, SUM(quantity) AS total_qty, SUM(total_amount) AS total_sales
FROM sales
GROUP BY product_id
ORDER BY total_sales DESC;

-- 2. Complex join (sales with customer and product info)
SELECT s.id, s.sale_date, s.quantity, s.total_amount, c.name AS customer_name, p.name AS product_name, p.category
FROM sales s
JOIN customers c ON s.customer_id = c.id
JOIN products p ON s.product_id = p.id
ORDER BY s.sale_date DESC LIMIT 10000;

-- 3. Correlated subquery (customers with most tickets)
SELECT c.id, c.name, (
    SELECT COUNT(*) FROM support_tickets t WHERE t.customer_id = c.id
) AS ticket_count
FROM customers c
ORDER BY ticket_count DESC LIMIT 100;

-- 4. Window function (rank employees by total sales)
SELECT e.id, e.name, SUM(s.total_amount) AS total_sales,
       RANK() OVER (ORDER BY SUM(s.total_amount) DESC) AS sales_rank
FROM employees e
JOIN sales s ON e.id = (s.customer_id % (SELECT COUNT(*) FROM employees)) + 1
GROUP BY e.id, e.name
ORDER BY total_sales DESC LIMIT 100;

-- 5. Pattern matching (search in support ticket descriptions)
SELECT * FROM support_tickets WHERE description ILIKE '%error%' OR description ILIKE '%fail%' LIMIT 1000;

-- 6. Filtering and sorting on non-indexed columns
SELECT * FROM sales WHERE total_amount > 1000 ORDER BY sale_date ASC LIMIT 10000;

-- 7. Multi-table update (simulate a slow update)
UPDATE employees SET salary = salary * 1.05 WHERE id IN (
    SELECT employee_id FROM activity_logs WHERE activity_type = 'update' LIMIT 10000
);

-- 8. Multi-table delete (simulate a slow delete)
DELETE FROM support_tickets WHERE customer_id IN (
    SELECT id FROM customers WHERE signup_date < '2012-01-01' LIMIT 10000
);
