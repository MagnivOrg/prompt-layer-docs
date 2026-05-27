import asyncio
import os
from argparse import ArgumentParser

from agents import Agent, ModelSettings, Runner, function_tool
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.shared.reasoning import Reasoning
from promptlayer.integrations.openai_agents import instrument_openai_agents


DEFAULT_MODEL = "gpt-5"
DEFAULT_MESSAGE = (
    "Use the embedding tool to embed exactly this text: "
    "PromptLayer OpenAI embedding trace probe. Then report the embedding "
    "dimensions and token count."
)
EMBEDDING_MODEL = "text-embedding-3-small"

openai_client = OpenAI()


@function_tool
def get_demo_weather(city: str) -> str:
    """Return demo weather for a city."""
    forecasts = {
        "new york": "New York is 61F and cloudy.",
        "san francisco": "San Francisco is 58F and breezy.",
        "tokyo": "Tokyo is 72F with light rain.",
        "london": "London is 55F and overcast.",
    }
    return forecasts.get(city.strip().lower(), f"{city} is 68F and clear in the demo forecast.")


@function_tool
def embed_text(text: str) -> str:
    """Embed text with OpenAI embeddings and return metadata about the result."""
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )
    embedding = response.data[0].embedding
    return (
        f"embedding model: {response.model}; "
        f"dimensions: {len(embedding)}; "
        f"prompt tokens: {response.usage.prompt_tokens}"
    )


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing {name}. Add it to .env or export it.")
    return value


async def run_agent(message: str) -> str:
    required_env("OPENAI_API_KEY")
    required_env("PROMPTLAYER_API_KEY")

    processor = instrument_openai_agents()
    model = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    agent = Agent(
        name="PromptLayer Demo Agent",
        instructions=(
            "You are concise and practical. "
            "If the user asks for weather, call get_demo_weather before answering. "
            "If the user asks to embed text or asks about embedding metadata, call embed_text before answering."
        ),
        model=model,
        model_settings=ModelSettings(
            reasoning=Reasoning(summary="auto"),
            response_include=["reasoning.encrypted_content"],
        ),
        tools=[get_demo_weather, embed_text],
    )

    try:
        result = await Runner.run(agent, message)
        return str(result.final_output)
    finally:
        processor.force_flush()
        processor.shutdown()


def parse_args() -> str:
    parser = ArgumentParser(description="Run an OpenAI Agents SDK example with PromptLayer tracing.")
    parser.add_argument(
        "message",
        nargs="?",
        default=DEFAULT_MESSAGE,
        help="Message to send to the agent.",
    )
    return parser.parse_args().message


def main() -> None:
    load_dotenv()
    print(asyncio.run(run_agent(parse_args())))


if __name__ == "__main__":
    main()
