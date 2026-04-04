"""
evals/eval_helpers.py — Shared utilities using Phoenix native eval patterns

Provides:
  - Phoenix client connection
  - SpanQuery helpers for pulling trace data
  - llm_classify for LLM-as-judge evaluations
  - SpanEvaluations for pushing results back to Phoenix
  - SQLite ground truth lookups

⚠️  This file is COMPLETE — no changes needed.
"""

import os
import json
import sqlite3
from pathlib import Path

import pandas as pd
import nest_asyncio
nest_asyncio.apply()

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

# ─── Phoenix Imports ───────────────────────────────────────────

import phoenix as px
from phoenix.evals import (
    llm_classify,
    OpenAIModel,
    TOOL_CALLING_PROMPT_TEMPLATE,
)
from phoenix.trace import SpanEvaluations
from phoenix.trace.dsl import SpanQuery
from openinference.instrumentation import suppress_tracing


# ─── Phoenix Connection ────────────────────────────────────────

def get_phoenix_client():
    """
    Get a Phoenix client connected to your Phoenix Cloud instance.
    Uses PHOENIX_COLLECTOR_ENDPOINT and PHOENIX_API_KEY from .env.
    """
    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "https://app.phoenix.arize.com")
    api_key = os.getenv("PHOENIX_API_KEY", "")
    student_name = os.getenv("STUDENT_NAME", "unknown")

    # Set Phoenix environment for the client
    os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = endpoint
    os.environ["PHOENIX_API_KEY"] = api_key

    client = px.Client(endpoint=endpoint, headers={"api_key": api_key})
    print(f"✅ Connected to Phoenix at {endpoint}")
    print(f"   Student: {student_name}")
    return client


def get_project_name() -> str:
    """Get the Phoenix project name for this student."""
    student_name = os.getenv("STUDENT_NAME", "unknown")
    return f"edd-{student_name}"


def get_eval_model():
    """
    Get the OpenAI model wrapper for Phoenix llm_classify.
    This is what the LLM judge uses to evaluate traces.
    """
    return OpenAIModel(model="gpt-4o-mini")


# ─── SpanQuery Helpers ─────────────────────────────────────────

def query_tool_spans(client, tool_name: str = None) -> pd.DataFrame:
    """
    Query tool spans from Phoenix using SpanQuery DSL.

    Args:
        client: Phoenix client
        tool_name: Optional tool name filter (e.g., "lookup_product")

    Returns:
        DataFrame with columns: tool_call_name, tool_parameters, tool_result
    """
    project_name = get_project_name()

    if tool_name:
        filter_expr = f"name == 'tool:{tool_name}'"
    else:
        filter_expr = "span_kind == 'TOOL'"

    query = SpanQuery().where(
        filter_expr
    ).select(
        tool_call_name="name",
        tool_parameters="attributes.tool.parameters",
        tool_result="output.value",
    )

    df = client.query_spans(query, project_name=project_name, timeout=None)

    if df is None or len(df) == 0:
        print(f"   ⚠️  No tool spans found matching '{filter_expr}'.")
        print("   Chat with your bot first to generate traces!")
        return pd.DataFrame()

    print(f"   Found {len(df)} tool spans")
    return df


def query_conversation_spans(client) -> pd.DataFrame:
    """
    Query conversation (root) spans from Phoenix using SpanQuery DSL.

    Returns:
        DataFrame with columns: user_input, agent_response, tool_call_count
    """
    project_name = get_project_name()

    query = SpanQuery().where(
        "name == 'conversation'"
    ).select(
        user_input="input.value",
        agent_response="output.value",
        tool_call_count="attributes.tool.call_count",
    )

    df = client.query_spans(query, project_name=project_name, timeout=None)

    if df is None or len(df) == 0:
        print("   ⚠️  No conversation spans found.")
        print("   Chat with your bot first to generate traces!")
        return pd.DataFrame()

    print(f"   Found {len(df)} conversation spans")
    return df


def query_llm_spans(client) -> pd.DataFrame:
    """
    Query LLM spans from Phoenix — includes tool call decisions.

    Returns:
        DataFrame with columns: question, tool_calls
    """
    project_name = get_project_name()

    query = SpanQuery().where(
        "span_kind == 'LLM'"
    ).select(
        question="input.value",
        tool_calls="llm.tools",
    )

    df = client.query_spans(query, project_name=project_name, timeout=None)

    if df is None or len(df) == 0:
        print("   ⚠️  No LLM spans found.")
        return pd.DataFrame()

    print(f"   Found {len(df)} LLM spans")
    return df


# ─── Push Evaluations to Phoenix ──────────────────────────────

def push_eval_results(client, eval_df: pd.DataFrame, eval_name: str):
    """
    Push evaluation results back to Phoenix as SpanEvaluations.

    This is the Phoenix-native way to log eval results — they appear
    as annotation columns in the traces table.

    Args:
        client: Phoenix client
        eval_df: DataFrame with index=span_id and columns: label, score, explanation
        eval_name: Name of the evaluation (e.g., "pricing_accuracy")
    """
    if eval_df is None or len(eval_df) == 0:
        print("   No evaluation results to push.")
        return

    client.log_evaluations(
        SpanEvaluations(eval_name=eval_name, dataframe=eval_df)
    )

    pass_count = (eval_df["label"] == "PASS").sum() if "PASS" in eval_df["label"].values else \
                 (eval_df["label"] == "correct").sum()
    total = len(eval_df)
    fail_count = total - pass_count

    print(f"\n📊 Results for '{eval_name}':")
    print(f"   Total:  {total}")
    print(f"   PASS:   {pass_count} ({pass_count/total*100:.0f}%)")
    print(f"   FAIL:   {fail_count} ({fail_count/total*100:.0f}%)")
    print(f"   ✅ Evaluations pushed to Phoenix")


# ─── SQLite Ground Truth ──────────────────────────────────────

DB_PATH = Path(__file__).parent.parent / "data" / "adventureworks.db"


def get_db():
    """Get a connection to the local AdventureWorks SQLite database."""
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}. "
            "Make sure adventureworks.db is in the data/ folder."
        )
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def lookup_product_price(product_name: str) -> float | None:
    """
    Look up the actual price of a product in the database.
    Returns the ListPrice or None if not found.

    Usage:
        price = lookup_product_price("Mountain-200")
        # Returns 2294.99
    """
    conn = get_db()
    cursor = conn.execute(
        "SELECT ListPrice FROM Product WHERE Name LIKE ? LIMIT 1",
        (f"%{product_name}%",),
    )
    row = cursor.fetchone()
    conn.close()
    return float(row["ListPrice"]) if row else None


def lookup_order_total(order_id: int) -> float | None:
    """
    Look up the actual total for an order in the database.
    Returns TotalDue or None if not found.
    """
    conn = get_db()
    cursor = conn.execute(
        "SELECT TotalDue FROM SalesOrderHeader WHERE SalesOrderID = ?",
        (order_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return float(row["TotalDue"]) if row else None


# ─── Tool Definitions (for TOOL_CALLING eval) ─────────────────
# These match the tools defined in lib/tools.ts in the starter kit.

ADVENTUREWORKS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_product",
            "description": "Look up a product by name. Returns price, color, size, and category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Full or partial product name"}
                },
                "required": ["name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for products by category, price range, or color.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "maxPrice": {"type": "number"},
                    "minPrice": {"type": "number"},
                    "color": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_order",
            "description": "Look up an order by order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "orderId": {"type": "number", "description": "The sales order ID number"}
                },
                "required": ["orderId"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_orders",
            "description": "Get recent orders for a customer by their customer ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customerId": {"type": "number", "description": "The customer ID number"}
                },
                "required": ["customerId"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_customer",
            "description": "Look up customer information by customer ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customerId": {"type": "number", "description": "The customer ID number"}
                },
                "required": ["customerId"],
            },
        },
    },
]
