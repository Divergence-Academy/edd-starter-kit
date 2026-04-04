# Session Guide — What To Do Each Session

## Session 1: WTH Are AI Evals?
**No code this session.** Focus on concepts.

- Read Chapter 1 of the course material
- Understand: Why is evaluating AI different from testing traditional software?
- Key vocabulary: evaluation, benchmark, evaluation metric, rubric
- Discuss: What could go wrong with an AdventureWorks bike shop chatbot?

**Prep for next session:** Make sure your environment works:
```bash
git clone <repo>
cp .env.example .env
# Fill in your LLM API key and Phoenix credentials
pnpm install
pnpm dev
# Visit http://localhost:3000/chat — you should see the UI
# (The bot won't work yet — that's Session 3)
```

---

## Session 2: Model vs. Product Evaluations
**No code this session.** Focus on concepts.

- Read Chapter 2 of the course material
- Understand: Model evals ≠ Product evals
- Key insight: Even if GPT-4o scores well on benchmarks, it might quote wrong
  prices or fail to escalate angry customers in YOUR product
- Activity: List 5 things that could go wrong specifically for an AdventureWorks
  support bot (these become your evaluation metrics later)

---

## Session 3: Get Your Bot Working
**🔧 Complete `lib/llmClient.ts` and `app/api/chat/route.ts`**

### Step 1: Complete llmClient.ts
Open `lib/llmClient.ts`. Read the TODO comments. You need to:
1. Call the OpenAI API with messages + tool definitions
2. Handle tool calls: execute them and send results back
3. Loop until you get a text response
4. Add tracing calls for Phoenix

### Step 2: Complete route.ts  
Open `app/api/chat/route.ts`. Read the TODO comments. You need to:
1. Parse the request body
2. Start a Phoenix trace
3. Call chat()
4. End the trace
5. Return the response

### Step 3: Test It
```
How much is the Mountain-200 Black?
→ Should return $2,294.99 (from the database, not hallucinated)

What's the status of order 43659?
→ Should return real order details

Recommend a bike for commuting under $1000
→ Should search products and suggest options
```

### Step 4: Check Phoenix
Log into Phoenix Cloud. You should see traces appearing in your project.
Click into a trace to see the conversation span, LLM call span, and tool spans.

---

## Session 4: Build Your Reference Dataset
**No new code.** Analytical work in Phoenix + spreadsheet.

### Step 1: Generate Diverse Traces
Chat with your bot using different scenarios:
- Pricing questions (correct and tricky ones)
- Order lookups (valid and invalid order IDs)
- Product recommendations (broad and narrow)
- Frustrated customer messages ("This is terrible, I want a manager!")
- Out-of-scope questions ("What's the weather?")

### Step 2: Export and Analyze
In Phoenix, export your traces. For each interaction, record:

| Input | Expected Behavior | Actual Behavior | Scenario Tag | Ground Truth |
|---|---|---|---|---|
| "How much is the Mountain-200?" | Quote $2,294.99 from DB | ??? | pricing | ??? |
| "I'm furious, get me a manager!" | Escalate to human | ??? | escalation | ??? |

### Step 3: Identify Error Patterns
Group your FAIL cases. What patterns emerge?
These patterns become your evaluation metrics in Session 5.

---

## Session 5: Write Your First Custom Evals
**🔧 Complete `evals/pricing_accuracy.py` and `evals/escalation_quality.py`**

### Setup the Eval Environment
```bash
cd evals
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Step 1: Complete pricing_accuracy.py
This is a CODE-BASED eval. Read the TODO comments.
Run it: `python pricing_accuracy.py`
Check Phoenix: you should see pricing_accuracy annotations on your spans.

### Step 2: Complete escalation_quality.py
This is an LLM JUDGE eval. Read the TODO comments.
Review the rubric — does it match what you found in Session 4?
Run it: `python escalation_quality.py`
Check Phoenix: you should see escalation_quality annotations.

### Step 3: Analyze Results
In Phoenix, filter by eval label = FAIL. What's going wrong?

---

## Session 6: The Improvement Cycle
**No new stubs.** This session is about the flywheel.

### Step 1: Fix Your System
Based on your Session 5 FAIL cases, improve your bot:
- Edit the SYSTEM_PROMPT in llmClient.ts
- Improve tool descriptions in tools.ts
- Add edge case handling

### Step 2: Re-run and Compare
Generate new traces with the same test inputs.
Re-run your evals. Compare pass rates before vs. after.

This is the EDD flywheel: Evaluate → Identify failures → Improve → Re-evaluate.

---

## Session 7: Design Your Own Metric
**🔧 Complete `evals/custom_eval.py`**

### Step 1: Choose Your Metric
Based on everything you've learned, identify a quality dimension
that pricing_accuracy and escalation_quality don't cover.
See the suggestions in custom_eval.py for ideas.

### Step 2: Write the Rubric
Define clear PASS/FAIL criteria. Include edge cases and examples.

### Step 3: Implement and Run
Complete custom_eval.py. Run it. Check Phoenix.

### Step 4: Validate Your Judge (if LLM-based)
Compare your LLM judge's labels against your reference dataset.
Calculate True Positive Rate and True Negative Rate.
Does your judge agree with human judgment?

---

## Session 8: Capstone
**10-minute presentation + live demo + 5-minute Q&A**

### Your Presentation Should Cover:
1. **Your system** — show the architecture (app + Phoenix + evals)
2. **Your metrics** — explain what you measure and why
3. **Your rubrics** — show a rubric and explain your design decisions
4. **The flywheel** — demonstrate a before/after improvement cycle
5. **Your custom eval** — explain what it measures and how you validated it

### Live Demo:
- Chat with your bot
- Show traces in Phoenix
- Show eval annotations and pass rates
- Show a before/after comparison

### Rubric (how you'll be scored):
| Category | Weight | Criteria |
|---|---|---|
| Architecture | 30% | Clear system design, appropriate tool choices |
| Technical Execution | 30% | Working demo, evals produce reliable results |
| Analysis | 20% | Thoughtful metric design, validated judge |
| Communication | 20% | Clear presentation, handles Q&A, business case |

**Have backup screenshots in case of live demo issues.**
