"""
evals/custom_eval.py — Your Custom Eval (Session 7)

🔧 YOU COMPLETE THIS FILE (Session 7)

Design and implement your own evaluation metric using Phoenix native patterns.

This template shows THREE patterns you can use (pick one or combine):

  Pattern A: TOOL_CALLING_PROMPT_TEMPLATE (from Phoenix built-in)
     Evaluates whether the agent called the correct tool.
     Uses Phoenix's pre-built template — no rubric writing needed.

  Pattern B: Custom llm_classify (like escalation_quality.py)
     Write your own rubric prompt and run it through llm_classify.
     Good for: response_completeness, hallucination_detection, tone.

  Pattern C: Code-based evaluator (like pricing_accuracy.py)
     Pure Python logic, no LLM calls.
     Good for: format checks, data grounding, structural validation.

Patterns from: DeepLearning.AI "Evaluating AI Agents" Labs 3-5

Run:
  python custom_eval.py
"""

import json
import pandas as pd
from eval_helpers import (
    get_phoenix_client,
    get_eval_model,
    get_project_name,
    query_conversation_spans,
    query_llm_spans,
    push_eval_results,
    llm_classify,
    suppress_tracing,
    TOOL_CALLING_PROMPT_TEMPLATE,
    ADVENTUREWORKS_TOOLS,
    SpanQuery,
)


# ═══════════════════════════════════════════════════════════════
# CHOOSE YOUR METRIC — uncomment ONE section below
# ═══════════════════════════════════════════════════════════════


# ─── Option A: Tool Selection Accuracy ─────────────────────────
# Uses Phoenix's built-in TOOL_CALLING_PROMPT_TEMPLATE
# Checks: did the agent call the correct tool for the question?
#

METRIC_NAME = "tool_selection_accuracy"

def run_custom_eval():
    client = get_phoenix_client()

    # Query LLM spans that contain tool call decisions
    df = query_llm_spans(client)

    if df.empty:
        return

    # Filter to spans that actually have tool calls
    df = df.dropna(subset=["tool_calls"])

    if df.empty:
        print("   ⚠️  No LLM spans with tool calls found.")
        return

    print(f"   Evaluating {len(df)} tool call decisions...")

    # ────────────────────────────────────────────────────────────
    # TODO: Run the tool calling eval using Phoenix's built-in template
    #
    # Phoenix provides TOOL_CALLING_PROMPT_TEMPLATE — a pre-built
    # rubric that evaluates whether the correct tool was called
    # with the correct parameters.
    #
    # You need to:
    #   1. Get the template string:
    #      template = TOOL_CALLING_PROMPT_TEMPLATE.template[0].template
    #
    #   2. Inject your tool definitions into the template:
    #      template = template.replace(
    #          "{tool_definitions}",
    #          json.dumps(ADVENTUREWORKS_TOOLS)
    #              .replace("{", '"').replace("}", '"')
    #      )
    #
    #   3. Run llm_classify:
    #      with suppress_tracing():
    #          eval_result = llm_classify(
    #              dataframe=df,
    #              template=template,
    #              rails=["correct", "incorrect"],
    #              model=get_eval_model(),
    #              provide_explanation=True,
    #          )
    #
    #   4. Add score column:
    #      eval_result["score"] = eval_result.apply(
    #          lambda x: 1 if x["label"] == "correct" else 0, axis=1
    #      )
    #
    #   5. Map labels to PASS/FAIL:
    #      eval_result["label"] = eval_result["label"].map(
    #          {"correct": "PASS", "incorrect": "FAIL"}
    #      ).fillna("FAIL")
    #
    #   6. Push results:
    #      push_eval_results(client, eval_result, METRIC_NAME)
    #
    # ────────────────────────────────────────────────────────────

    # REMOVE THIS PLACEHOLDER once you implement the above:
    print(f"⚠️  {METRIC_NAME} is not yet implemented.")
    print("   Complete the TODO in this file.")


# ─── Option B: Response Completeness (llm_classify) ────────────
# Uncomment this section and comment out Option A to use this instead.
#
# METRIC_NAME = "response_completeness"
#
# COMPLETENESS_EVAL_PROMPT = """
# You are evaluating whether a customer support agent fully answered
# ALL parts of the customer's question.
#
# ## PASS Criteria
# - The agent addressed every distinct question or request in the input
# - All factual claims are supported by tool results
# - No parts of the question were ignored or skipped
#
# ## FAIL Criteria
# - The agent answered some parts but missed others
# - The customer asked multiple things but only got one answer
# - The agent acknowledged the question but didn't provide the information
#
# ## Conversation
# Customer: {user_input}
# Agent: {agent_response}
#
# Your response should be a single word: either "pass" or "fail".
# """
#
# def run_custom_eval():
#     client = get_phoenix_client()
#     df = query_conversation_spans(client)
#     if df.empty:
#         return
#     df = df.dropna(subset=["user_input", "agent_response"])
#
#     with suppress_tracing():
#         eval_result = llm_classify(
#             dataframe=df,
#             template=COMPLETENESS_EVAL_PROMPT,
#             rails=["pass", "fail"],
#             model=get_eval_model(),
#             provide_explanation=True,
#         )
#     eval_result["score"] = eval_result.apply(
#         lambda x: 1 if x["label"] == "pass" else 0, axis=1)
#     eval_result["label"] = eval_result["label"].map(
#         {"pass": "PASS", "fail": "FAIL"}).fillna("FAIL")
#     push_eval_results(client, eval_result, METRIC_NAME)


# ─── Option C: Data Grounding (code-based) ─────────────────────
# Uncomment this section and comment out Option A to use this instead.
#
# Checks whether the agent mentioned any product prices without
# having a corresponding tool:lookup_product span.
#
# METRIC_NAME = "data_grounding"
#
# def run_custom_eval():
#     import re
#     client = get_phoenix_client()
#     conv_df = query_conversation_spans(client)
#     tool_df = query_tool_spans(client, tool_name="lookup_product")
#
#     if conv_df.empty:
#         return
#
#     results = []
#     # Get set of span_ids that have tool calls
#     tool_span_ids = set(tool_df.index) if not tool_df.empty else set()
#
#     for span_id, row in conv_df.iterrows():
#         response = str(row.get("agent_response", ""))
#         # Check if response mentions a dollar amount
#         has_price = bool(re.search(r"\$[\d,]+\.?\d*", response))
#         # Check if there was a tool call for this conversation
#         # (simplified — checks if any tool spans exist in the project)
#         has_tool_call = len(tool_span_ids) > 0
#
#         if has_price and not has_tool_call:
#             results.append({"label": "FAIL", "score": 0,
#                 "explanation": "Response mentions price but no lookup_product tool was called"})
#         else:
#             results.append({"label": "PASS", "score": 1,
#                 "explanation": "Price claims are grounded in tool results (or no prices mentioned)"})
#
#     eval_df = pd.DataFrame(results, index=conv_df.index)
#     push_eval_results(client, eval_df, METRIC_NAME)


if __name__ == "__main__":
    run_custom_eval()
