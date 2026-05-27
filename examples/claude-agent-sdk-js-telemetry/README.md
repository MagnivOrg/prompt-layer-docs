# Claude PromptLayer Next App

Tiny Next.js app for manually testing PromptLayer's Claude Agent SDK integration.

## Setup

```bash
cp .env.example .env.local
npm install
npm run dev
```

Open the local URL printed by Next.js.

## Environment

- `ANTHROPIC_API_KEY` runs Claude.
- `PROMPTLAYER_API_KEY` enables PromptLayer tracing through `getClaudeConfig()`.

The development server uses port `3333` by default.
