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
import { traceToolCall, traceLLMCall } from "./tracing";

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
  conversationHistory: ChatMessage[] = []
): Promise<ChatResponse> {
  const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
  });

  const allToolCalls: ToolResult[] = [];

  // Build the messages array with system prompt + history + new message
  const messages: ChatMessage[] = [
    { role: "system", content: SYSTEM_PROMPT },
    ...conversationHistory,
    { role: "user", content: userMessage },
  ];

  // ────────────────────────────────────────────────────────────
  // TODO: Implement the tool-calling loop
  //
  // Steps:
  //   1. Call client.chat.completions.create() with:
  //      - model: "gpt-4o-mini"
  //      - messages: messages (cast as needed)
  //      - tools: TOOL_DEFINITIONS
  //
  //   2. Check the response:
  //      - If the LLM returned tool_calls:
  //          a. For each tool call, extract the function name and arguments
  //          b. Call executeTool(name, args) to get the result
  //          c. Call traceToolCall(name, args, result) for Phoenix tracing
  //          d. Collect the tool result into allToolCalls
  //          e. Add the assistant message (with tool_calls) and tool results
  //             back into the messages array
  //          f. Call the LLM again (loop back to step 1)
  //
  //      - If the LLM returned a text response (no tool_calls):
  //          a. Call traceLLMCall(messages, responseText) for Phoenix tracing
  //          b. Return { message: responseText, toolCalls: allToolCalls }
  //
  // Hint: Use a while(true) loop. Break when you get a text response.
  //
  // Hint: Tool call arguments come as a JSON string. Parse them:
  //   const args = JSON.parse(toolCall.function.arguments);
  //
  // Hint: Tool results go back to the LLM like this:
  //   { role: "tool", content: JSON.stringify(result), tool_call_id: toolCall.id }
  //
  // ────────────────────────────────────────────────────────────

  // REMOVE THIS PLACEHOLDER once you implement the above:
  return {
    message:
      "⚠️ llmClient.ts is not yet implemented. Complete the TODO in this file to connect to your LLM.",
    toolCalls: [],
  };
}
