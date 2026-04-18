#!/usr/bin/env python3
"""
Migration script: SQLite to MySQL with date format conversion
Converts dates from "DD-Mon-YY" format to proper DATE type
"""

import sqlite3
import pymysql
from datetime import datetime
from config import get_settings

settings = get_settings()

# Parse DD-Mon-YY format (e.g., "31-May-25")
def parse_date(date_str: str) -> str | None:
    if not date_str:
        return None

    # If already in ISO format, return as-is
    if '-' in date_str and len(date_str) == 10 and date_str[4] == '-':
        return date_str

    # Parse DD-Mon-YY format
    try:
        months = {
            'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
        }
        parts = date_str.split('-')
        if len(parts) == 3:
            day, month, year = parts
            month_num = months.get(month, '01')
            year_full = 2000 + int(year) if int(year) < 100 else int(year)
            return f"{year_full}-{month_num}-{day.zfill(2)}"
    except Exception as e:
        print(f"Warning: Could not parse date '{date_str}': {e}")

    return date_str  # Fallback


def parse_mysql_url(url: str):
    """Parse MySQL URL: mysql+pymysql://user:password@host:port/database"""
    # Remove prefix
    url = url.replace('mysql+pymysql://', '').replace('mysql://', '')

    # Split user:password from host:port/database
    if '@' in url:
        user_pass, host_db = url.split('@')
        user, password = user_pass.split(':') if ':' in user_pass else ('root', '')

        # Split host from database
        if '/' in host_db:
            host_port, database = host_db.split('/')
            host = host_port.split(':')[0] if ':' in host_port else host_port
        else:
            host = host_port.split(':')[0] if ':' in host_port else host_port
            database = 'sales_app'
    else:
        user, password, host, database = 'root', '', 'localhost', 'sales_app'

    return user, password, host, database


def migrate():
    print("Starting migration: SQLite -> MySQL")

    # SQLite connection
    sqlite_conn = sqlite3.connect('sales_app.db')
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    # Parse MySQL URL
    user, password, host, database = parse_mysql_url(settings.database_url)
    print(f"\nConnecting to MySQL: {user}@{host}/{database}")

    # MySQL connection
    mysql_conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        charset='utf8mb4'
    )
    mysql_cur = mysql_conn.cursor()

    # Create database if not exists
    mysql_cur.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    mysql_cur.execute(f"USE {database}")

    # Drop existing tables if any
    print("Dropping existing MySQL tables...")
    tables = ['forecasts', 'sales', 'products', 'users']
    for table in tables:
        mysql_cur.execute(f"DROP TABLE IF EXISTS {table}")
    mysql_conn.commit()

    # Create tables with proper schema
    print("Creating MySQL tables...")

    mysql_cur.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            hashed_password VARCHAR(255),
            role VARCHAR(20),
            INDEX idx_username (username)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    mysql_cur.execute("""
        CREATE TABLE products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            created_at DATETIME,
            INDEX idx_name (name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    mysql_cur.execute("""
        CREATE TABLE sales (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            product_name VARCHAR(100) NOT NULL,
            qty INT NOT NULL,
            INDEX idx_date (date),
            INDEX idx_product (product_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    mysql_cur.execute("""
        CREATE TABLE forecasts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_name VARCHAR(100),
            created_at DATETIME NOT NULL,
            created_by INT,
            alpha FLOAT,
            product_name VARCHAR(100),
            next_period_forecast FLOAT,
            next_period_date DATE,
            mape FLOAT,
            calculation_steps JSON,
            INDEX idx_project (project_name),
            FOREIGN KEY (created_by) REFERENCES users(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)

    mysql_conn.commit()

    # Migrate Users
    print("Migrating users...")
    sqlite_cur.execute("SELECT * FROM users")
    users = sqlite_cur.fetchall()
    for user in users:
        mysql_cur.execute(
            "INSERT INTO users (id, username, hashed_password, role) VALUES (%s, %s, %s, %s)",
            (user['id'], user['username'], user['hashed_password'], user['role'])
        )
    mysql_conn.commit()
    print(f"  Migrated {len(users)} users")

    # Migrate Products
    print("Migrating products...")
    sqlite_cur.execute("SELECT * FROM products")
    products = sqlite_cur.fetchall()
    for product in products:
        mysql_cur.execute(
            "INSERT INTO products (id, name, created_at) VALUES (%s, %s, %s)",
            (product['id'], product['name'], product['created_at'])
        )
    mysql_conn.commit()
    print(f"  Migrated {len(products)} products")

    # Migrate Sales with date conversion
    print("Migrating sales (converting dates)...")
    sqlite_cur.execute("SELECT * FROM sales")
    sales = sqlite_cur.fetchall()
    converted = 0
    for sale in sales:
        new_date = parse_date(sale['date'])
        if new_date != sale['date']:
            converted += 1
        mysql_cur.execute(
            "INSERT INTO sales (id, date, product_name, qty) VALUES (%s, %s, %s, %s)",
            (sale['id'], new_date, sale['product_name'], sale['qty'])
        )
    mysql_conn.commit()
    print(f"  Migrated {len(sales)} sales ({converted} dates converted)")

    # Migrate Forecasts
    print("Migrating forecasts...")
    sqlite_cur.execute("SELECT * FROM forecasts")
    forecasts = sqlite_cur.fetchall()
    converted_forecast = 0
    for forecast in forecasts:
        new_date = parse_date(forecast['next_period_date']) if forecast['next_period_date'] else None
        if new_date and new_date != forecast['next_period_date']:
            converted_forecast += 1
        mysql_cur.execute(
            """INSERT INTO forecasts (id, project_name, created_at, created_by, alpha, product_name,
               next_period_forecast, next_period_date, mape, calculation_steps)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (forecast['id'], forecast['project_name'], forecast['created_at'],
             forecast['created_by'], forecast['alpha'], forecast['product_name'],
             forecast['next_period_forecast'], new_date, forecast['mape'],
             forecast['calculation_steps'])
        )
    mysql_conn.commit()
    print(f"  Migrated {len(forecasts)} forecasts ({converted_forecast} dates converted)")

    # Close connections
    sqlite_conn.close()
    mysql_conn.close()

    print("\n✅ Migration complete!")
    print("\nNext steps:")
    print("1. Create .env file with MySQL credentials")
    print("2. Run: uvicorn main:app --reload")
    print("3. Optionally backup SQLite: mv sales_app.db sales_app.db.backup")


if __name__ == "__main__":
    migrate()
