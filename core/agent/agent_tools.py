"""
agent_tools.py — Real tools the HearMeOut LangGraph agent can call.

Each function is decorated with @tool so LangGraph/LangChain can expose it to
the LLM as a callable function. Docstrings double as the tool description the
model sees, so keep them precise — the model decides when to call a tool
based on this text.
"""

import uuid
from datetime import datetime
from langchain_core.tools import tool

from core.agent.database import get_connection


@tool
def check_order_status(order_id: str) -> str:
    """Look up the current status of an order by its order ID (e.g. 'ord_1001').

    Returns the order's product, amount, status, and order date. Use this
    whenever a customer asks 'where is my order' or 'what's the status of
    order X'.
    """
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM orders WHERE order_id = ?", (order_id,)
        ).fetchone()

    if row is None:
        return f"No order found with ID '{order_id}'. Please double check the order ID."

    return (
        f"Order {row['order_id']}: {row['product']} (${row['amount']:.2f}), "
        f"status = '{row['status']}', ordered on {row['order_date']}."
    )


@tool
def check_account(email: str) -> str:
    """Look up a customer's account details and order history by email address.

    Returns account status (active/suspended/closed) and a summary of their
    recent orders. Use this to verify who the customer is or to answer
    'what's the status of my account' / 'what have I ordered'.
    """
    with get_connection() as conn:
        customer = conn.execute(
            "SELECT * FROM customers WHERE email = ?", (email,)
        ).fetchone()

        if customer is None:
            return f"No account found for email '{email}'."

        orders = conn.execute(
            "SELECT order_id, product, amount, status, order_date FROM orders "
            "WHERE customer_id = ? ORDER BY order_date DESC",
            (customer["customer_id"],),
        ).fetchall()

    order_lines = [
        f"  - {o['order_id']}: {o['product']} (${o['amount']:.2f}), {o['status']}, {o['order_date']}"
        for o in orders
    ] or ["  (no orders on file)"]

    return (
        f"Account for {customer['name']} ({customer['email']}): "
        f"status = '{customer['account_status']}'.\n"
        f"Orders:\n" + "\n".join(order_lines)
    )


@tool
def process_refund(order_id: str, reason: str) -> str:
    """Process a refund for a given order ID, recording the reason given.

    Only orders with status 'delivered', 'shipped', or 'placed' can be
    refunded. This will mark the order as 'refunded' and create a refund
    transaction. Use this only after confirming with the customer that they
    want to proceed with the refund — this action is irreversible in the
    mock system.
    """
    with get_connection() as conn:
        order = conn.execute(
            "SELECT * FROM orders WHERE order_id = ?", (order_id,)
        ).fetchone()

        if order is None:
            return f"No order found with ID '{order_id}'."

        if order["status"] not in ("delivered", "shipped", "placed"):
            return (
                f"Order {order_id} cannot be refunded — current status is "
                f"'{order['status']}'."
            )

        conn.execute(
            "UPDATE orders SET status = 'refunded' WHERE order_id = ?",
            (order_id,),
        )
        txn_id = f"txn_{uuid.uuid4().hex[:8]}"
        conn.execute(
            "INSERT INTO transactions "
            "(transaction_id, order_id, customer_id, type, amount, status, transaction_date, reason) "
            "VALUES (?, ?, ?, 'refund', ?, 'completed', ?, ?)",
            (
                txn_id,
                order_id,
                order["customer_id"],
                order["amount"],
                datetime.now().strftime("%Y-%m-%d"),
                reason,
            ),
        )

    return (
        f"Refund processed for order {order_id}: ${order['amount']:.2f} refunded. "
        f"Reason: {reason}. Transaction ID: {txn_id}."
    )


# Tools list, imported by agent.py and bound to the LLM
ALL_TOOLS = [check_order_status, check_account, process_refund]