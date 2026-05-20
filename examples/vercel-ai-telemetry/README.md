# Relay Chat Demo

A simple Next.js App Router scaffold for a chat app built with the Vercel AI SDK and the direct OpenAI provider.

## What is included

- A streaming chat interface powered by `useChat`
- A `ToolLoopAgent` with three mocked server-side tools
- Typed UI messages via `InferAgentUIMessage`
- An API route that streams agent responses with `createAgentUIStreamResponse`

## Setup

1. Install dependencies:

```bash
npm install
```

2. Create a local env file from the example:

```bash
cp .env.example .env.local
```

3. Add your OpenAI API key to `.env.local`:

```bash
OPENAI_API_KEY=your_key_here
```

4. Optional: add PromptLayer tracing credentials if you want OpenTelemetry traces exported to PromptLayer:

```bash
PROMPTLAYER_API_KEY=your_promptlayer_key_here
OTEL_SERVICE_NAME=vercel-chat-app
```

5. Start the app:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Model configuration

The scaffold uses the direct OpenAI provider from `@ai-sdk/openai` and defaults to `gpt-5`, matching the current example on the AI SDK OpenAI provider docs. You can override that with:

```bash
OPENAI_MODEL=your_preferred_model
```

## PromptLayer tracing

This app can export Vercel AI SDK traces to PromptLayer using OpenTelemetry.

- `PROMPTLAYER_API_KEY` enables OTLP trace export to PromptLayer
- `OTEL_SERVICE_NAME` optionally overrides the service name shown in traces

If `PROMPTLAYER_API_KEY` is not set, the app still runs normally and skips PromptLayer export.

## Useful scripts

- `npm run dev`
- `npm run lint`
- `npm run typecheck`
