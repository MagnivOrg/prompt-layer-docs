from __future__ import annotations

"""Local Pydantic AI web app wired to PromptLayer through OpenTelemetry."""

import os
from pathlib import Path

import logfire
from dotenv import load_dotenv
from opentelemetry import trace
from pydantic_ai import Agent, RunContext
from pydantic_ai.models import parse_model_id

from embeddings import search_demo_embeddings


PROMPTLAYER_SERVICE_NAME = "pydantic-ai-promptlayer-demo"
PROMPTLAYER_TRACE_ENDPOINT = "https://api.promptlayer.com/v1/traces"
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
TRUTHY = {"1", "true", "yes"}
FALSY = {"0", "false", "no"}
THINKING_LEVELS = {"minimal", "low", "medium", "high", "xhigh"}
MODEL_API_KEYS = {
    "anthropic": ("ANTHROPIC_API_KEY",),
    "openai": ("OPENAI_API_KEY",),
    "openai-chat": ("OPENAI_API_KEY",),
    "openai-responses": ("OPENAI_API_KEY",),
}


load_dotenv(dotenv_path=ENV_FILE, override=True)


def env_enabled(name: str) -> bool:
    return os.getenv(name, "").lower() in TRUTHY


def required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing {name}. Add it to {ENV_FILE} or export it.")
    return value


def thinking_setting() -> dict[str, bool | str]:
    """Configure model reasoning through Pydantic AI's unified thinking setting."""
    raw_value = required_env("PYDANTIC_AI_THINKING").lower()
    if raw_value in TRUTHY:
        return {"thinking": True}
    if raw_value in FALSY:
        return {"thinking": False}
    if raw_value in THINKING_LEVELS:
        return {"thinking": raw_value}
    raise ValueError(
        "PYDANTIC_AI_THINKING must be one of: true, false, "
        f"{', '.join(sorted(THINKING_LEVELS))}"
    )


def selected_model() -> str:
    return required_env("PYDANTIC_AI_MODEL")


def validate_model_api_key(model: str) -> None:
    provider, _model_name = parse_model_id(model)
    if provider is None:
        raise ValueError(
            f"Could not infer provider for PYDANTIC_AI_MODEL={model!r}. "
            "Use an explicit provider prefix like 'anthropic:' or 'openai:'."
        )

    required_keys = MODEL_API_KEYS.get(provider)
    if not required_keys or any(os.getenv(key) for key in required_keys):
        return

    formatted_keys = " or ".join(required_keys)
    raise ValueError(
        f"PYDANTIC_AI_MODEL={model!r} uses provider {provider!r}, "
        f"so set {formatted_keys} in {ENV_FILE} or your shell environment."
    )


def configure_telemetry() -> None:
    """Configure Pydantic AI instrumentation for PromptLayer and optional Logfire export."""
    if promptlayer_api_key := os.getenv("PROMPTLAYER_API_KEY"):
        os.environ.setdefault(
            "OTEL_EXPORTER_OTLP_TRACES_ENDPOINT",
            PROMPTLAYER_TRACE_ENDPOINT,
        )
        os.environ.setdefault(
            "OTEL_EXPORTER_OTLP_HEADERS",
            f"X-API-KEY={promptlayer_api_key}",
        )
        os.environ.setdefault(
            "OTEL_SERVICE_NAME",
            PROMPTLAYER_SERVICE_NAME,
        )

    logfire.configure(send_to_logfire=env_enabled("SEND_TO_LOGFIRE"))
    logfire.instrument_pydantic_ai()

    if env_enabled("ENABLE_HTTPX_CAPTURE"):
        logfire.instrument_httpx(capture_all=True)


configure_telemetry()
MODEL = selected_model()
validate_model_api_key(MODEL)

agent = Agent(
    MODEL,
    model_settings=thinking_setting(),
    instructions=(
        "You are a concise local demo assistant. Use tools when they help, "
        "and keep answers practical."
    ),
)


@agent.tool
def get_weather(_ctx: RunContext[None], city: str) -> str:
    """Tiny demo tool that tags its span with PromptLayer prompt metadata."""
    span = trace.get_current_span()
    span.set_attribute("promptlayer.prompt.name", "pydantic-chat-weather-demo")
    span.set_attribute("promptlayer.prompt.label", "development")
    return f"The weather in {city} is sunny and 72F."


@agent.instructions
async def embedding_context(ctx: RunContext[None]) -> str:
    """Inject semantic-search context when the user asks about embeddings."""
    if not isinstance(ctx.prompt, str) or "embedding" not in ctx.prompt.lower():
        return ""

    result = await search_demo_embeddings(ctx.prompt)
    return (
        "Embedding demo context: the user's prompt is closest to "
        f"{result.matched_item.title!r} with similarity {result.similarity:.3f}. "
        f"Topic text: {result.matched_item.text}"
    )


app = agent.to_web(
    instructions=(
        "This is a local development chat app. If the user asks about weather, "
        "call the weather tool. If embedding demo context is available, use it "
        "to answer the user."
    )
)
