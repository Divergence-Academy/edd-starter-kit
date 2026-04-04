/**
 * lib/tracing.ts — Arize Phoenix Tracing via OpenTelemetry
 *
 * Sends trace data (LLM calls, tool calls) to Phoenix Cloud
 * so you can inspect them in the Phoenix dashboard.
 *
 * ⚠️  This file is COMPLETE — no changes needed.
 *     Just set PHOENIX_COLLECTOR_ENDPOINT and PHOENIX_API_KEY in .env.
 */

import { trace, SpanStatusCode, context } from "@opentelemetry/api";
import { NodeTracerProvider } from "@opentelemetry/sdk-node/node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-proto";
import { BatchSpanProcessor } from "@opentelemetry/sdk-node/node";
import { Resource } from "@opentelemetry/resources";

// ─── Initialize Tracing ───────────────────────────────────────

let _initialized = false;

function ensureInitialized() {
  if (_initialized) return;

  const endpoint = process.env.PHOENIX_COLLECTOR_ENDPOINT;
  const apiKey = process.env.PHOENIX_API_KEY;
  const studentName = process.env.STUDENT_NAME || "unknown";

  if (!endpoint || !apiKey) {
    console.warn(
      "⚠️  Phoenix tracing disabled: PHOENIX_COLLECTOR_ENDPOINT and PHOENIX_API_KEY not set."
    );
    _initialized = true;
    return;
  }

  const exporter = new OTLPTraceExporter({
    url: `${endpoint}/v1/traces`,
    headers: {
      Authorization: `Bearer ${apiKey}`,
    },
  });

  const provider = new NodeTracerProvider({
    resource: new Resource({
      "service.name": `edd-${studentName}`,
      "student.name": studentName,
    }),
  });

  provider.addSpanProcessor(new BatchSpanProcessor(exporter));
  provider.register();

  _initialized = true;
  console.log(`✅ Phoenix tracing enabled → ${endpoint} (student: ${studentName})`);
}

// ─── Tracing Functions ────────────────────────────────────────

const TRACER_NAME = "edd-adventureworks";

/**
 * Start a new conversation trace. Call this at the beginning of each
 * API request in route.ts.
 *
 * Returns a span that you should end when the request completes.
 */
export function startConversationTrace(metadata: {
  userMessage: string;
  studentName: string;
  scenario?: string;
}) {
  ensureInitialized();
  const tracer = trace.getTracer(TRACER_NAME);

  const span = tracer.startSpan("conversation", {
    attributes: {
      "input.value": metadata.userMessage,
      "student.name": metadata.studentName,
      "scenario": metadata.scenario || "general",
      "openinference.span.kind": "CHAIN",
    },
  });

  return span;
}

/**
 * Trace an LLM call. Records the messages sent and response received.
 */
export function traceLLMCall(
  messages: Array<{ role: string; content: string }>,
  response: string
) {
  ensureInitialized();
  const tracer = trace.getTracer(TRACER_NAME);

  const span = tracer.startSpan("llm_call", {
    attributes: {
      "openinference.span.kind": "LLM",
      "llm.input_messages": JSON.stringify(messages.slice(-5)), // last 5 messages
      "output.value": response,
    },
  });
  span.setStatus({ code: SpanStatusCode.OK });
  span.end();
}

/**
 * Trace a tool call. Records the tool name, arguments, and result.
 */
export function traceToolCall(
  toolName: string,
  args: Record<string, unknown>,
  result: unknown
) {
  ensureInitialized();
  const tracer = trace.getTracer(TRACER_NAME);

  const span = tracer.startSpan(`tool:${toolName}`, {
    attributes: {
      "openinference.span.kind": "TOOL",
      "tool.name": toolName,
      "tool.parameters": JSON.stringify(args),
      "output.value": JSON.stringify(result),
    },
  });
  span.setStatus({ code: SpanStatusCode.OK });
  span.end();
}

/**
 * End a conversation trace with the final response.
 */
export function endConversationTrace(
  span: ReturnType<typeof startConversationTrace>,
  response: string,
  toolCallCount: number
) {
  span.setAttribute("output.value", response);
  span.setAttribute("tool.call_count", toolCallCount);
  span.setStatus({ code: SpanStatusCode.OK });
  span.end();
}
