#!/usr/bin/env python3
"""
Fix SQLite date format from "DD-Mon-YY" to "YYYY-MM-DD"
Run this before migrating to MySQL, or use migrate_to_mysql.py directly
"""

import sqlite3
from datetime import datetime

DB_PATH = 'sales_app.db'


def parse_date(date_str: str) -> str | None:
    """Convert DD-Mon-YY to YYYY-MM-DD"""
    if not date_str:
        return None

    # Already in ISO format
    if len(date_str) == 10 and date_str[4] == '-':
        return date_str

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
            # Handle 2-digit year (assume 20xx)
            year_int = int(year)
            year_full = 2000 + year_int if year_int < 100 else year_int
            return f"{year_full}-{month_num}-{day.zfill(2)}"
    except Exception:
        pass

    return date_str


def fix_sales():
    print("Fixing sales table...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Get all sales
    cur.execute("SELECT id, date FROM sales")
    sales = cur.fetchall()

    updated = 0
    for sale_id, date_str in sales:
        new_date = parse_date(date_str)
        if new_date != date_str:
            cur.execute("UPDATE sales SET date = ? WHERE id = ?", (new_date, sale_id))
            updated += 1
            print(f"  Sale {sale_id}: {date_str} -> {new_date}")

    conn.commit()
    conn.close()
    print(f"✅ Updated {updated} sales records\n")


def fix_forecasts():
    print("Fixing forecasts table...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, next_period_date FROM forecasts WHERE next_period_date IS NOT NULL")
    forecasts = cur.fetchall()

    updated = 0
    for forecast_id, date_str in forecasts:
        new_date = parse_date(date_str)
        if new_date != date_str:
            cur.execute("UPDATE forecasts SET next_period_date = ? WHERE id = ?", (new_date, forecast_id))
            updated += 1
            print(f"  Forecast {forecast_id}: {date_str} -> {new_date}")

    conn.commit()
    conn.close()
    print(f"✅ Updated {updated} forecast records\n")


def verify():
    print("Verifying dates...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT date FROM sales LIMIT 5")
    print("Sample sales dates:")
    for row in cur.fetchall():
        print(f"  {row[0]}")

    conn.close()


if __name__ == "__main__":
    print("=" * 50)
    print("SQLite Date Format Fixer")
    print("=" * 50 + "\n")

    fix_sales()
    fix_forecasts()
    verify()

    print("\n✅ All dates converted to ISO format (YYYY-MM-DD)")
    print("\nNow you can:")
    print("  1. Test with SQLite: uvicorn main:app --reload")
    print("  2. Or migrate to MySQL: python migrate_to_mysql.py")
