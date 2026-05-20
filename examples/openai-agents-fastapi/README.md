# PromptLayer OpenAI Agents Web Example

Minimal FastAPI app using PromptLayer's OpenAI Agents SDK tracing integration.

The app follows the PromptLayer OpenAI Agents SDK integration pattern and exports traces to `https://api.promptlayer.com/v1/traces`:

```python
from agents import Agent, Runner
from promptlayer.integrations.openai_agents import instrument_openai_agents

processor = instrument_openai_agents()

agent = Agent(
    name="PromptLayer Demo Agent",
    instructions="You are concise and practical.",
    model="gpt-5",
)

result = await Runner.run(agent, "Say hello.")
processor.force_flush()
```

## Setup

```bash
cd examples/openai-agents-fastapi
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Edit `.env`, then run:

```bash
.venv/bin/uvicorn app:app --port 8000 --env-file .env
```

Open the local URL printed by Uvicorn in your browser.

You can also call the app route directly:

```bash
curl -X POST /api/agent \
  -H "Content-Type: application/json" \
  -d '{"message":"Use the embedding tool to embed exactly this text: PromptLayer OpenAI embedding trace probe. Then report the embedding dimensions and token count."}'
```

## Notes

- `instrument_openai_agents()` must run before the first agent run.
- `force_flush()` sends buffered spans to PromptLayer before the request returns.
- The demo includes `get_demo_weather` and `embed_text` function tools, so tool-call spans are easy to trigger.
- `embed_text` calls the OpenAI embeddings API with `text-embedding-3-small`. The OpenAI Agents SDK currently surfaces that work as a function-tool span, not as a separate native embedding span.
