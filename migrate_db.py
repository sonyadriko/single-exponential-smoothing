#!/usr/bin/env python3
"""Migration script to add missing columns to the database."""

import sqlite3
import os

DB_PATH = "sales_app.db"

def migrate():
    """Add missing columns to existing tables."""
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. Nothing to migrate.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if next_period_date column exists in forecasts table
        cursor.execute("PRAGMA table_info(forecasts)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'next_period_date' not in columns:
            print("Adding next_period_date column to forecasts table...")
            cursor.execute("ALTER TABLE forecasts ADD COLUMN next_period_date VARCHAR(20)")
            conn.commit()
            print("Done!")
        else:
            print("Column next_period_date already exists.")

        # Check all tables are created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables in database: {tables}")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
