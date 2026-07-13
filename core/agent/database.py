"""
database.py — Mock SQLite database for HearMeOut's agentic backend.

Creates three tables (customers, orders, transactions) with seed data so the
LangGraph agent has something real to query and mutate via tools.

Run directly to (re)build the database from scratch:
    python database.py
"""

import sqlite3
import os
from contextlib import contextmanager
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hearmeout.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS customers (
    customer_id     TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    email           TEXT NOT NULL UNIQUE,
    phone           TEXT,
    account_status  TEXT NOT NULL DEFAULT 'active'   -- active, suspended, closed
);

CREATE TABLE IF NOT EXISTS orders (
    order_id        TEXT PRIMARY KEY,
    customer_id     TEXT NOT NULL,
    product         TEXT NOT NULL,
    amount          REAL NOT NULL,
    status          TEXT NOT NULL DEFAULT 'delivered', -- placed, shipped, delivered, cancelled, refunded
    order_date      TEXT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id  TEXT PRIMARY KEY,
    order_id        TEXT NOT NULL,
    customer_id     TEXT NOT NULL,
    type            TEXT NOT NULL,                     -- payment, refund
    amount          REAL NOT NULL,
    status          TEXT NOT NULL DEFAULT 'completed',  -- pending, completed, failed
    transaction_date TEXT NOT NULL,
    reason          TEXT,
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);
"""

CUSTOMERS = [
    ("cust_001", "Priya Sharma", "priya.sharma@example.com", "+91-9820011223", "active"),
    ("cust_002", "Daniel Reyes", "daniel.reyes@example.com", "+1-415-555-0192", "active"),
    ("cust_003", "Amara Okafor", "amara.okafor@example.com", "+234-802-555-0110", "suspended"),
    ("cust_004", "Wei Zhang", "wei.zhang@example.com", "+86-138-0013-8000", "active"),
]

def _d(days_ago: int) -> str:
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

ORDERS = [
    ("ord_1001", "cust_001", "Wireless Earbuds Pro",      79.99, "delivered", _d(12)),
    ("ord_1002", "cust_001", "USB-C Fast Charger",        24.50, "shipped",   _d(2)),
    ("ord_1003", "cust_002", "Smart Home Hub",           129.00, "delivered", _d(30)),
    ("ord_1004", "cust_002", "Ergonomic Keyboard",         89.99, "cancelled", _d(5)),
    ("ord_1005", "cust_003", "4K Webcam",                  59.99, "delivered", _d(45)),
    ("ord_1006", "cust_004", "Noise Cancelling Headphones", 199.99, "placed",  _d(1)),
]

TRANSACTIONS = [
    ("txn_5001", "ord_1001", "cust_001", "payment", 79.99, "completed", _d(12), None),
    ("txn_5002", "ord_1002", "cust_001", "payment", 24.50, "completed", _d(2), None),
    ("txn_5003", "ord_1003", "cust_002", "payment", 129.00, "completed", _d(30), None),
    ("txn_5004", "ord_1004", "cust_002", "payment", 89.99, "completed", _d(5), None),
    ("txn_5005", "ord_1004", "cust_002", "refund", 89.99, "completed", _d(4), "order cancelled by customer"),
    ("txn_5006", "ord_1005", "cust_003", "payment", 59.99, "completed", _d(45), None),
    ("txn_5007", "ord_1006", "cust_004", "payment", 199.99, "completed", _d(1), None),
]


@contextmanager
def get_connection():
    """Context-managed SQLite connection with row access by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(reset: bool = False):
    """Create tables and seed mock data. If reset=True, wipes existing data first."""
    if reset and os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    with get_connection() as conn:
        conn.executescript(SCHEMA)

        existing = conn.execute("SELECT COUNT(*) AS c FROM customers").fetchone()["c"]
        if existing > 0:
            return  # already seeded

        conn.executemany(
            "INSERT INTO customers (customer_id, name, email, phone, account_status) VALUES (?, ?, ?, ?, ?)",
            CUSTOMERS,
        )
        conn.executemany(
            "INSERT INTO orders (order_id, customer_id, product, amount, status, order_date) VALUES (?, ?, ?, ?, ?, ?)",
            ORDERS,
        )
        conn.executemany(
            "INSERT INTO transactions (transaction_id, order_id, customer_id, type, amount, status, transaction_date, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            TRANSACTIONS,
        )


if __name__ == "__main__":
    init_db(reset=True)
    with get_connection() as conn:
        n_cust = conn.execute("SELECT COUNT(*) AS c FROM customers").fetchone()["c"]
        n_ord = conn.execute("SELECT COUNT(*) AS c FROM orders").fetchone()["c"]
        n_txn = conn.execute("SELECT COUNT(*) AS c FROM transactions").fetchone()["c"]
    print(f"Database rebuilt at {DB_PATH}")
    print(f"  customers: {n_cust}, orders: {n_ord}, transactions: {n_txn}")