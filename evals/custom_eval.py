"""
evals/custom_eval.py — Your Custom Eval (Session 7)

🔧 YOU COMPLETE THIS FILE (Session 7)

Design and implement your own evaluation metric. This is YOUR metric —
something you identified as important through your work in Sessions 4–6.

Some ideas (pick one or invent your own):

  📐 tool_selection_accuracy
     Did the agent call the right tool for the question?
     e.g., product question → lookup_product, order question → lookup_order
     Method: Code-based (compare tool called vs. expected tool)

  📐 response_completeness
     Did the agent answer ALL parts of the customer's question?
     e.g., "What color is the Mountain-200 and how much does it cost?"
     → Response should include both color AND price
     Method: LLM judge with rubric

  📐 hallucination_detection
     Did the agent make up information not in the tool results?
     e.g., Agent says "free shipping included" but no tool returned shipping info
     Method: LLM judge comparing response against tool outputs

  📐 tone_professionalism
     Is the agent's tone professional and appropriate?
     Method: LLM judge with rubric

  📐 data_grounding
     Does every factual claim in the response trace back to a tool call?
     Method: Hybrid (code check for tool calls + LLM judge for claims)

Run:
  python custom_eval.py
"""

from eval_helpers import (
    get_phoenix_client,
    get_traces,
    push_annotations,
    run_llm_judge,      # if using LLM judge
    lookup_product_price, # if checking prices
    get_db,              # if running custom SQL
)


# ─── Your Metric Definition ────────────────────────────────────

METRIC_NAME = "your_metric_name"  # TODO: Name your metric

# If using an LLM judge, define your rubric here:
YOUR_RUBRIC = """
## Your Metric Rubric

TODO: Write your rubric here. Include:
  - What you're measuring and why it matters
  - Clear PASS criteria
  - Clear FAIL criteria
  - At least one edge case
  - One example of a PASS and one of a FAIL
"""


def run_custom_eval():
    """
    Your custom eval implementation.
    """
    client = get_phoenix_client()
    df = get_traces(client)

    if df is None:
        return

    annotations = []

    # ────────────────────────────────────────────────────────────
    # TODO: Implement your custom eval
    #
    # Use the patterns from pricing_accuracy.py (code-based)
    # or escalation_quality.py (LLM judge) as your starting point.
    #
    # Requirements:
    #   1. Filter traces to the relevant spans
    #   2. Evaluate each span against your criteria
    #   3. Produce PASS/FAIL with explanations
    #   4. Push annotations to Phoenix
    #
    # Grading criteria for your capstone:
    #   - Is the metric measuring something meaningful?
    #   - Is the rubric clear and unambiguous?
    #   - Does the eval produce reliable results?
    #   - Can you show before/after improvement using this metric?
    #
    # ────────────────────────────────────────────────────────────

    print("⚠️  custom_eval.py is not yet implemented.")
    print(f"   Metric name: {METRIC_NAME}")
    print("   Complete the TODO in this file to run your custom eval.")


if __name__ == "__main__":
    run_custom_eval()
