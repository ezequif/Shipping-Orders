import sqlite3

DB_FILE = "data/orders.db"


def create_database():
    """Creates the database and orders table."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_number TEXT PRIMARY KEY,
        customer TEXT,
        product TEXT,
        quantity INTEGER,
        shipping_with TEXT,
        truck_eta TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    print("✅ Database initialized successfully.")
