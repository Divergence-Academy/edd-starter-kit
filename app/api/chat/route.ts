/**
 * app/api/chat/route.ts — Chat API endpoint
 *
 * 🔧 YOU COMPLETE THIS FILE (Session 3)
 *
 * This API route receives user messages from the chat UI,
 * passes them to the LLM client, and returns the response.
 * It also starts and ends Phoenix traces for each request.
 */

import { NextRequest, NextResponse } from "next/server";
import { chat } from "@/lib/llmClient";
import {
  startConversationTrace,
  endConversationTrace,
} from "@/lib/tracing";

export async function POST(request: NextRequest) {
  // ────────────────────────────────────────────────────────────
  // TODO: Implement the chat API endpoint
  //
  // Steps:
  //   1. Parse the request body to get { message, history }
  //      - message: string (the user's new message)
  //      - history: ChatMessage[] (previous messages in the conversation)
  //
  //   2. Start a Phoenix conversation trace:
  //      const span = startConversationTrace({
  //        userMessage: message,
  //        studentName: process.env.STUDENT_NAME || "unknown",
  //      });
  //
  //   3. Call the chat() function from llmClient.ts:
  //      const response = await chat(message, history);
  //
  //   4. End the Phoenix trace:
  //      endConversationTrace(span, response.message, response.toolCalls.length);
  //
  //   5. Return the response as JSON:
  //      return NextResponse.json({
  //        message: response.message,
  //        toolCalls: response.toolCalls,
  //      });
  //
  //   6. Wrap everything in try/catch. On error:
  //      - End the span with an error status
  //      - Return a 500 response with the error message
  //
  // ────────────────────────────────────────────────────────────

  // REMOVE THIS PLACEHOLDER once you implement the above:
  return NextResponse.json(
    {
      message:
        "⚠️ route.ts is not yet implemented. Complete the TODO in this file.",
      toolCalls: [],
    },
    { status: 501 }
  );
}
