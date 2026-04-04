"""
evals/pricing_accuracy.py — Code-Based Eval: Pricing Accuracy

🔧 YOU COMPLETE THIS FILE (Session 5)

Uses Phoenix SpanQuery to pull tool:lookup_product spans, then compares
the price in the tool result against SQLite ground truth.

How it works:
  1. SpanQuery pulls all tool:lookup_product spans from Phoenix
  2. For each span, extract the product name and tool result price
  3. Look up the real price in SQLite (ground truth)
  4. Compare: match within $0.01 → PASS, otherwise FAIL
  5. Push SpanEvaluations back to Phoenix

Run:
  python pricing_accuracy.py
"""

import json
import pandas as pd
from eval_helpers import (
    get_phoenix_client,
    query_tool_spans,
    push_eval_results,
    lookup_product_price,
)


def run_pricing_eval():
    """
    Main eval function. Pull tool spans, check prices, push results.
    """
    client = get_phoenix_client()

    # ────────────────────────────────────────────────────────────
    # Step 1: Query tool spans from Phoenix using SpanQuery
    #
    # This uses the Phoenix SpanQuery DSL to pull only the spans
    # we care about — tool:lookup_product calls.
    # ────────────────────────────────────────────────────────────
    df = query_tool_spans(client, tool_name="lookup_product")

    if df.empty:
        return

    # ────────────────────────────────────────────────────────────
    # TODO: Step 2 — Evaluate each span
    #
    # For each row in the DataFrame:
    #   a. Parse tool_parameters (JSON string) to get the product name
    #   b. Parse tool_result (JSON string) to get the returned ListPrice
    #   c. Look up ground truth price: lookup_product_price(product_name)
    #   d. Compare: abs(tool_price - actual_price) < 0.01
    #   e. Record label ("PASS" or "FAIL"), score (1 or 0), explanation
    #
    # Build a results DataFrame with the same index as df (span IDs)
    # and columns: label, score, explanation
    #
    # Hints:
    #   - tool_parameters is a JSON string: json.loads(row["tool_parameters"])
    #   - tool_result is a JSON string: json.loads(row["tool_result"])
    #   - The product result dict has a "ListPrice" field
    #   - Handle errors gracefully (missing data, parse failures)
    #
    # Example:
    #   params = json.loads(row["tool_parameters"])
    #   product_name = params.get("name", "")
    #   result = json.loads(row["tool_result"])
    #   tool_price = result.get("ListPrice")
    #   actual_price = lookup_product_price(product_name)
    #
    # ────────────────────────────────────────────────────────────

    results = []

    for span_id, row in df.iterrows():
        try:
            # Parse tool parameters
            params = json.loads(row["tool_parameters"]) if isinstance(row["tool_parameters"], str) else row["tool_parameters"]
            product_name = params.get("name", "") if isinstance(params, dict) else ""

            if not product_name:
                results.append({"label": "FAIL", "score": 0, "explanation": "No product name in tool parameters"})
                continue

            # Parse tool result
            result = json.loads(row["tool_result"]) if isinstance(row["tool_result"], str) else row["tool_result"]

            # Check for error response
            if isinstance(result, dict) and "error" in result:
                results.append({"label": "FAIL", "score": 0, "explanation": f"Product not found: {result['error']}"})
                print(f"   [FAIL] {product_name}: not found")
                continue

            # Extract price from tool result
            tool_price = result.get("ListPrice") if isinstance(result, dict) else None

            # Get ground truth from SQLite
            actual_price = lookup_product_price(product_name)

            if tool_price is None:
                results.append({"label": "FAIL", "score": 0, "explanation": f"No ListPrice in tool result for '{product_name}'"})
                print(f"   [FAIL] {product_name}: no price in result")
                continue

            if actual_price is None:
                results.append({"label": "FAIL", "score": 0, "explanation": f"'{product_name}' not found in ground truth DB"})
                print(f"   [FAIL] {product_name}: not in DB")
                continue

            # Compare prices
            if abs(float(tool_price) - float(actual_price)) < 0.01:
                results.append({"label": "PASS", "score": 1, "explanation": f"Price ${tool_price} matches DB (${actual_price})"})
                print(f"   [PASS] {product_name}: ${tool_price} ✓")
            else:
                results.append({"label": "FAIL", "score": 0, "explanation": f"Price mismatch: tool=${tool_price}, DB=${actual_price}"})
                print(f"   [FAIL] {product_name}: ${tool_price} ≠ ${actual_price}")

        except Exception as e:
            results.append({"label": "FAIL", "score": 0, "explanation": f"Error: {str(e)}"})

    # ────────────────────────────────────────────────────────────
    # Step 3: Push results to Phoenix as SpanEvaluations
    # ────────────────────────────────────────────────────────────
    if results:
        eval_df = pd.DataFrame(results, index=df.index)
        push_eval_results(client, eval_df, "pricing_accuracy")


if __name__ == "__main__":
    run_pricing_eval()
