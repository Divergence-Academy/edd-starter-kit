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
  try {
    const { message, history } = await request.json();

    const traceHandle = startConversationTrace({
      userMessage: message,
      studentName: process.env.STUDENT_NAME || "unknown",
    });

    const response = await chat(message, history || [], traceHandle);

    endConversationTrace(
      traceHandle, response.message, response.toolCalls.length
    );

    return NextResponse.json({
      message: response.message,
      toolCalls: response.toolCalls,
    });
  } catch (error: any) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { message: `Error: ${error.message}`, toolCalls: [] },
      { status: 500 }
    );
  }
}

