"""
test_tools.py — Exercise the three agent tools directly, no LLM involved.

Run this from inside core/agent/ (same folder as database.py, agent_tools.py):

    python test_tools.py

This confirms the tools + database work correctly before we add the LLM/
LangGraph layer on top. If something's wrong here, it's a tools/DB bug, not
an agent bug — much easier to debug in isolation.
"""

from database import init_db
from agent_tools import check_order_status, check_account, process_refund


def run(label, tool_fn, **kwargs):
    print(f"\n--- {label} ---")
    print(f"input: {kwargs}")
    # LangChain @tool-decorated functions are invoked via .invoke(dict)
    result = tool_fn.invoke(kwargs)
    print(f"output: {result}")
    return result


if __name__ == "__main__":
    # Fresh DB so results are predictable and repeatable
    init_db(reset=True)

    # 1. Look up a normal order
    run("check_order_status - valid order", check_order_status, order_id="ord_1001")

    # 2. Look up a non-existent order
    run("check_order_status - bad order id", check_order_status, order_id="ord_9999")

    # 3. Check an account with order history
    run("check_account - valid email", check_account, email="priya.sharma@example.com")

    # 4. Check a non-existent account
    run("check_account - unknown email", check_account, email="nobody@example.com")

    # 5. Process a valid refund (ord_1001 is 'delivered', should succeed)
    run("process_refund - valid refund", process_refund,
        order_id="ord_1001", reason="arrived damaged")

    # 6. Confirm the order status flipped to 'refunded'
    run("check_order_status - after refund", check_order_status, order_id="ord_1001")

    # 7. Try to refund the SAME order again — should be rejected
    run("process_refund - double refund (should fail)", process_refund,
        order_id="ord_1001", reason="trying again")

    # 8. Try to refund an order that's already cancelled+refunded in seed data
    run("process_refund - already-refunded seed order (should fail)", process_refund,
        order_id="ord_1004", reason="trying again")

    print("\n--- test_tools.py finished ---")