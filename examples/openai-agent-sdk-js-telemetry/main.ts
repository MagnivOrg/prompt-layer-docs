import "dotenv/config";

import { Agent, run, tool } from "@openai/agents";
import { instrumentOpenAIAgents } from "promptlayer/openai-agents";
import { z } from "zod";

const DEFAULT_MODEL = "gpt-5";
const DEFAULT_MESSAGE = "Use the weather tool for Tokyo, then summarize the forecast in one sentence.";

const getDemoWeather = tool({
  name: "get_demo_weather",
  description: "Return demo weather for a city.",
  parameters: z.object({
    city: z.string().describe("City to look up in the demo forecast."),
  }),
  execute: async ({ city }) => {
    const forecasts: Record<string, string> = {
      "new york": "New York is 61F and cloudy.",
      "san francisco": "San Francisco is 58F and breezy.",
      tokyo: "Tokyo is 72F with light rain.",
      london: "London is 55F and overcast.",
    };

    return forecasts[city.trim().toLowerCase()] ?? `${city} is 68F and clear in the demo forecast.`;
  },
});

function requiredEnv(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`Missing ${name}. Add it to .env or export it.`);
  }
  return value;
}

function parseMessage(): string {
  const message = process.argv.slice(2).join(" ").trim();
  return message || DEFAULT_MESSAGE;
}

async function main(): Promise<void> {
  requiredEnv("OPENAI_API_KEY");
  requiredEnv("PROMPTLAYER_API_KEY");

  const processor = await instrumentOpenAIAgents();
  const model = process.env.OPENAI_MODEL?.trim() || DEFAULT_MODEL;

  const agent = new Agent({
    name: "PromptLayer Demo Agent",
    instructions: [
      "You are concise and practical.",
      "If the user asks for weather, call get_demo_weather before answering.",
    ].join(" "),
    model,
    modelSettings: {
      reasoning: { summary: "auto" },
    },
    tools: [getDemoWeather],
  });

  try {
    const result = await run(agent, parseMessage(), { maxTurns: 4 });
    console.log(result.finalOutput);
  } finally {
    await processor.forceFlush();
    await processor.shutdown();
  }
}

main().catch((error: unknown) => {
  console.error(error instanceof Error ? error.message : error);
  process.exitCode = 1;
});
