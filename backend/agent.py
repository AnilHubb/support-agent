import os
import json
from typing import List

from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_mistralai import ChatMistralAI

from database import get_db

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a friendly and empathetic customer support assistant for an
e-commerce platform. Your job is to help customers with:
  - Order status and tracking
  - Estimated delivery times
  - Delayed or missing orders
  - Order cancellations

You have tools to look up order data. Always use them when the customer asks about
specific orders. Present information clearly. If an order is delayed, be empathetic
and offer next steps.

Current authenticated user ID: {user_id}
When a customer asks about "my orders" use get_user_orders with user_id={user_id}.
"""


# ---------------------------------------------------------------------------
# LangChain tools
# ---------------------------------------------------------------------------
@tool
def get_order_status(order_id: str) -> str:
    """Fetch the current status and details of a single order by its order ID (e.g. ORD-001)."""
    conn = get_db()
    order = conn.execute(
        "SELECT * FROM orders WHERE order_id = ?", (order_id,)
    ).fetchone()
    conn.close()

    if not order:
        return f"No order found with ID '{order_id}'."

    status_labels = {
        "processing":       "Being processed — not yet shipped.",
        "shipped":          "Shipped and on its way.",
        "out_for_delivery": "Out for delivery today!",
        "delivered":        "Successfully delivered.",
        "delayed":          "Delayed — we apologise for the inconvenience.",
        "cancelled":        "Cancelled.",
    }

    return json.dumps({
        "order_id":           order["order_id"],
        "product":            order["product_name"],
        "status":             order["status"],
        "status_description": status_labels.get(order["status"], "Unknown"),
        "tracking_number":    order["tracking_number"],
        "estimated_delivery": order["estimated_delivery"],
        "actual_delivery":    order["delivery_date"],
    })


@tool
def get_user_orders(user_id: int) -> str:
    """Fetch all orders belonging to a user. Use the current user's user_id."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM orders WHERE user_id = ?", (user_id,)
    ).fetchall()
    conn.close()

    if not rows:
        return f"No orders found for user {user_id}."

    orders = [
        {
            "order_id":           r["order_id"],
            "product":            r["product_name"],
            "status":             r["status"],
            "estimated_delivery": r["estimated_delivery"],
            "actual_delivery":    r["delivery_date"],
            "tracking_number":    r["tracking_number"],
        }
        for r in rows
    ]
    return json.dumps(orders)


# ---------------------------------------------------------------------------
# Agent wrapper
# ---------------------------------------------------------------------------
class ChatAgent:
    def __init__(self, user_id: int):
        self.user_id = user_id

        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "MISTRAL_API_KEY is not set. "
                "Add it to backend/.env or export it in your shell."
            )

        llm = ChatMistralAI(
            model="mistral-large-latest",
            mistral_api_key=api_key,
            temperature=0.4,
        )

        tools = [get_order_status, get_user_orders]
        system_msg = SYSTEM_PROMPT.format(user_id=user_id)

        # create_react_agent is the modern LangGraph replacement for AgentExecutor
        self.graph = create_react_agent(llm, tools=tools, prompt=system_msg)

    def chat(self, message: str, history: List[dict]) -> str:
        # Build the full message list from history + new message
        messages: list = []
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
        messages.append(HumanMessage(content=message))

        result = self.graph.invoke({"messages": messages})

        # The last message in the output is the assistant reply
        return result["messages"][-1].content
