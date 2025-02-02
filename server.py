import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO
import sqlite3

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")  # ✅ Enable WebSockets

DB_FILE = "data/orders.db"

def get_orders():
    """Retrieve all orders from the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT order_number, customer, product, quantity, shipping_with, status FROM orders")
    orders = cursor.fetchall()
    conn.close()
    return orders

from flask_socketio import SocketIO

socketio = SocketIO(app, cors_allowed_origins="*")  # ✅ Enable WebSockets

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Admin Panel - Manage Orders."""
    if request.method == "POST":
        order_number = request.form.get("order_number")
        customer = request.form.get("customer")
        product = request.form.get("product")
        quantity = request.form.get("quantity")
        shipping_with = request.form.get("shipping_with")
        status = request.form.get("status")

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO orders (order_number, customer, product, quantity, shipping_with, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (order_number, customer, product, quantity, shipping_with, status))
        conn.commit()
        conn.close()

        # ✅ Emit real-time update to all warehouse monitors
        socketio.emit("update_orders", {"orders": get_orders()})
        return redirect(url_for("admin"))

    orders = get_orders()
    return render_template("admin.html", orders=orders)


@app.route("/update_order", methods=["POST"])
def update_order():
    """Update an order from the Manage Orders page."""
    data = request.json
    order_number = data.get("order_number")
    customer = data.get("customer")
    product = data.get("product")
    quantity = data.get("quantity")
    shipping_with = data.get("shipping_with")
    status = data.get("status")

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE orders SET customer=?, product=?, quantity=?, shipping_with=?, status=?
    WHERE order_number=?
    """, (customer, product, quantity, shipping_with, status, order_number))
    conn.commit()
    conn.close()

    # ✅ Emit real-time update after order edit
    socketio.emit("update_orders", {"orders": get_orders()})
    return jsonify({"message": "Order updated successfully"})

@app.route("/delete_order/<order_number>", methods=["GET"])
def delete_order(order_number):
    """Delete an order."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE order_number = ?", (order_number,))
    conn.commit()
    conn.close()

    # ✅ Emit real-time update after order deletion
    socketio.emit("update_orders", {"orders": get_orders()})
    return jsonify({"message": "Order deleted successfully"})

@app.route("/manage_orders")
def manage_orders():
    """Manage Orders Page."""
    orders = get_orders()
    return render_template("manage_orders.html", orders=orders)

@app.route("/warehouse")
def warehouse():
    """Warehouse Order Shipping Status Page"""
    orders = get_orders()
    return render_template("warehouse.html", orders=orders)
@app.route("/")
def home():
    return redirect(url_for("warehouse"))  # ✅ Redirect root to warehouse page

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # ✅ Use Render's PORT
    socketio.run(app, host="0.0.0.0", port=port)

