import { NextResponse } from "next/server";
import { trace, type Span } from "@opentelemetry/api";

import { runItineraryPrompt } from "../../itinerary";

// LangChain/OpenAI and OTEL context management need the Node runtime, not the Edge runtime.
export const runtime = "nodejs";
// Always execute the route on demand so each chat turn creates fresh spans.
export const dynamic = "force-dynamic";

type ChatRequestBody = {
  input?: unknown;
};

async function withSpan<T>(name: string, fn: (span: Span) => Promise<T>): Promise<T> {
  return trace.getTracer("langchain-itinerary-app").startActiveSpan(name, async (span) => {
    try {
      return await fn(span);
    } finally {
      span.end();
    }
  });
}

export async function POST(request: Request) {
  let body: ChatRequestBody;

  try {
    // The client sends exactly one field: { input }, which becomes the human message.
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Request body must be valid JSON." }, { status: 400 });
  }

  const input = typeof body.input === "string" ? body.input.trim() : "";
  if (!input) {
    return NextResponse.json({ error: "Message is required." }, { status: 400 });
  }

  const reply = await withSpan("itinerary.request", (span) => {
    span.setAttribute("langsmith.span.kind", "chain");
    return runItineraryPrompt(input);
  });

  return NextResponse.json({ reply });
}
