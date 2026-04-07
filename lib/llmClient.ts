/**
 * lib/llmClient.ts — LLM Client with Tool Calling
 *
 * 🔧 YOU COMPLETE THIS FILE (Session 3)
 *
 * This file handles communication with your LLM provider (OpenAI or Anthropic).
 * It sends user messages along with tool definitions, executes any tool calls
 * the LLM requests, and returns the final response.
 *
 * The tool-calling loop works like this:
 *   1. Send user message + tool definitions to LLM
 *   2. If LLM wants to call a tool → execute it, send result back
 *   3. Repeat until LLM returns a text response (no more tool calls)
 *   4. Return the final text
 */

import OpenAI from "openai";
import { TOOL_DEFINITIONS, executeTool, type ToolResult } from "./tools";
import { traceToolCall, traceLLMCall, type TraceHandle } from "./tracing";

// ─── Configuration ────────────────────────────────────────────

const SYSTEM_PROMPT = `You are a helpful customer support assistant for AdventureWorks, 
a bicycle and outdoor equipment company. 

Your responsibilities:
- Help customers find products and check prices
- Look up order status and order details  
- Answer questions about the product catalog
- Be friendly, professional, and accurate

Important rules:
- ALWAYS use the lookup_product tool to get real prices. Never guess or make up prices.
- ALWAYS use the lookup_order tool to check order status. Never guess order details.
- If a customer seems very frustrated or mentions legal action, switching providers, 
  or demanding a manager, tell them you are escalating to a human agent.
- If you don't know something, say so. Don't make things up.
- Keep responses concise and helpful.`;

// ─── Types ────────────────────────────────────────────────────

export interface ChatMessage {
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  tool_call_id?: string;
  tool_calls?: unknown[];
}

export interface ChatResponse {
  message: string;
  toolCalls: ToolResult[];
}

// ─── Main Function ────────────────────────────────────────────

/**
 * Send a user message to the LLM and get a response.
 * Handles the full tool-calling loop automatically.
 *
 * @param userMessage - The user's message
 * @param conversationHistory - Previous messages in this conversation
 * @returns The assistant's text response and any tool calls made
 */
export async function chat(
  userMessage: string,
  conversationHistory: ChatMessage[] = [],
  traceHandle?: TraceHandle
): Promise<ChatResponse> {
  const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
  });

  const allToolCalls: ToolResult[] = [];

  const messages: ChatMessage[] = [
    { role: "system", content: SYSTEM_PROMPT },
    ...conversationHistory,
    { role: "user", content: userMessage },
  ];

  // Tool-calling loop
  while (true) {
    const response = await client.chat.completions.create({
      model: "gpt-4o-mini",
      messages: messages as any,
      tools: TOOL_DEFINITIONS,
    });

    const choice = response.choices[0];
    const assistantMessage = choice.message;

    // Check if the LLM wants to call tools
    if (assistantMessage.tool_calls && assistantMessage.tool_calls.length > 0) {
      messages.push(assistantMessage as any);

      for (const toolCall of assistantMessage.tool_calls) {
        const name = toolCall.function.name;
        const args = JSON.parse(toolCall.function.arguments);

        const result = executeTool(name, args);
        if (traceHandle) traceToolCall(traceHandle.ctx, name, args, result);
        allToolCalls.push({ toolName: name, args, result });

        messages.push({
          role: "tool",
          content: JSON.stringify(result),
          tool_call_id: toolCall.id,
        } as any);
      }
      continue;
    }

    // No tool calls — final text response
    const responseText = assistantMessage.content
      || "I'm sorry, I couldn't generate a response.";

    if (traceHandle) {
      traceLLMCall(
        traceHandle.ctx,
        messages.map((m) => ({
          role: m.role,
          content: typeof m.content === 'string' ? m.content : ''
        })),
        responseText,
        "gpt-4o-mini"
      );
    }

    return { message: responseText, toolCalls: allToolCalls };
  }
}
