# demo_db_setup.py
# This makes a simple SQLite database for practice.
# You can replace this with your real database later.

import sqlite3
import os

DB_PATH = "demo.db"

def setup():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            price INTEGER,
            stock INTEGER
        )
    """)

    sample_data = [
        (1, "iPhone 15", 999, 50),
        (2, "Samsung Galaxy S24", 899, 30),
        (3, "Google Pixel 8", 799, 20),
        (4, "OnePlus 12", 699, 15),
    ]

    cursor.executemany(
        "INSERT INTO products VALUES (?, ?, ?, ?)",
        sample_data
    )

    conn.commit()
    conn.close()
    print(f"Demo database '{DB_PATH}' created with {len(sample_data)} products.")


if __name__ == "__main__":
    setup()
