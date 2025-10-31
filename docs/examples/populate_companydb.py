# Data population script for companydb
# This script uses Python and psycopg2 to efficiently insert millions of records into each table.
# Usage: python populate_companydb.py

import random
import string
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import execute_batch

DB_PARAMS = dict(
    dbname="companydb",
    user="postgres",
    password="yourpassword",
    host="localhost",
    port=5432,
)

NUM_DEPARTMENTS = 10
NUM_EMPLOYEES = 100_000
NUM_PRODUCTS = 1_000
NUM_CUSTOMERS = 500_000
NUM_SALES = 5_000_000
NUM_TICKETS = 100_000
NUM_LOGS = 2_000_000

random.seed(42)

def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def main():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    # Departments
    departments = [f"Department {i+1}" for i in range(NUM_DEPARTMENTS)]
    cur.executemany("INSERT INTO departments (name) VALUES (%s) ON CONFLICT DO NOTHING", [(d,) for d in departments])
    conn.commit()

    # Employees
    employees = []
    for i in range(NUM_EMPLOYEES):
        name = f"Employee_{i+1}"
        department_id = random.randint(1, NUM_DEPARTMENTS)
        hire_date = datetime(2000, 1, 1) + timedelta(days=random.randint(0, 9000))
        salary = round(random.uniform(40000, 200000), 2)
        employees.append((name, department_id, hire_date, salary))
    execute_batch(cur, "INSERT INTO employees (name, department_id, hire_date, salary) VALUES (%s, %s, %s, %s)", employees, page_size=10000)
    conn.commit()

    # Products
    categories = ["Electronics", "Clothing", "Books", "Home", "Toys"]
    products = []
    for i in range(NUM_PRODUCTS):
        name = f"Product_{i+1}"
        category = random.choice(categories)
        price = round(random.uniform(5, 2000), 2)
        products.append((name, category, price))
    execute_batch(cur, "INSERT INTO products (name, category, price) VALUES (%s, %s, %s)", products, page_size=1000)
    conn.commit()

    # Customers
    customers = []
    for i in range(NUM_CUSTOMERS):
        name = f"Customer_{i+1}"
        email = f"customer{i+1}@example.com"
        signup_date = datetime(2010, 1, 1) + timedelta(days=random.randint(0, 5000))
        customers.append((name, email, signup_date))
    execute_batch(cur, "INSERT INTO customers (name, email, signup_date) VALUES (%s, %s, %s)", customers, page_size=10000)
    conn.commit()

    # Sales
    sales = []
    for i in range(NUM_SALES):
        product_id = random.randint(1, NUM_PRODUCTS)
        customer_id = random.randint(1, NUM_CUSTOMERS)
        sale_date = datetime(2015, 1, 1) + timedelta(days=random.randint(0, 3650), seconds=random.randint(0, 86400))
        quantity = random.randint(1, 10)
        total_amount = round(quantity * products[product_id-1][2] * random.uniform(0.9, 1.1), 2)
        sales.append((product_id, customer_id, sale_date, quantity, total_amount))
        if len(sales) % 10000 == 0:
            execute_batch(cur, "INSERT INTO sales (product_id, customer_id, sale_date, quantity, total_amount) VALUES (%s, %s, %s, %s, %s)", sales)
            sales = []
    if sales:
        execute_batch(cur, "INSERT INTO sales (product_id, customer_id, sale_date, quantity, total_amount) VALUES (%s, %s, %s, %s, %s)", sales)
    conn.commit()

    # Support Tickets
    tickets = []
    for i in range(NUM_TICKETS):
        customer_id = random.randint(1, NUM_CUSTOMERS)
        created_at = datetime(2016, 1, 1) + timedelta(days=random.randint(0, 2000), seconds=random.randint(0, 86400))
        resolved_at = created_at + timedelta(days=random.randint(0, 30)) if random.random() < 0.8 else None
        status = random.choice(["open", "closed", "pending"])
        subject = f"Issue {random_string(10)}"
        description = f"Description {random_string(50)}"
        tickets.append((customer_id, created_at, resolved_at, status, subject, description))
    execute_batch(cur, "INSERT INTO support_tickets (customer_id, created_at, resolved_at, status, subject, description) VALUES (%s, %s, %s, %s, %s, %s)", tickets, page_size=1000)
    conn.commit()

    # Activity Logs
    logs = []
    for i in range(NUM_LOGS):
        employee_id = random.randint(1, NUM_EMPLOYEES)
        activity_type = random.choice(["login", "update", "delete", "create", "view"])
        activity_time = datetime(2017, 1, 1) + timedelta(days=random.randint(0, 1500), seconds=random.randint(0, 86400))
        details = f"{activity_type} {random_string(20)}"
        logs.append((employee_id, activity_type, activity_time, details))
        if len(logs) % 10000 == 0:
            execute_batch(cur, "INSERT INTO activity_logs (employee_id, activity_type, activity_time, details) VALUES (%s, %s, %s, %s)", logs)
            logs = []
    if logs:
        execute_batch(cur, "INSERT INTO activity_logs (employee_id, activity_type, activity_time, details) VALUES (%s, %s, %s, %s)", logs)
    conn.commit()

    cur.close()
    conn.close()
    print("Data population complete.")

if __name__ == "__main__":
    main()
