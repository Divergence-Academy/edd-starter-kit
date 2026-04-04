# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AdventureWorks EDD (Evaluation-Driven Development) Starter Kit — a course project for 9BRAINS / Divergence Academy / The Helm Program. Students build an AI-powered customer support chatbot for a bike shop, then write custom evaluation scripts to measure and improve quality using Arize Phoenix.

This is a **teaching scaffold** with intentional stub files marked with `🔧 YOU COMPLETE THIS`. Do not implement the stubs unless the student asks for help with them.

## Commands

```bash
# App (Next.js + TypeScript)
pnpm install          # install dependencies
pnpm dev              # start dev server at http://localhost:3000
pnpm build            # production build

# Evals (Python, separate environment)
cd evals
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python pricing_accuracy.py   # run a specific eval
python escalation_quality.py
python custom_eval.py
```

## Architecture

Two independent runtime systems share a `.env` file and the SQLite database:

**Next.js App** (TypeScript): Chat UI → `/api/chat` route → LLM client (OpenAI tool-calling loop) → AdventureWorks SQLite via better-sqlite3. All LLM calls, tool executions, and conversations are traced to Arize Phoenix Cloud via OpenTelemetry.

**Eval Scripts** (Python): Pull trace spans from Phoenix → evaluate them (code-based comparison or LLM judge) → push PASS/FAIL annotations back to Phoenix.

```
Chat UI (app/api/chat/page.tsx)
  → POST /api/chat (app/api/chat/route.ts)
    → chat() in lib/llmClient.ts
      → OpenAI API with tool definitions from lib/tools.ts
      → tools call lib/adventureworks.ts → lib/db.ts → data/adventureworks.db
      → tracing via lib/tracing.ts → Phoenix Cloud

evals/*.py → Phoenix API (pull spans) → evaluate → Phoenix API (push annotations)
```

## Key Files and Their Status

**Complete (do not modify unless student asks):**
- `lib/db.ts` — SQLite singleton (readonly, WAL mode)
- `lib/adventureworks.ts` — typed data access (products, orders, customers)
- `lib/tools.ts` — OpenAI function-calling tool definitions + executor
- `lib/tracing.ts` — OpenTelemetry → Phoenix Cloud trace export
- `app/api/chat/page.tsx` — Chat UI (client component at `/chat` route, note: lives under `app/api/chat/` not `app/chat/`)
- `app/layout.tsx`, `app/page.tsx` — root layout and redirect to `/chat`
- `evals/eval_helpers.py` — Phoenix client, SQLite lookups, annotation push, LLM judge helper

**Student stubs (Session 3):**
- `lib/llmClient.ts` — implement the OpenAI tool-calling loop with tracing
- `app/api/chat/route.ts` — wire up the POST handler with Phoenix traces

**Student stubs (Session 5):**
- `evals/pricing_accuracy.py` — code-based eval comparing agent prices to SQLite ground truth
- `evals/escalation_quality.py` — LLM judge eval for frustrated-customer escalation

**Student stub (Session 7):**
- `evals/custom_eval.py` — student-designed custom metric

## Important Patterns

- **Tool-calling loop**: `llmClient.ts` must loop (call LLM → execute tool calls → feed results back) until the LLM returns a text response with no tool_calls. Tool definitions use OpenAI function-calling format.
- **Tracing contract**: `route.ts` must call `startConversationTrace()` before `chat()` and `endConversationTrace()` after. Inside `chat()`, call `traceLLMCall()` and `traceToolCall()` for each respective event.
- **Database is readonly**: `lib/db.ts` opens SQLite in readonly mode. All queries are parameterized SELECTs.
- **Eval annotations**: Python evals produce `{span_id, label, score, explanation}` dicts and push them via `push_annotations(client, annotations, metric_name)`.
- **LLM judge pattern**: `run_llm_judge(prompt)` in eval_helpers sends a rubric+conversation to gpt-4o-mini and returns `{"label": "PASS"|"FAIL", "explanation": "..."}`.

## Environment Variables

Defined in `.env` (copy from `.env.example`):
- `OPENAI_API_KEY` — primary LLM provider (or `ANTHROPIC_API_KEY`)
- `PHOENIX_COLLECTOR_ENDPOINT` — Arize Phoenix Cloud URL
- `PHOENIX_API_KEY` — Phoenix auth token
- `STUDENT_NAME` — used in trace metadata and Phoenix project naming (`edd-{STUDENT_NAME}`)

## Verification Test

The Mountain-200 Black, 42 should return a ListPrice of $2,294.99 from the database. Use this as a smoke test for the chatbot and pricing eval.

## Session Progression
- Sessions 1-2 are concepts only. 
- Session 3: implement chatbot. 
- Session 4: generate traces and build reference dataset. 
- Session 5: write evals. 
- Session 6: improve system prompt and re-evaluate. 
- Session 7: custom eval. 
- Session 8: capstone presentation.
