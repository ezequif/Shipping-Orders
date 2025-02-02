import sqlite3

DB_FILE = "data/orders.db"

def add_order(order_number, customer, product, quantity, shipping_with, truck_eta, status):
    """Adds or updates an order in the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO orders (order_number, customer, product, quantity, shipping_with, truck_eta, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(order_number) DO UPDATE SET
        customer=excluded.customer,
        product=excluded.product,
        quantity=excluded.quantity,
        shipping_with=excluded.shipping_with,
        truck_eta=excluded.truck_eta,
        status=excluded.status
    """, (order_number, customer, product, quantity, shipping_with, truck_eta, status))

    conn.commit()
    conn.close()
    print(f"✅ Order {order_number} updated successfully.")

def remove_order(order_number):
    """Removes an order from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM orders WHERE order_number = ?", (order_number,))
    conn.commit()
    conn.close()
    print(f"❌ Order {order_number} removed.")

# Example usage
if __name__ == "__main__":
    while True:
        print("\n📦 Order Management")
        print("1️⃣ Add/Update Order")
        print("2️⃣ Remove Order")
        print("3️⃣ Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            order_number = input("Order Number: ")
            customer = input("Customer Name: ")
            product = input("Finish Product Number: ")
            quantity = input("Quantity: ")
            shipping_with = input("Shipping With: ")
            truck_eta = input("Truck ETA: ")
            status = input("Status: ")
            add_order(order_number, customer, product, quantity, shipping_with, truck_eta, status)
        elif choice == "2":
            order_number = input("Order Number to Remove: ")
            remove_order(order_number)
        elif choice == "3":
            break
        else:
            print("❌ Invalid choice. Try again.")
