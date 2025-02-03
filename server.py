import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO
import eventlet

# ✅ Ensure eventlet is patched first
eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # ✅ Enable WebSockets

DB_FILE = "data/orders.db"  # ✅ Database path

# ✅ Function to create database & tables if missing
def create_database():
    """Creates the database and tables if they don't exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_number TEXT PRIMARY KEY,
        customer TEXT NOT NULL,
        product TEXT NOT NULL,
        quantity TEXT NOT NULL,  -- ✅ Allows letters & numbers
        shipping_with TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# ✅ Call this function at startup
create_database()

# ✅ Function to get a database connection (prevents locking)
def get_db_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

# ✅ Function to get all orders from the database
def get_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return orders

# ✅ Root route (redirects to Warehouse Monitor)
@app.route("/")
def home():
    return redirect(url_for("warehouse"))

# ✅ Warehouse Monitor route
@app.route("/warehouse")
def warehouse():
    orders = get_orders()
    return render_template("warehouse.html", orders=orders)

# ✅ Admin Panel route
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        order_number = request.form.get("order_number")
        customer = request.form.get("customer")
        product = request.form.get("product")
        quantity = request.form.get("quantity")  # ✅ Now allows text input
        shipping_with = request.form.get("shipping_with")
        status = request.form.get("status")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (order_number, customer, product, quantity, shipping_with, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (order_number, customer, product, quantity, shipping_with, status))
            conn.commit()
            conn.close()

            # ✅ Emit real-time update to all warehouse monitors
            socketio.emit("update_orders", {"orders": get_orders()})

        except sqlite3.IntegrityError:
            return "Error: Order number must be unique!", 400

        return redirect(url_for("admin"))

    orders = get_orders()
    return render_template("admin.html", orders=orders)

# ✅ API route to fetch orders (for debugging)
@app.route("/api/orders")
def api_orders():
    return jsonify({"orders": get_orders()})

# ✅ Flask-SocketIO runs on Render with assigned port
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # ✅ Uses Render's assigned port
    socketio.run(app, host="0.0.0.0", port=port)
