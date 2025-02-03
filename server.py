import os
import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # ✅ Enable WebSockets

DB_FILE = "data/orders.db"  # ✅ Database file

# ✅ Function to get a database connection (prevents "database locked" errors)
def get_db_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

# ✅ Function to retrieve all orders from the database
def get_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT order_number, customer, product, quantity, shipping_with, status FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return orders

# ✅ Function to ensure database exists
def create_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_number TEXT PRIMARY KEY,
        customer TEXT NOT NULL,
        product TEXT NOT NULL,
        quantity TEXT NOT NULL,  -- ✅ Allows text (letters + numbers)
        shipping_with TEXT NOT NULL,
        status TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

# ✅ Call this function at startup
create_database()

# ✅ Admin Panel - Manage Orders
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        order_number = request.form.get("order_number")
        customer = request.form.get("customer")
        product = request.form.get("product")
        quantity = request.form.get("quantity")  # ✅ Allows letters & numbers
        shipping_with = request.form.get("shipping_with")
        status = request.form.get("status")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO orders (order_number, customer, product, quantity, shipping_with, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (order_number, customer, product, quantity, shipping_with, status))
        conn.commit()
        conn.close()

        # ✅ Emit real-time update to all warehouse monitors
        socketio.emit("update_orders", {"orders": get_orders()}, namespace="/")
        return redirect(url_for("admin"))

    orders = get_orders()
    return render_template("admin.html", orders=orders)

# ✅ Edit Order
@app.route("/update_order", methods=["POST"])
def update_order():
    data = request.json
    order_number = data.get("order_number")
    customer = data.get("customer")
    product = data.get("product")
    quantity = data.get("quantity")
    shipping_with = data.get("shipping_with")
    status = data.get("status")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE orders SET customer=?, product=?, quantity=?, shipping_with=?, status=?
    WHERE order_number=?
    """, (customer, product, quantity, shipping_with, status, order_number))
    conn.commit()
    conn.close()

    # ✅ Emit real-time update
    socketio.emit("update_orders", {"orders": get_orders()}, namespace="/")
    return jsonify({"message": "Order updated successfully"})

# ✅ Delete Order
@app.route("/delete_order/<order_number>", methods=["GET"])
def delete_order(order_number):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE order_number = ?", (order_number,))
    conn.commit()
    conn.close()

    # ✅ Emit real-time update
    socketio.emit("update_orders", {"orders": get_orders()}, namespace="/")
    return jsonify({"message": "Order deleted successfully"})

# ✅ Manage Orders Page
@app.route("/manage_orders")
def manage_orders():
    orders = get_orders()
    return render_template("manage_orders.html", orders=orders)

# ✅ Warehouse Order Shipping Status Page
@app.route("/warehouse")
def warehouse():
    orders = get_orders()
    return render_template("warehouse.html", orders=orders)

# ✅ Redirect Root URL to Warehouse Monitor
@app.route("/")
def home():
    return redirect(url_for("warehouse"))

# ✅ Run Flask-SocketIO on Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # ✅ Uses Render's assigned port
    socketio.run(app, host="0.0.0.0", port=port, allow_unsafe_werkzeug=True)
