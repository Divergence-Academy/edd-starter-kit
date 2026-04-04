"""
evals/eval_helpers.py — Shared utilities for eval scripts

Provides functions to:
  - Connect to Phoenix and pull traces
  - Connect to the local AdventureWorks SQLite database
  - Push annotations (eval results) back to Phoenix

⚠️  This file is COMPLETE — no changes needed.
"""

import os
import json
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# ─── Phoenix Connection ────────────────────────────────────────

def get_phoenix_client():
    """
    Get a Phoenix client connected to your Phoenix Cloud instance.
    Uses PHOENIX_COLLECTOR_ENDPOINT and PHOENIX_API_KEY from .env.
    """
    try:
        import phoenix.Client as PhoenixClient
    except ImportError:
        from phoenix.client import Client as PhoenixClient

    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "https://app.phoenix.arize.com")
    api_key = os.getenv("PHOENIX_API_KEY", "")
    student_name = os.getenv("STUDENT_NAME", "unknown")

    client = PhoenixClient(endpoint=endpoint, api_key=api_key)
    print(f"✅ Connected to Phoenix at {endpoint}")
    print(f"   Student: {student_name}")
    return client


def get_traces(client, project_name: str = None, limit: int = 100):
    """
    Pull recent traces from Phoenix as a pandas DataFrame.

    Each row is a span with columns like:
      - name, span_kind, status_code
      - attributes (dict with input.value, output.value, tool.name, etc.)
      - start_time, end_time

    Usage:
        client = get_phoenix_client()
        df = get_traces(client, project_name="edd-yourname")
    """
    student_name = os.getenv("STUDENT_NAME", "unknown")
    if project_name is None:
        project_name = f"edd-{student_name}"

    print(f"📥 Pulling traces from project: {project_name}")
    df = client.get_spans_dataframe(project_name=project_name)

    if df is None or len(df) == 0:
        print("   ⚠️  No traces found. Chat with your bot first to generate some!")
        return None

    print(f"   Found {len(df)} spans")
    return df


# ─── SQLite Connection (for ground truth lookups) ──────────────

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


# ─── Push Annotations to Phoenix ──────────────────────────────

def push_annotations(client, annotations: list[dict], metric_name: str):
    """
    Push eval results back to Phoenix as span annotations.

    Each annotation dict should have:
      - span_id: str
      - label: "PASS" or "FAIL"
      - score: 1 (pass) or 0 (fail)
      - explanation: str (why this label)

    Usage:
        annotations = [
            {
                "span_id": "abc123",
                "label": "FAIL",
                "score": 0,
                "explanation": "Agent quoted $2,500 but actual price is $2,294.99"
            }
        ]
        push_annotations(client, annotations, "pricing_accuracy")
    """
    import pandas as pd

    if not annotations:
        print("   No annotations to push.")
        return

    df = pd.DataFrame(annotations)
    df = df.rename(columns={"span_id": "context.span_id"})

    client.log_annotations(
        dataframe=df,
        annotation_name=metric_name,
        annotator_kind="CODE",
    )

    pass_count = sum(1 for a in annotations if a["label"] == "PASS")
    fail_count = sum(1 for a in annotations if a["label"] == "FAIL")
    total = len(annotations)

    print(f"\n📊 Results for '{metric_name}':")
    print(f"   Total:  {total}")
    print(f"   PASS:   {pass_count} ({pass_count/total*100:.0f}%)")
    print(f"   FAIL:   {fail_count} ({fail_count/total*100:.0f}%)")
    print(f"   ✅ Annotations pushed to Phoenix")


# ─── LLM Judge Helper ─────────────────────────────────────────

def run_llm_judge(
    prompt: str,
    model: str = "gpt-4o-mini",
) -> dict:
    """
    Send a rubric prompt to an LLM and get a structured judgment.

    The prompt should ask the judge to respond with JSON containing:
      - label: "PASS" or "FAIL"
      - explanation: why

    Returns: {"label": "PASS"|"FAIL", "explanation": "..."}
    """
    from openai import OpenAI

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an evaluation judge. Assess the interaction below "
                    "and respond with ONLY a JSON object: "
                    '{"label": "PASS" or "FAIL", "explanation": "brief reason"}'
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )

    text = response.choices[0].message.content.strip()

    # Parse JSON from response (handle markdown code blocks)
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    try:
        result = json.loads(text)
        return {
            "label": result.get("label", "FAIL"),
            "explanation": result.get("explanation", "No explanation provided"),
        }
    except json.JSONDecodeError:
        return {
            "label": "FAIL",
            "explanation": f"Judge returned unparseable response: {text[:200]}",
        }
