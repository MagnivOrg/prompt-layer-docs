# PromptLayer OpenAI Agents SDK JS Example

Minimal TypeScript CLI example using PromptLayer's OpenAI Agents SDK tracing integration.

This example follows the PromptLayer OpenAI Agents SDK JavaScript integration pattern and exports traces to `https://api.promptlayer.com/v1/traces`:

```ts
import { Agent, run } from "@openai/agents";
import { instrumentOpenAIAgents } from "promptlayer/openai-agents";

const processor = await instrumentOpenAIAgents();

const agent = new Agent({
  name: "PromptLayer Demo Agent",
  instructions: "You are concise and practical.",
  model: "gpt-5",
});

const result = await run(agent, "Say hello.");
await processor.forceFlush();
await processor.shutdown();
```

## Setup

This docs example intentionally installs the supported PromptLayer JavaScript package from npm through the `promptlayer` dependency in `package.json`. Do not commit a local `file:`, `link:`, or `workspace:` dependency here.

```bash
cd examples/openai-agent-sdk-js-telemetry
npm install
cp .env.example .env
```

Edit `.env`, then run:

```bash
npm run dev
```

You can also pass a custom message:

```bash
npm run dev -- "What is the weather in Tokyo?"
```

## Environment

- `OPENAI_API_KEY` runs the OpenAI Agents SDK.
- `PROMPTLAYER_API_KEY` enables PromptLayer tracing through `instrumentOpenAIAgents()`.
- `OPENAI_MODEL` optionally overrides the default `gpt-5` model.

## Notes

- Requires Node.js 22 or later, matching the OpenAI Agents SDK JavaScript runtime requirement.
- `instrumentOpenAIAgents()` must run before the first agent run.
- `forceFlush()` and `shutdown()` send buffered spans to PromptLayer before the process exits.
- The demo includes a `get_demo_weather` function tool, so tool-call spans are easy to trigger.
