import { createAgentUIStreamResponse } from "ai";
import { chatAgent } from "@/lib/chat-agent";

export const maxDuration = 30;

export async function POST(request: Request) {
  if (!process.env.OPENAI_API_KEY) {
    return new Response(
      "Missing OPENAI_API_KEY. Add it to .env.local before using the chat route.",
      { status: 500 },
    );
  }

  const { messages } = await request.json();

  return createAgentUIStreamResponse({
    agent: chatAgent,
    uiMessages: messages,
  });
}
