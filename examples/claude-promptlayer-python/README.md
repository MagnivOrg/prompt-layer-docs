# Claude PromptLayer Python Lab

Tiny Python CLI for manually testing PromptLayer's Claude Agent SDK integration.

It runs one Claude Agent SDK query, enables PromptLayer tracing through `get_claude_config()`, and exposes one in-process MCP tool named `random_number` in the model's default tool set.

## Setup

```bash
cp .env.example .env
uv sync
```

Or with pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m claude_promptlayer_python_lab.main
```

## Environment

- `ANTHROPIC_API_KEY` runs Claude.
- `PROMPTLAYER_API_KEY` enables PromptLayer tracing through `get_claude_config()`.

## Usage

CLI:

```bash
uv run claude-promptlayer-python \
  "Use the random_number tool, then tell me the number it returned."
```

Optional flags:

```bash
uv run claude-promptlayer-python --model sonnet --max-turns 3
```
