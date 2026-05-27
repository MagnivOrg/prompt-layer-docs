from __future__ import annotations

import argparse
import asyncio
import os
import random
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, TypedDict

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)
from dotenv import load_dotenv
from promptlayer.integrations.claude_agents import get_claude_config

DEFAULT_PROMPT = "Use the random_number tool, then tell me the number it returned."
RANDOM_NUMBER_TOOL = "mcp__lab-tools__random_number"


class AgentResult(TypedDict):
    text: str
    messages: list[Any]


@tool("random_number", "Generate a random integer from 1 to 100.", {})
async def random_number(args: dict[str, Any]) -> dict[str, Any]:
    value = random.randint(1, 100)
    return {
        "content": [{"type": "text", "text": str(value)}],
        "structuredContent": {"value": value},
    }


async def run_agent(prompt: str, model: str, max_turns: int) -> AgentResult:
    required_env("ANTHROPIC_API_KEY")
    promptlayer_key = required_env("PROMPTLAYER_API_KEY")

    pl_claude_config = get_claude_config(api_key=promptlayer_key)
    lab_tools = create_sdk_mcp_server(
        name="lab-tools",
        version="0.1.0",
        tools=[random_number],
    )
    options = ClaudeAgentOptions(
        cwd=Path.cwd(),
        model=model,
        max_turns=max_turns,
        tools=[RANDOM_NUMBER_TOOL],
        plugins=[pl_claude_config.plugin],
        mcp_servers={"lab-tools": lab_tools},
        allowed_tools=[RANDOM_NUMBER_TOOL],
        env={**os.environ, **pl_claude_config.env},
    )

    messages: list[Any] = []
    text_parts: list[str] = []
    async for message in query(prompt=prompt, options=options):
        messages.append(serialize_message(message))
        text_parts.extend(extract_text(message))

    return {
        "text": "\n".join(text_parts),
        "messages": messages,
    }


async def run(prompt: str, model: str, max_turns: int) -> None:
    result = await run_agent(prompt, model, max_turns)
    for message in result["messages"]:
        print_message(message)


def print_message(message: Any) -> None:
    if isinstance(message, dict):
        if message.get("type") == "assistant":
            for block in message.get("content", []):
                if block.get("type") == "text":
                    print(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    print(f"[tool] {block.get('name', '')}")
        elif message.get("type") == "result" and message.get("result"):
            print(f"\n[result]\n{message['result']}")
        else:
            print(message)
        return

    print_message(serialize_message(message))


def extract_text(message: Any) -> list[str]:
    parts: list[str] = []

    if isinstance(message, AssistantMessage):
        for block in message.content:
            if isinstance(block, TextBlock):
                parts.append(block.text)
            elif isinstance(block, ToolUseBlock):
                parts.append(f"[tool] {block.name}")
    elif isinstance(message, ResultMessage) and message.result:
        parts.append(message.result)

    return parts


def serialize_message(message: Any) -> Any:
    if is_dataclass(message):
        return asdict(message)
    return message


def required_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing {name}. Add it to .env or export it before running.")
    return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Claude with PromptLayer tracing enabled.")
    parser.add_argument("prompt", nargs="?", default=DEFAULT_PROMPT)
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--max-turns", type=int, default=3)
    return parser.parse_args()


def cli() -> None:
    load_dotenv()
    args = parse_args()
    asyncio.run(run(args.prompt, args.model, args.max_turns))


if __name__ == "__main__":
    cli()
