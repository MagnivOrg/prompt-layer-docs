# Pocket Trip Pal

A small Next.js chat app that demonstrates a traced LangChain itinerary assistant.

The frontend keeps chat history in local React state. The `/api/chat` route runs OpenAI or Anthropic through LangChain, forces a mocked `lookup_destination_highlights` tool call, and can export OpenTelemetry spans for the route, LLM calls, and tool execution.

## Setup

Install dependencies:

```bash
npm install
```

Create `.env`:

```bash
cp .env.example .env
```

Set at least:

```bash
OPENAI_API_KEY=
```

To use Anthropic instead:

```bash
LANGCHAIN_MODEL_PROVIDER=anthropic
ANTHROPIC_API_KEY=
ANTHROPIC_MODEL=claude-sonnet-4-6
ANTHROPIC_THINKING=medium
```

Start the development server:

```bash
npm run dev
```

## Environment Variables

- `LANGCHAIN_MODEL_PROVIDER`: optional, `openai` or `anthropic`; defaults to `openai`.
- `OPENAI_API_KEY`: required server-side OpenAI key when using OpenAI.
- `OPENAI_MODEL`: optional, defaults to `gpt-4o-mini`.
- `ANTHROPIC_API_KEY`: required server-side Anthropic key when using Anthropic.
- `ANTHROPIC_MODEL`: optional, defaults to `claude-sonnet-4-6`.
- `ANTHROPIC_THINKING`: optional Anthropic effort value. When set, the app enables adaptive thinking and passes the value to `ChatAnthropic` as `outputConfig.effort`.
- `LANGSMITH_TRACING`, `LANGSMITH_TRACING_MODE`, `LANGCHAIN_CALLBACKS_BACKGROUND`: enable LangChain OTEL tracing mode.
- `OTEL_EXPORTER_OTLP_ENDPOINT`: PromptLayer OTLP endpoint, `https://api.promptlayer.com/v1/traces`.
- `OTEL_EXPORTER_OTLP_HEADERS`: PromptLayer OTLP API key header, `X-API-KEY=<PROMPTLAYER_API_KEY>`.

## Scripts

- `npm run dev`: run the local dev server.
- `npm run build`: create a production build.
- `npm run start`: serve the production build.
- `npm run lint`: run ESLint.

## Project Structure

```text
src/app/page.tsx          Main page shell
src/app/chat-client.tsx   Client-side chat UI and fetch logic
src/app/api/chat/route.ts API route validation, tracing, and response handling
src/app/itinerary.ts      LangChain prompt, tool definition, and LLM orchestration
src/instrumentation.ts    OpenTelemetry and LangSmith setup
instrumentation.ts        Next.js root instrumentation export
```

## Request Flow

1. The user sends a message from the chat UI.
2. The client posts `{ input }` to `/api/chat`.
3. The API route validates the request and opens an `itinerary.request` span.
4. `runItineraryPrompt` creates a LangChain chat model for the configured provider with the mocked destination tool bound.
5. The first model call is forced to call `lookup_destination_highlights`.
6. The tool result is added back into the message history.
7. A follow-up model call returns the final user-facing itinerary response.

## Notes

Chat history is not persisted. Destination data is mocked in `getDestinationHighlights` inside `src/app/itinerary.ts`. `.env` is ignored by git.
