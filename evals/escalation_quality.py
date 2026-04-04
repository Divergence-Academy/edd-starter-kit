"""
evals/escalation_quality.py — LLM Judge Eval: Escalation Quality

🔧 YOU COMPLETE THIS FILE (Session 6)

Uses Phoenix llm_classify to assess whether the agent appropriately
escalated (or should have escalated) when customers expressed frustration.

How it works:
  1. SpanQuery pulls conversation spans from Phoenix
  2. llm_classify sends each conversation to an LLM judge with a rubric
  3. The judge returns "pass" or "fail" with explanation
  4. Push SpanEvaluations back to Phoenix

Run:
  python escalation_quality.py
"""

import pandas as pd
from eval_helpers import (
    get_phoenix_client,
    get_eval_model,
    query_conversation_spans,
    push_eval_results,
    llm_classify,
    suppress_tracing,
)


# ─── Escalation Rubric (LLM Judge Prompt Template) ────────────
#
# This follows the Phoenix llm_classify pattern:
#   - Template uses {variable} placeholders matching DataFrame columns
#   - Rails define the possible labels
#   - The judge returns one of the rails + explanation

ESCALATION_EVAL_PROMPT = """
You are evaluating whether a customer support agent correctly handled
escalation situations in a conversation.

## PASS Criteria
The agent should receive a "pass" if ANY of these are true:
- The customer did NOT express frustration or request escalation,
  and the agent handled the query normally
- The customer expressed frustration or requested a manager,
  AND the agent acknowledged their concern and offered to escalate
  to a human agent or supervisor

## FAIL Criteria
The agent should receive a "fail" if:
- The customer expressed frustration, threatened to leave, mentioned
  legal action, or requested a manager, BUT the agent did NOT offer
  to escalate or connect them with a human
- The agent gave a generic helpful response to an angry customer
  instead of acknowledging the severity and escalating

## Edge Cases
- Mild annoyance without escalation request → normal response is OK (pass)
- Profanity or ALL CAPS → signals frustration even without explicit request (fail if not escalated)
- "I'm switching to [competitor]" → implicit churn signal (fail if not escalated)

## Conversation to Evaluate

Customer: {user_input}
Agent: {agent_response}

Your response should be a single word: either "pass" or "fail".
"""


def run_escalation_eval():
    """
    Main eval function. Pull conversations, judge with llm_classify, push results.
    """
    client = get_phoenix_client()

    # ────────────────────────────────────────────────────────────
    # Step 1: Query conversation spans from Phoenix
    # ────────────────────────────────────────────────────────────
    df = query_conversation_spans(client)

    if df.empty:
        return

    # Drop rows with missing input or response
    df = df.dropna(subset=["user_input", "agent_response"])

    if df.empty:
        print("   ⚠️  No conversations with both input and response found.")
        return

    print(f"   Evaluating {len(df)} conversations...")

    # ────────────────────────────────────────────────────────────
    # TODO: Step 2 — Run llm_classify on the conversation spans
    #
    # Phoenix's llm_classify is the native way to run LLM-as-judge.
    # It takes a DataFrame, a prompt template, and rails (labels),
    # and returns a DataFrame with label, score, and explanation.
    #
    # The template uses {column_name} placeholders that map to
    # DataFrame columns. Our DataFrame has:
    #   - user_input (from SpanQuery)
    #   - agent_response (from SpanQuery)
    #
    # These match the {user_input} and {agent_response} in the
    # ESCALATION_EVAL_PROMPT template above.
    #
    # Usage:
    #   with suppress_tracing():
    #       eval_result = llm_classify(
    #           dataframe=df,
    #           template=ESCALATION_EVAL_PROMPT,
    #           rails=["pass", "fail"],
    #           model=get_eval_model(),
    #           provide_explanation=True,
    #       )
    #
    # suppress_tracing() prevents the judge's own LLM calls from
    # being traced (you don't want eval traces mixed with app traces).
    #
    # After llm_classify, add a numeric score column:
    #   eval_result["score"] = eval_result.apply(
    #       lambda x: 1 if x["label"] == "pass" else 0, axis=1
    #   )
    #
    # Rename labels to PASS/FAIL for consistency:
    #   eval_result["label"] = eval_result["label"].map(
    #       {"pass": "PASS", "fail": "FAIL"}
    #   )
    #
    # ────────────────────────────────────────────────────────────

    with suppress_tracing():
        eval_result = llm_classify(
            dataframe=df,
            template=ESCALATION_EVAL_PROMPT,
            rails=["pass", "fail"],
            model=get_eval_model(),
            provide_explanation=True,
        )

    # Add numeric score
    eval_result["score"] = eval_result.apply(
        lambda x: 1 if x["label"] == "pass" else 0, axis=1
    )

    # Rename to PASS/FAIL
    eval_result["label"] = eval_result["label"].map(
        {"pass": "PASS", "fail": "FAIL"}
    ).fillna("FAIL")

    # Print individual results
    for span_id, row in eval_result.iterrows():
        user_msg = df.loc[span_id, "user_input"][:60] if span_id in df.index else "?"
        print(f"   [{row['label']}] {user_msg}...")
        if row.get("explanation"):
            print(f"            → {str(row['explanation'])[:80]}")

    # ────────────────────────────────────────────────────────────
    # Step 3: Push results to Phoenix as SpanEvaluations
    # ────────────────────────────────────────────────────────────
    push_eval_results(client, eval_result, "escalation_quality")


if __name__ == "__main__":
    run_escalation_eval()
