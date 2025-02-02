import tkinter as tk
from tkinter import ttk
import sqlite3

# Database file location
DB_FILE = "data/orders.db"

# Color themes for different statuses
STATUS_COLORS = {
    "Shipped": "green",
    "In Transit": "yellow",
    "Delayed": "red",
    "Pending": "orange",
    "Processing": "blue"
}

class ShippingDisplayApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚚 Order Shipping Status")
        self.root.geometry("1400x700")  # Adjusted for larger displays
        self.root.configure(bg="black")

        # Create the UI components
        self.create_header()
        self.create_table()
        self.update_data()

    def create_header(self):
        """Creates the title header with a dark background."""
        header_frame = tk.Frame(self.root, bg="black")
        header_frame.pack(fill="x")

        title = tk.Label(
            header_frame, text="📦 Order Shipping Status",
            font=("Arial", 36, "bold"), fg="white", bg="black"
        )
        title.pack(pady=20)

    def create_table(self):
        """Creates the table structure with a dark theme and color-coded statuses."""
        columns = ("Order Number", "Customer", "Product", "Qty", "Shipping With", "Truck ETA", "Status")

        # ✅ Apply dark theme to Treeview (fix header bar issue)
        style = ttk.Style()
        style.theme_use("clam")  # Switch to 'clam' theme to allow customization

        style.configure("Treeview",
                        font=("Arial", 18),
                        rowheight=40,
                        background="black",
                        foreground="white",
                        fieldbackground="black")  # Ensures table matches the background

        # ✅ Set header (column titles) to a dark background
        style.configure("Treeview.Heading",
                        font=("Arial", 20, "bold"),
                        background="black",
                        foreground="white",
                        relief="flat")  # Removes white bar effect

        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=10, style="Treeview")

        # Define column headings with centered text
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=200)

        self.tree.pack(expand=True, fill="both", padx=40, pady=20)

    def update_data(self):
        """Fetch data from the database and update the table in real-time with color coding."""
        self.tree.delete(*self.tree.get_children())  # Clear existing data

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders ORDER BY truck_eta ASC")
        orders = cursor.fetchall()
        conn.close()

        # Insert new data with color-coded status
        for order in orders:
            order_number, customer, product, quantity, shipping_with, truck_eta, status = order

            # Color coding for status
            tag = STATUS_COLORS.get(status, "white")
            self.tree.insert("", "end", values=order, tags=(tag,))

        # Apply tag colors
        for status, color in STATUS_COLORS.items():
            self.tree.tag_configure(color, foreground=color)

        # Refresh every 5 seconds
        self.root.after(5000, self.update_data)

# Run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = ShippingDisplayApp(root)
    root.mainloop()
