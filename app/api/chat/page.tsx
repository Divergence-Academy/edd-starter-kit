/**
 * app/chat/page.tsx — Chat Interface
 *
 * A simple chat UI for talking to the AdventureWorks assistant.
 * Sends messages to /api/chat and displays responses.
 *
 * ⚠️  This file is COMPLETE — no changes needed.
 */

"use client";

import { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ToolCall {
  toolName: string;
  args: Record<string, unknown>;
  result: unknown;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [lastToolCalls, setLastToolCalls] = useState<ToolCall[]>([]);
  const [showTools, setShowTools] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setLoading(true);
    setLastToolCalls([]);

    const updatedMessages: Message[] = [
      ...messages,
      { role: "user", content: userMessage },
    ];
    setMessages(updatedMessages);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage,
          history: updatedMessages.map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      });

      const data = await res.json();

      setMessages([
        ...updatedMessages,
        { role: "assistant", content: data.message },
      ]);

      if (data.toolCalls?.length > 0) {
        setLastToolCalls(data.toolCalls);
      }
    } catch (err) {
      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Check the console for errors.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        maxWidth: 700,
        margin: "0 auto",
        padding: 24,
        fontFamily: "system-ui, sans-serif",
      }}
    >
      <h1 style={{ fontSize: 22, marginBottom: 4 }}>
        🚲 AdventureWorks Support
      </h1>
      <p style={{ color: "#666", fontSize: 14, marginBottom: 20 }}>
        Ask about products, prices, orders, or recommendations.
      </p>

      {/* Messages */}
      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: 8,
          height: 450,
          overflowY: "auto",
          padding: 16,
          marginBottom: 12,
          backgroundColor: "#fafafa",
        }}
      >
        {messages.length === 0 && (
          <p style={{ color: "#999", textAlign: "center", marginTop: 180 }}>
            Try: "How much is the Mountain-200 Black?" or "Show me bikes under
            $1000"
          </p>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              marginBottom: 12,
              textAlign: msg.role === "user" ? "right" : "left",
            }}
          >
            <span
              style={{
                display: "inline-block",
                padding: "8px 14px",
                borderRadius: 12,
                maxWidth: "80%",
                fontSize: 14,
                lineHeight: 1.5,
                backgroundColor: msg.role === "user" ? "#0066cc" : "#e8e8e8",
                color: msg.role === "user" ? "#fff" : "#222",
              }}
            >
              {msg.content}
            </span>
          </div>
        ))}

        {loading && (
          <div style={{ textAlign: "left", marginBottom: 12 }}>
            <span
              style={{
                display: "inline-block",
                padding: "8px 14px",
                borderRadius: 12,
                backgroundColor: "#e8e8e8",
                color: "#999",
                fontSize: 14,
              }}
            >
              Thinking...
            </span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{ display: "flex", gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask a question..."
          disabled={loading}
          style={{
            flex: 1,
            padding: "10px 14px",
            borderRadius: 8,
            border: "1px solid #ccc",
            fontSize: 14,
          }}
        />
        <button
          onClick={sendMessage}
          disabled={loading || !input.trim()}
          style={{
            padding: "10px 20px",
            borderRadius: 8,
            border: "none",
            backgroundColor: "#0066cc",
            color: "#fff",
            fontSize: 14,
            cursor: loading ? "not-allowed" : "pointer",
            opacity: loading || !input.trim() ? 0.5 : 1,
          }}
        >
          Send
        </button>
      </div>

      {/* Tool Call Inspector */}
      {lastToolCalls.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <button
            onClick={() => setShowTools(!showTools)}
            style={{
              background: "none",
              border: "1px solid #ccc",
              borderRadius: 6,
              padding: "4px 12px",
              fontSize: 12,
              color: "#666",
              cursor: "pointer",
            }}
          >
            {showTools ? "Hide" : "Show"} tool calls ({lastToolCalls.length})
          </button>

          {showTools && (
            <pre
              style={{
                marginTop: 8,
                padding: 12,
                backgroundColor: "#f0f0f0",
                borderRadius: 8,
                fontSize: 11,
                overflow: "auto",
                maxHeight: 200,
              }}
            >
              {JSON.stringify(lastToolCalls, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
