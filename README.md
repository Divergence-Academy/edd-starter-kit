# AdventureWorks EDD Starter Kit

**Evaluation-Driven Development for AI Systems**
9BRAINS · Divergence Academy · The Helm Program

Build an AI-powered customer support assistant for AdventureWorks bike shop, then write custom evaluations to measure and improve its quality using Arize Phoenix.

---

## Quick Start

```bash
git clone <repo-url>
cd edd-starter-kit
cp .env.example .env        # Fill in your API keys
pnpm install                 # Install dependencies
pnpm dev                     # Start the app → http://localhost:3000
```

## What You Need

| Requirement | Where to Get It |
|---|---|
| Node.js 18+ | [nodejs.org](https://nodejs.org) |
| Python 3.10+ | [python.org](https://python.org) |
| An LLM API key | [OpenAI](https://platform.openai.com/api-keys) or [Anthropic](https://console.anthropic.com) |
| Phoenix Cloud account | Provided by your instructor |

## What's In This Kit

```
edd-starter-kit/
├── data/
│   └── adventureworks.db        ← Pre-loaded SQLite database
├── lib/
│   ├── db.ts                    ← Database connection (done)
│   ├── adventureworks.ts        ← Data access functions (done)
│   ├── tools.ts                 ← Tool wrappers for LLM (done)
│   ├── llmClient.ts             ← 🔧 YOU COMPLETE THIS (Session 3)
│   └── tracing.ts               ← Phoenix tracing setup (done)
├── app/
│   ├── api/chat/route.ts        ← 🔧 YOU COMPLETE THIS (Session 3)
│   └── chat/page.tsx            ← Chat UI (done)
├── evals/
│   ├── requirements.txt         ← Python dependencies for evals
│   ├── eval_helpers.py          ← Shared utilities (done)
│   ├── pricing_accuracy.py      ← 🔧 YOU COMPLETE THIS (Session 5)
│   ├── escalation_quality.py    ← 🔧 YOU COMPLETE THIS (Session 5)
│   └── custom_eval.py           ← 🔧 YOU COMPLETE THIS (Session 7)
├── docs/
│   └── SESSION_GUIDE.md         ← What to do each session
├── .env.example
├── package.json
└── README.md
```

**🔧 = Stubs you complete during the course. Everything else is provided.**

## Environment Variables

```bash
# .env.example — copy to .env and fill in your values

# LLM Provider (pick one)
OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# Arize Phoenix Cloud
PHOENIX_COLLECTOR_ENDPOINT=https://app.phoenix.arize.com
PHOENIX_API_KEY=your-phoenix-api-key

# Your identity (used in trace metadata)
STUDENT_NAME=your-name-here
```

## Setting Up Evals (Python)

The eval scripts run separately from the app. Set them up once:

```bash
cd evals
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run an eval:

```bash
python pricing_accuracy.py
```

Results appear as annotations in your Phoenix dashboard.

## Architecture

```
┌─────────────────────────┐
│  Your Next.js App       │
│                         │
│  Chat UI ──→ /api/chat  │
│              │          │
│         LLM Client      │
│         ↕         ↕     │
│     Tools      Tracing  │
│       ↕           ↓     │
│    SQLite     Phoenix   │
│  (local DB)   (cloud)   │
└─────────────────────────┘

┌─────────────────────────┐
│  Your Eval Scripts      │
│  (Python)               │
│                         │
│  Pull traces ← Phoenix  │
│  Run checks / judges    │
│  Push annotations →     │
│              Phoenix    │
└─────────────────────────┘
```

## Session Progression

| Session | What You Build |
|---|---|
| 1–2 | Concepts only — no code yet |
| 3 | Complete `llmClient.ts` and `route.ts` — get your chatbot working |
| 4 | Generate traces, build reference dataset from Phoenix exports |
| 5 | Complete `pricing_accuracy.py` and `escalation_quality.py` |
| 6 | Improve your system prompt, re-run evals, compare before/after |
| 7 | Complete `custom_eval.py` — design your own metric |
| 8 | Capstone: present your app, evals, and improvement cycle |

## AdventureWorks Data

Your SQLite database contains a trimmed AdventureWorks schema:

| Table | Records | Key Fields |
|---|---|---|
| `Product` | ~500 | ProductID, Name, ListPrice, Color, Size, Category |
| `SalesOrderHeader` | ~31K | SalesOrderID, CustomerID, OrderDate, TotalDue, Status |
| `SalesOrderDetail` | ~121K | OrderQty, UnitPrice, ProductID |
| `Customer` | ~19K | CustomerID, PersonID, StoreID, TerritoryID |

**Test query:** The Mountain-200 Black, 42 should return a ListPrice of $2,294.99.

## Need Help?

- Open the stubs — every `TODO` has comments explaining what to do
- Use Claude Code to ask questions about the codebase
- Check `docs/SESSION_GUIDE.md` for session-specific instructions
- Post in the course Slack channel
