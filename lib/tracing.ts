/**
 * lib/tracing.ts — Arize Phoenix Tracing via OpenTelemetry
 *
 * Sends trace data (LLM calls, tool calls) to Phoenix Cloud
 * so you can inspect them in the Phoenix dashboard.
 *
 * Spans follow OpenInference conventions and are nested:
 *   conversation (CHAIN)
 *     ├── tool:lookup_product (TOOL)
 *     └── llm_call (LLM)
 */

import { trace, SpanStatusCode, context, type Context } from "@opentelemetry/api";
import { NodeTracerProvider } from "@opentelemetry/sdk-trace-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-proto";
import { BatchSpanProcessor, type SpanProcessor, type ReadableSpan } from "@opentelemetry/sdk-trace-base";
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
      "phoenix-project-name": `edd-${studentName}`,
    },
  });

  const provider = new NodeTracerProvider({
    resource: new Resource({
      "openinference.project.name": `edd-${studentName}`,
      "student.name": studentName,
    }),
  });

  // Filter out Next.js internal spans so only our app spans reach Phoenix
  const batchProcessor = new BatchSpanProcessor(exporter);
  const filteringProcessor: SpanProcessor = {
    onStart(span) { batchProcessor.onStart(span); },
    onEnd(span: ReadableSpan) {
      const name = span.name;
      // Drop Next.js framework spans (POST /api/*, start response, resolve page, etc.)
      if (name.startsWith("POST ") || name.startsWith("GET ") ||
          name === "start response" || name.startsWith("resolve page") ||
          name.startsWith("executing api route")) {
        return;
      }
      batchProcessor.onEnd(span);
    },
    shutdown() { return batchProcessor.shutdown(); },
    forceFlush() { return batchProcessor.forceFlush(); },
  };

  provider.addSpanProcessor(filteringProcessor);
  provider.register();

  _initialized = true;
  console.log(`✅ Phoenix tracing enabled → ${endpoint} (student: ${studentName})`);
}

// ─── Types ───────────────────────────────────────────────────

export interface TraceHandle {
  span: ReturnType<ReturnType<typeof trace.getTracer>["startSpan"]>;
  ctx: Context;
}

// ─── Tracing Functions ────────────────────────────────────────

const TRACER_NAME = "edd-adventureworks";

/**
 * Start a new conversation trace. Returns a handle with the span
 * and its context so child spans (LLM, tool) nest correctly.
 */
export function startConversationTrace(metadata: {
  userMessage: string;
  studentName: string;
  scenario?: string;
}): TraceHandle {
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

  const ctx = trace.setSpan(context.active(), span);
  return { span, ctx };
}

/**
 * Trace an LLM call as a child of the conversation span.
 */
export function traceLLMCall(
  parentCtx: Context,
  messages: Array<{ role: string; content: string }>,
  response: string,
  modelName: string = "gpt-4o-mini"
) {
  ensureInitialized();
  const tracer = trace.getTracer(TRACER_NAME);

  context.with(parentCtx, () => {
    const attrs: Record<string, string | number> = {
      "openinference.span.kind": "LLM",
      "llm.model_name": modelName,
      "output.value": response,
    };

    // Structured message attributes per OpenInference convention
    const recentMessages = messages.slice(-5);
    recentMessages.forEach((msg, i) => {
      attrs[`llm.input_messages.${i}.message.role`] = msg.role;
      attrs[`llm.input_messages.${i}.message.content`] = msg.content || "";
    });

    const span = tracer.startSpan("llm_call", { attributes: attrs });
    span.setStatus({ code: SpanStatusCode.OK });
    span.end();
  });
}

/**
 * Trace a tool call as a child of the conversation span.
 */
export function traceToolCall(
  parentCtx: Context,
  toolName: string,
  args: Record<string, unknown>,
  result: unknown
) {
  ensureInitialized();
  const tracer = trace.getTracer(TRACER_NAME);

  context.with(parentCtx, () => {
    const span = tracer.startSpan(`tool:${toolName}`, {
      attributes: {
        "openinference.span.kind": "TOOL",
        "tool.name": toolName,
        "input.value": JSON.stringify(args),
        "output.value": JSON.stringify(result),
      },
    });
    span.setStatus({ code: SpanStatusCode.OK });
    span.end();
  });
}

/**
 * End a conversation trace with the final response.
 */
export function endConversationTrace(
  handle: TraceHandle,
  response: string,
  toolCallCount: number
) {
  handle.span.setAttribute("output.value", response);
  handle.span.setAttribute("tool.call_count", toolCallCount);
  handle.span.setStatus({ code: SpanStatusCode.OK });
  handle.span.end();
}
