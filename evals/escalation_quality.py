"""
evals/escalation_quality.py — LLM Judge Eval: Escalation Quality

🔧 YOU COMPLETE THIS FILE (Session 5)

This eval uses an LLM judge to assess whether the agent appropriately
escalated (or should have escalated) to a human when a customer
expressed frustration, threatened to leave, or requested a manager.

How it works:
  1. Pull conversation traces from Phoenix
  2. For each conversation, build a judge prompt with the rubric
  3. Send to an LLM judge for a PASS/FAIL verdict
  4. Push annotations back to Phoenix

Run:
  python escalation_quality.py
"""

import json
from eval_helpers import (
    get_phoenix_client,
    get_traces,
    run_llm_judge,
    push_annotations,
)


# ─── Rubric Definition ─────────────────────────────────────────
#
# This is the rubric the LLM judge will use to evaluate each conversation.
# A well-written rubric has:
#   - Clear PASS criteria
#   - Clear FAIL criteria
#   - Specific examples of edge cases

ESCALATION_RUBRIC = """
## Escalation Quality Rubric

You are evaluating whether a customer support agent correctly handled
escalation situations in a conversation.

### PASS Criteria
The agent should receive a PASS if ANY of these are true:
- The customer did NOT express frustration or request escalation,
  and the agent handled the query normally
- The customer expressed frustration or requested a manager,
  AND the agent acknowledged their concern and offered to escalate
  to a human agent or supervisor

### FAIL Criteria
The agent should receive a FAIL if:
- The customer expressed frustration, threatened to leave, mentioned
  legal action, or requested a manager, BUT the agent did NOT offer
  to escalate or connect them with a human
- The agent gave a generic helpful response to an angry customer
  instead of acknowledging the severity and escalating

### Edge Cases
- If the customer is mildly annoyed but not requesting escalation,
  a helpful response without escalation is acceptable (PASS)
- If the customer uses profanity or all-caps, that signals frustration
  even without explicitly requesting a manager (should escalate → FAIL if not)
"""


def build_judge_prompt(conversation: str) -> str:
    """
    Build the full prompt to send to the LLM judge.
    Combines the rubric with the actual conversation to evaluate.
    """
    return f"""
{ESCALATION_RUBRIC}

## Conversation to Evaluate

{conversation}

## Your Judgment

Based on the rubric above, evaluate this conversation.
Respond with a JSON object: {{"label": "PASS" or "FAIL", "explanation": "brief reason"}}
"""


def run_escalation_eval():
    """
    Main eval function. Pull traces, judge conversations, push results.
    """
    client = get_phoenix_client()
    df = get_traces(client)

    if df is None:
        return

    annotations = []

    # ────────────────────────────────────────────────────────────
    # TODO: Implement the escalation quality eval
    #
    # Steps:
    #   1. Filter the DataFrame to conversation spans:
    #      conversations = df[df["name"] == "conversation"]
    #
    #   2. For each conversation span:
    #      a. Extract the user's input message from attributes:
    #         user_msg = row["attributes"].get("input.value", "")
    #
    #      b. Extract the agent's response from attributes:
    #         agent_msg = row["attributes"].get("output.value", "")
    #
    #      c. Build the conversation text:
    #         conversation_text = f"Customer: {user_msg}\nAgent: {agent_msg}"
    #
    #      d. Build the judge prompt:
    #         prompt = build_judge_prompt(conversation_text)
    #
    #      e. Run the LLM judge:
    #         result = run_llm_judge(prompt)
    #
    #      f. Append to annotations:
    #         annotations.append({
    #             "span_id": span_id,
    #             "label": result["label"],
    #             "score": 1 if result["label"] == "PASS" else 0,
    #             "explanation": result["explanation"],
    #         })
    #
    #      g. Print progress (helpful for debugging):
    #         print(f"   [{result['label']}] {user_msg[:60]}...")
    #
    #   3. Push annotations to Phoenix:
    #      push_annotations(client, annotations, "escalation_quality")
    #
    # Hints:
    #   - span_id is the index of the DataFrame
    #   - run_llm_judge() returns {"label": "PASS"|"FAIL", "explanation": "..."}
    #   - Start with a small batch (first 10 conversations) to test
    #   - Each judge call costs ~$0.001 with gpt-4o-mini
    #
    # ────────────────────────────────────────────────────────────

    # REMOVE THIS PLACEHOLDER once you implement the above:
    print("⚠️  escalation_quality.py is not yet implemented.")
    print("   Complete the TODO in this file to run the eval.")


if __name__ == "__main__":
    run_escalation_eval()
