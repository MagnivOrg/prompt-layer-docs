import { NextResponse } from "next/server";
import { createSdkMcpServer, query, tool, type Options } from "@anthropic-ai/claude-agent-sdk";
import { getClaudeConfig } from "promptlayer/claude-agents";

export const runtime = "nodejs";

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const prompt = String(body.prompt || "").trim();
    const model = String(body.model || "sonnet").trim();

    if (!prompt) {
      return NextResponse.json({ error: "Prompt is required." }, { status: 400 });
    }

    const anthropicKey = requiredEnv("ANTHROPIC_API_KEY");
    const promptLayerKey = requiredEnv("PROMPTLAYER_API_KEY");
    const promptLayer = getClaudeConfig({ apiKey: promptLayerKey });
    const labTools = createSdkMcpServer({
      name: "lab-tools",
      version: "0.1.0",
      alwaysLoad: true,
      tools: [
        tool("random_number", "Generate a random integer from 1 to 100.", {}, async () => {
          const value = Math.floor(Math.random() * 100) + 1;
          return {
            content: [{ type: "text", text: String(value) }],
            structuredContent: { value }
          };
        })
      ]
    });

    const options: Options = {
      cwd: process.cwd(),
      model,
      maxTurns: 3,
      plugins: [promptLayer.plugin],
      mcpServers: {
        "lab-tools": labTools
      },
      allowedTools: ["mcp__lab-tools__random_number"],
      env: {
        ...process.env,
        ANTHROPIC_API_KEY: anthropicKey,
        ...promptLayer.env
      }
    };

    const messages: unknown[] = [];
    for await (const message of query({ prompt, options })) {
      messages.push(message);
    }

    return NextResponse.json({
      text: extractText(messages),
      messages
    });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : String(error) },
      { status: 500 }
    );
  }
}

function requiredEnv(name: "ANTHROPIC_API_KEY" | "PROMPTLAYER_API_KEY") {
  const value = process.env[name]?.trim();
  if (!value) throw new Error(`Missing ${name}. Add it to .env and restart npm run dev.`);
  return value;
}

function extractText(value: unknown) {
  const parts: string[] = [];
  visit(value);
  return parts.join("\n");

  function visit(item: unknown) {
    if (Array.isArray(item)) {
      item.forEach(visit);
      return;
    }
    if (!item || typeof item !== "object") return;

    const record = item as Record<string, unknown>;
    if (typeof record.text === "string") parts.push(record.text);
    Object.values(record).forEach(visit);
  }
}
