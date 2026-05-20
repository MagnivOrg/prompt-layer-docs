import os
from typing import Any

from agents import Agent, ModelSettings, Runner, function_tool
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from openai import OpenAI
from openai.types.shared.reasoning import Reasoning
from promptlayer.integrations.openai_agents import instrument_openai_agents


DEFAULT_MODEL = "gpt-5"
EMBEDDING_MODEL = "text-embedding-3-small"

app = FastAPI(title="PromptLayer OpenAI Agents Example")
promptlayer_processor: Any = None
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


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise HTTPException(status_code=500, detail=f"Missing required environment variable: {name}")
    return value


def get_promptlayer_processor():
    global promptlayer_processor

    require_env("OPENAI_API_KEY")
    require_env("PROMPTLAYER_API_KEY")

    if promptlayer_processor is None:
        promptlayer_processor = instrument_openai_agents()

    return promptlayer_processor


@app.on_event("shutdown")
def shutdown_promptlayer_processor() -> None:
    if promptlayer_processor is not None:
        promptlayer_processor.force_flush()
        promptlayer_processor.shutdown()


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>PromptLayer OpenAI Agents Example</title>
    <style>
      body {
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        margin: 0;
        background: #f7f7f8;
        color: #19191c;
      }
      main {
        max-width: 760px;
        margin: 48px auto;
        padding: 0 20px;
      }
      h1 {
        font-size: 28px;
        margin: 0 0 8px;
      }
      p {
        color: #555760;
        line-height: 1.5;
      }
      form {
        display: grid;
        gap: 12px;
        margin-top: 24px;
      }
      textarea {
        min-height: 120px;
        resize: vertical;
        padding: 12px;
        border: 1px solid #c8cad0;
        border-radius: 8px;
        font: inherit;
      }
      button {
        width: fit-content;
        padding: 10px 14px;
        border: 0;
        border-radius: 8px;
        background: #19191c;
        color: white;
        font: inherit;
        cursor: pointer;
      }
      pre {
        white-space: pre-wrap;
        min-height: 80px;
        padding: 16px;
        background: white;
        border: 1px solid #dddfe5;
        border-radius: 8px;
      }
    </style>
  </head>
  <body>
    <main>
      <h1>PromptLayer OpenAI Agents Example</h1>
      <p>Run an OpenAI Agents SDK agent with PromptLayer tracing enabled.</p>
      <form id="agent-form">
        <textarea id="message">Use the embedding tool to embed exactly this text: PromptLayer OpenAI embedding trace probe. Then report the embedding dimensions and token count.</textarea>
        <button type="submit">Run agent</button>
      </form>
      <h2>Response</h2>
      <pre id="output">Waiting for a request...</pre>
    </main>
    <script>
      const form = document.querySelector("#agent-form");
      const message = document.querySelector("#message");
      const output = document.querySelector("#output");
      const submitButton = form.querySelector("button");

      form.addEventListener("submit", async (event) => {
        event.preventDefault();
        output.textContent = "Running agent...";
        submitButton.disabled = true;

        try {
          const response = await fetch("/api/agent", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message.value }),
          });
          const data = await response.json();

          if (!response.ok) {
            output.textContent = data.detail || "Request failed";
            return;
          }

          output.textContent = data.answer;
        } catch (error) {
          output.textContent = `Request failed: ${error.message}`;
        } finally {
          submitButton.disabled = false;
        }
      });
    </script>
  </body>
</html>
"""


@app.post("/api/agent")
async def run_agent(request: Request) -> dict[str, str]:
    body = await request.json()
    message = body.get("message", "Say hello in one sentence.")
    if not isinstance(message, str) or not message.strip():
        raise HTTPException(status_code=400, detail="message is required")

    processor = get_promptlayer_processor()
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
    except Exception as exc:
        processor.force_flush()
        raise HTTPException(status_code=500, detail=f"Agent request failed: {exc}") from exc
    finally:
        processor.force_flush()

    return {
        "model": model,
        "answer": str(result.final_output),
    }
