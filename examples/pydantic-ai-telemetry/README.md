# Pydantic AI Chat App With PromptLayer OTel

Minimal local Pydantic AI web chat app that forwards Pydantic AI OpenTelemetry traces to PromptLayer.

## Structure

- `app.py` defines the chat agent, weather tool, dynamic embedding context, and telemetry setup.
- `embeddings.py` contains the native Pydantic AI embeddings demo.

## Stack

- Python 3.11+
- `uv`
- `pydantic-ai-slim[web,openai,anthropic,logfire]`
- `logfire`
- OpenTelemetry OTLP HTTP exporter
- PromptLayer OTLP ingest

## Setup

```bash
cp .env.example .env
```

Fill in:

- `ANTHROPIC_API_KEY` for the default Anthropic chat model
- `OPENAI_API_KEY` for OpenAI chat models and the default embeddings demo
- `PROMPTLAYER_API_KEY`
- `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://api.promptlayer.com/v1/traces`
- `SEND_TO_LOGFIRE=true` if you also want to send traces to Logfire
- `PYDANTIC_AI_MODEL` to choose a Pydantic AI model
- `PYDANTIC_AI_THINKING` to control reasoning effort
- `PYDANTIC_AI_EMBEDDING_MODEL` if you want to override the embeddings demo model

The app validates the API key that matches `PYDANTIC_AI_MODEL`. For example,
`anthropic:*` requires `ANTHROPIC_API_KEY`, while `openai:*`,
`openai-chat:*`, and `openai-responses:*` require `OPENAI_API_KEY`.

Install dependencies:

```bash
uv sync
```

Run the local web chat:

```bash
uv run uvicorn app:app --port 7932
```

Open the local URL printed by Uvicorn.

## Telemetry

By default, the app forwards Pydantic AI OpenTelemetry traces to PromptLayer at `https://api.promptlayer.com/v1/traces` when these env vars are configured:

- `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=https://api.promptlayer.com/v1/traces`
- `OTEL_EXPORTER_OTLP_HEADERS=X-API-KEY=<PROMPTLAYER_API_KEY>`
- `OTEL_SERVICE_NAME=pydantic-ai-promptlayer-demo`

Logfire export is optional. To also send traces to Logfire, set this in `.env`:

```bash
SEND_TO_LOGFIRE=true
```

Leave `SEND_TO_LOGFIRE` unset to skip Logfire export.

Then authenticate locally:

```bash
uv run logfire auth
```

PromptLayer should show a trace after you send a chat message. Tool calls appear as child spans when the model invokes `get_weather`.

## Embeddings Demo

To see how native embeddings appear inside an agent run without using a tool, send a question like this:

```text
Use embeddings to find the local demo topic closest to "how are traces exported to PromptLayer?"
```

```text
Use embeddings to search for "what part of the demo uses tools?"
```

```text
Use embeddings to find the closest topic for "how does semantic search compare text?"
```

PromptLayer should show the agent run with native Pydantic AI embedding spans and the chat model span. The embedding spans use `gen_ai.operation.name=embeddings`.

Raw HTTP capture is disabled by default because it can include prompt and response content. Enable it only when you need provider-level request debugging:

```bash
ENABLE_HTTPX_CAPTURE=true uv run uvicorn app:app --port 7932
```
