/**
 * scripts/run-test-queries.ts
 *
 * Runs all test queries from data/test-queries.json against the local
 * /api/chat endpoint and logs results. Each query is sent as a fresh
 * conversation (no history) to generate independent traces in Phoenix.
 *
 * Usage:
 *   pnpm dev                          # start the app first
 *   npx tsx scripts/run-test-queries.ts
 */

import fs from "fs";
import path from "path";

const API_URL = "http://localhost:3000/api/chat";
const QUERIES_PATH = path.join(__dirname, "..", "data", "test-queries.json");
const RESULTS_PATH = path.join(__dirname, "..", "data", "test-results.json");

// Delay between requests to avoid overwhelming the API
const DELAY_MS = 2000;

interface TestQuery {
  category: string;
  tag: string;
  query: string;
}

interface TestResult extends TestQuery {
  response: string;
  toolCalls: number;
  status: "success" | "error";
  error?: string;
  durationMs: number;
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function sendQuery(query: string): Promise<{
  message: string;
  toolCalls: any[];
}> {
  const res = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: query, history: [] }),
  });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`);
  }

  return res.json();
}

async function main() {
  const queries: TestQuery[] = JSON.parse(
    fs.readFileSync(QUERIES_PATH, "utf-8")
  );

  console.log(`\n🚀 Running ${queries.length} test queries against ${API_URL}\n`);

  const results: TestResult[] = [];
  let passed = 0;
  let failed = 0;

  for (let i = 0; i < queries.length; i++) {
    const q = queries[i];
    const label = `[${i + 1}/${queries.length}] [${q.category}/${q.tag}]`;

    process.stdout.write(`${label} ${q.query.slice(0, 60)}... `);

    const start = Date.now();
    try {
      const res = await sendQuery(q.query);
      const duration = Date.now() - start;

      results.push({
        ...q,
        response: res.message,
        toolCalls: res.toolCalls?.length || 0,
        status: "success",
        durationMs: duration,
      });

      console.log(`✅ ${duration}ms (${res.toolCalls?.length || 0} tools)`);
      passed++;
    } catch (err: any) {
      const duration = Date.now() - start;

      results.push({
        ...q,
        response: "",
        toolCalls: 0,
        status: "error",
        error: err.message,
        durationMs: duration,
      });

      console.log(`❌ ${err.message}`);
      failed++;
    }

    // Wait between requests
    if (i < queries.length - 1) {
      await sleep(DELAY_MS);
    }
  }

  // Write results
  fs.writeFileSync(RESULTS_PATH, JSON.stringify(results, null, 2));

  // Summary
  console.log(`\n${"─".repeat(60)}`);
  console.log(`📊 Results: ${passed} passed, ${failed} failed out of ${queries.length}`);
  console.log(`📁 Full results saved to: data/test-results.json`);

  // Category breakdown
  const categories = ["good", "bad", "ugly"];
  for (const cat of categories) {
    const catResults = results.filter((r) => r.category === cat);
    const catPassed = catResults.filter((r) => r.status === "success").length;
    const avgDuration = Math.round(
      catResults.reduce((sum, r) => sum + r.durationMs, 0) / catResults.length
    );
    console.log(
      `   ${cat.toUpperCase().padEnd(6)} ${catPassed}/${catResults.length} success, avg ${avgDuration}ms`
    );
  }

  console.log(`\n✅ ${passed} traces generated in Phoenix (edd-samanka)\n`);
}

main().catch((err) => {
  console.error("Fatal error:", err);
  process.exit(1);
});
