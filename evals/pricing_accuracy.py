"""
evals/pricing_accuracy.py — Code-Based Eval: Pricing Accuracy

🔧 YOU COMPLETE THIS FILE (Session 5)

This eval checks whether the agent quoted correct product prices
by comparing the price in the agent's response against the actual
price in the AdventureWorks database.

How it works:
  1. Pull traces from Phoenix (only tool:lookup_product spans)
  2. For each span, extract the product name and the price the agent used
  3. Look up the real price in SQLite
  4. Compare: if they match (within $0.01), PASS. Otherwise, FAIL.
  5. Push annotations back to Phoenix

Run:
  python pricing_accuracy.py
"""

import re
import json
from eval_helpers import (
    get_phoenix_client,
    get_traces,
    lookup_product_price,
    push_annotations,
)


def extract_price_from_text(text: str) -> float | None:
    """
    Extract a dollar amount from text like "$2,294.99" or "2294.99 dollars".
    Returns the numeric value or None if no price found.
    """
    # Look for patterns like $1,234.56 or $1234.56
    matches = re.findall(r"\$?([\d,]+\.?\d*)", text)
    for match in matches:
        try:
            value = float(match.replace(",", ""))
            if value > 0:
                return value
        except ValueError:
            continue
    return None


def run_pricing_eval():
    """
    Main eval function. Pull traces, check prices, push results.
    """
    client = get_phoenix_client()
    df = get_traces(client)

    if df is None:
        return

    annotations = []

    # ────────────────────────────────────────────────────────────
    # TODO: Implement the pricing accuracy eval
    #
    # Steps:
    #   1. Filter the DataFrame to only include tool spans where
    #      the tool name is "lookup_product":
    #
    #      tool_spans = df[df["name"] == "tool:lookup_product"]
    #
    #   2. For each tool span:
    #      a. Extract the product name from the tool parameters
    #         (stored in attributes as "tool.parameters")
    #
    #      b. Extract the price from the tool result
    #         (stored in attributes as "output.value")
    #
    #      c. Look up the ground truth price from SQLite:
    #         actual_price = lookup_product_price(product_name)
    #
    #      d. Compare the two prices:
    #         - If they match within $0.01 → PASS
    #         - If they don't match → FAIL
    #         - If you can't extract either price → FAIL with explanation
    #
    #      e. Append to annotations:
    #         annotations.append({
    #             "span_id": span_id,
    #             "label": "PASS" or "FAIL",
    #             "score": 1 or 0,
    #             "explanation": "why"
    #         })
    #
    #   3. Push annotations to Phoenix:
    #      push_annotations(client, annotations, "pricing_accuracy")
    #
    # Hints:
    #   - span_id is the index of the DataFrame (df.index)
    #   - Tool parameters are JSON strings: json.loads(row["attributes"]["tool.parameters"])
    #   - Tool results are JSON strings: json.loads(row["attributes"]["output.value"])
    #   - The product result dict has a "ListPrice" field
    #
    # ────────────────────────────────────────────────────────────

    # REMOVE THIS PLACEHOLDER once you implement the above:
    print("⚠️  pricing_accuracy.py is not yet implemented.")
    print("   Complete the TODO in this file to run the eval.")


if __name__ == "__main__":
    run_pricing_eval()
