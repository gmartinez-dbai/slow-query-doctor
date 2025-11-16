# Data population script for companydb
# This script uses Python and psycopg (psycopg3) to efficiently insert millions of
# records into each table.
# Usage: python populate_companydb.py

import random
import string
from decimal import Decimal
from datetime import datetime, timedelta
import psycopg


DB_PARAMS = dict(
    dbname="companydb",
    # user="postgres",
    # password="yourpassword",
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
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def main():
    print("Connecting to database with params:", DB_PARAMS)
    try:
        conn = psycopg.connect(**DB_PARAMS)
        cur = conn.cursor()

        print("\nPopulating departments...")
        departments = [f"Department {i+1}" for i in range(NUM_DEPARTMENTS)]
        print("  Inserting departments...")
        cur.executemany(
            "INSERT INTO departments (name) VALUES (%s) ON CONFLICT DO NOTHING",
            [(d,) for d in departments],
        )
        conn.commit()
        print("  Fetching department IDs...")
        cur.execute("SELECT id FROM departments ORDER BY id")
        department_ids = [row[0] for row in cur.fetchall()]
        print(f"Inserted {len(department_ids)} departments.")

        print("\nPopulating employees...")
        employees = []
        for i in range(NUM_EMPLOYEES):
            name = f"Employee_{i+1}"
            department_id = random.choice(department_ids)
            hire_date = datetime(2000, 1, 1) + timedelta(days=random.randint(0, 9000))
            salary = round(random.uniform(40000, 200000), 2)
            employees.append((name, department_id, hire_date, salary))
            if (i + 1) % 10000 == 0:
                print(f"  Prepared {i+1} employees...")
        print("  Inserting employees...")
        cur.executemany(
            "INSERT INTO employees (name, department_id, hire_date, salary) "
            "VALUES (%s, %s, %s, %s)",
            employees,
        )
        conn.commit()
        print("  Fetching employee IDs...")
        cur.execute("SELECT id FROM employees ORDER BY id")
        employee_ids = [row[0] for row in cur.fetchall()]
        print(f"Inserted {len(employee_ids)} employees.")

        print("\nPopulating products...")
        categories = ["Electronics", "Clothing", "Books", "Home", "Toys"]
        products = []
        for i in range(NUM_PRODUCTS):
            name = f"Product_{i+1}"
            category = random.choice(categories)
            price = round(random.uniform(5, 2000), 2)
            products.append((name, category, price))
        print("  Inserting products...")
        cur.executemany(
            "INSERT INTO products (name, category, price) VALUES (%s, %s, %s)", products
        )
        conn.commit()
        print("  Fetching product IDs and prices...")
        cur.execute("SELECT id, price FROM products ORDER BY id")
        product_rows = cur.fetchall()
        product_ids = [row[0] for row in product_rows]
        product_prices = {row[0]: row[1] for row in product_rows}
        print(f"Inserted {len(product_ids)} products.")

        print("\nPopulating customers...")
        print("  Generating customer data...")
        customers = []
        used_emails = set()
        for i in range(NUM_CUSTOMERS):
            name = f"Customer_{i+1}"
            # Retry logic for unique email
            for attempt in range(10):
                email = (
                    f"customer{i+1}@example.com"
                    if attempt == 0
                    else f"customer{i+1}_{random_string(6)}@example.com"
                )
                if email not in used_emails:
                    used_emails.add(email)
                    break
            else:
                raise Exception(f"Failed to generate unique email for customer {i+1}")
            signup_date = datetime(2010, 1, 1) + timedelta(days=random.randint(0, 5000))
            customers.append((name, email, signup_date))
            if (i + 1) % 10000 == 0:
                print(f"  Prepared {i+1} customers...")
        before_count = None
        try:
            cur.execute("SELECT COUNT(*) FROM customers")
            before_count = cur.fetchone()[0]
        except Exception:
            pass
        print("  Inserting customers...")
        cur.executemany(
            "INSERT INTO customers (name, email, signup_date) VALUES (%s, %s, %s) "
            "ON CONFLICT (email) DO NOTHING",
            customers,
        )
        conn.commit()
        print("  Fetching customer IDs...")
        cur.execute("SELECT id FROM customers ORDER BY id")
        customer_ids = [row[0] for row in cur.fetchall()]
        inserted_count = len(customer_ids) - (
            before_count if before_count is not None else 0
        )
        if inserted_count < len(customers):
            print(
                f"[WARNING] {len(customers) - inserted_count} duplicate customers "
                f"were skipped due to existing emails."
            )
        print(
            f"Inserted {inserted_count} new customers. "
            f"Total in table: {len(customer_ids)}."
        )

        print("\nPopulating sales...")
        sales = []
        for i in range(NUM_SALES):
            product_id = random.choice(product_ids)
            customer_id = random.choice(customer_ids)
            sale_date = datetime(2015, 1, 1) + timedelta(
                days=random.randint(0, 3650), seconds=random.randint(0, 86400)
            )
            quantity = random.randint(1, 10)
            price = product_prices[product_id]
            multiplier = Decimal(str(random.uniform(0.9, 1.1)))
            total_amount = (Decimal(quantity) * price * multiplier).quantize(
                Decimal("0.01")
            )
            sales.append((product_id, customer_id, sale_date, quantity, total_amount))
            if (i + 1) % 100000 == 0:
                print(f"  Prepared {i+1} sales...")
            if len(sales) % 10000 == 0:
                print(f"    Inserting sales batch at {i+1}... ({len(sales)} records)")
                cur.executemany(
                    "INSERT INTO sales (product_id, customer_id, sale_date, quantity, "
                    "total_amount) VALUES (%s, %s, %s, %s, %s)",
                    sales,
                )
                sales = []
        if sales:
            print(f"    Inserting final sales batch... ({len(sales)} records)")
            cur.executemany(
                "INSERT INTO sales (product_id, customer_id, sale_date, quantity, "
                "total_amount) VALUES (%s, %s, %s, %s, %s)",
                sales,
            )
        conn.commit()
        print(f"Inserted {NUM_SALES} sales.")

        print("\nPopulating support tickets...")
        tickets = []
        for i in range(NUM_TICKETS):
            customer_id = random.choice(customer_ids)
            created_at = datetime(2016, 1, 1) + timedelta(
                days=random.randint(0, 2000), seconds=random.randint(0, 86400)
            )
            resolved_at = (
                created_at + timedelta(days=random.randint(0, 30))
                if random.random() < 0.8
                else None
            )
            status = random.choice(["open", "closed", "pending"])
            subject = f"Issue {random_string(10)}"
            description = f"Description {random_string(50)}"
            tickets.append(
                (customer_id, created_at, resolved_at, status, subject, description)
            )
            if (i + 1) % 10000 == 0:
                print(f"  Prepared {i+1} tickets...")
        print("  Inserting support tickets...")
        cur.executemany(
            "INSERT INTO support_tickets (customer_id, created_at, resolved_at, "
            "status, subject, description) VALUES (%s, %s, %s, %s, %s, %s)",
            tickets,
        )
        conn.commit()
        print(f"Inserted {NUM_TICKETS} support tickets.")

        print("\nPopulating activity logs...")
        logs = []
        for i in range(NUM_LOGS):
            employee_id = random.choice(employee_ids)
            activity_type = random.choice(
                ["login", "update", "delete", "create", "view"]
            )
            activity_time = datetime(2017, 1, 1) + timedelta(
                days=random.randint(0, 1500), seconds=random.randint(0, 86400)
            )
            details = f"{activity_type} {random_string(20)}"
            logs.append((employee_id, activity_type, activity_time, details))
            if (i + 1) % 100000 == 0:
                print(f"  Prepared {i+1} logs...")
            if len(logs) % 10000 == 0:
                print(f"    Inserting logs batch at {i+1}... ({len(logs)} records)")
                cur.executemany(
                    "INSERT INTO activity_logs (employee_id, activity_type, "
                    "activity_time, details) VALUES (%s, %s, %s, %s)",
                    logs,
                )
                logs = []
        if logs:
            print(f"    Inserting final logs batch... ({len(logs)} records)")
            cur.executemany(
                "INSERT INTO activity_logs (employee_id, activity_type, activity_time, "
                "details) VALUES (%s, %s, %s, %s)",
                logs,
            )
        conn.commit()
        print(f"Inserted {NUM_LOGS} activity logs.")

        cur.close()
        conn.close()
        print("\nData population complete.")
    except Exception as e:
        print("\n[ERROR] Data population failed:", e)


if __name__ == "__main__":
    main()
