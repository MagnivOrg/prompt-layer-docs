import {
  type AIMessage,
  HumanMessage,
  SystemMessage,
  ToolMessage,
  type ToolCall,
} from "@langchain/core/messages";
import { tool } from "@langchain/core/tools";
import { ChatAnthropic } from "@langchain/anthropic";
import { ChatOpenAI } from "@langchain/openai";
import { trace, type Span } from "@opentelemetry/api";

const SYSTEM_PROMPT =
  "You are a helpful travel assistant. Use lookup_destination_highlights before giving destination recommendations.";

const TOOL_NAME = "lookup_destination_highlights";
const WIKIVOYAGE_API_URL = "https://en.wikivoyage.org/w/api.php";

type ModelProvider = "anthropic" | "openai";
type DestinationLookupArgs = {
  destination: string;
  interests?: string[];
  trip_length_days?: number;
};

type WikivoyageSearchPage = {
  pageid: number;
  title: string;
  extract?: string;
  fullurl?: string;
};

type WikivoyageSearchResponse = {
  query?: {
    pages?: Record<string, WikivoyageSearchPage>;
  };
};

function compactText(value: string, maxLength: number): string {
  const compacted = value.replace(/\s+/g, " ").trim();
  return compacted.length > maxLength ? `${compacted.slice(0, maxLength - 1).trim()}...` : compacted;
}

function searchQuery(destination: string, interests: string[]): string {
  const interestText = interests.length > 0 ? ` ${interests.join(" ")}` : "";
  return `${destination}${interestText} travel`;
}

async function fetchWikivoyagePages(
  destination: string,
  interests: string[]
): Promise<WikivoyageSearchPage[]> {
  const params = new URLSearchParams({
    action: "query",
    format: "json",
    origin: "*",
    generator: "search",
    gsrsearch: searchQuery(destination, interests),
    gsrlimit: "3",
    prop: "extracts|info",
    exintro: "1",
    explaintext: "1",
    inprop: "url",
  });

  const response = await fetch(`${WIKIVOYAGE_API_URL}?${params}`, {
    signal: AbortSignal.timeout(5000),
  });
  if (!response.ok) {
    throw new Error(`Wikivoyage returned ${response.status}`);
  }

  const data = (await response.json()) as WikivoyageSearchResponse;
  return Object.values(data.query?.pages ?? {})
    .filter((page) => page.extract)
    .map((page) => ({
      ...page,
      extract: compactText(page.extract ?? "", 520),
    }));
}

function localTravelContext(destination: string, interests: string[], tripLengthDays: number) {
  const normalizedInterests = interests.length > 0 ? interests : ["food", "walkable neighborhoods", "local culture"];
  const beerFocused = normalizedInterests.some((interest) =>
    ["beer", "brewery", "breweries", "craft beer", "pubs"].some((term) =>
      interest.toLowerCase().includes(term)
    )
  );

  return {
    planning_notes: [
      `Plan ${destination} around compact neighborhood clusters instead of one-off sights.`,
      `For ${tripLengthDays} day${tripLengthDays === 1 ? "" : "s"}, keep each day to one anchor area plus one flexible evening plan.`,
      "Check opening days before locking the itinerary; small venues and museums often close early-week.",
    ],
    interest_angles: normalizedInterests.map((interest) => ({
      interest,
      angle: `${destination} works best when ${interest} stops are grouped near food, transit, or evening options.`,
    })),
    suggested_day_shape: [
      "Late morning: one anchor sight or neighborhood walk.",
      "Afternoon: food market, museum, waterfront, or park depending on weather.",
      beerFocused
        ? "Evening: two breweries or beer bars in the same district, with dinner between them."
        : "Evening: dinner near the final stop so transit back is simple.",
    ],
    cautions: [
      "Avoid over-planning cross-town hops.",
      "Keep a backup indoor stop for bad weather.",
      "Book destination restaurants, tours, and popular tasting rooms ahead when dates are fixed.",
    ],
  };
}

async function getDestinationHighlights({
  destination,
  interests = [],
  trip_length_days,
}: DestinationLookupArgs): Promise<string> {
  const normalizedDestination = destination.trim() || "the requested destination";
  const normalizedInterests = interests.map((interest) => interest.trim()).filter(Boolean);
  const tripLengthDays = Math.max(1, Math.min(14, Math.round(trip_length_days ?? 3)));
  let wikivoyagePages: WikivoyageSearchPage[] = [];
  let sourceStatus = "live Wikivoyage lookup succeeded";

  try {
    wikivoyagePages = await fetchWikivoyagePages(normalizedDestination, normalizedInterests);
  } catch (error) {
    sourceStatus = `live Wikivoyage lookup failed: ${error instanceof Error ? error.message : String(error)}`;
  }

  return JSON.stringify({
    destination: normalizedDestination,
    interests: normalizedInterests,
    trip_length_days: tripLengthDays,
    source_status: sourceStatus,
    external_sources: wikivoyagePages.map((page) => ({
      title: page.title,
      summary: page.extract,
      url: page.fullurl,
    })),
    local_context: localTravelContext(normalizedDestination, normalizedInterests, tripLengthDays),
  });
}

const lookupDestinationHighlights = tool(
  async (args: DestinationLookupArgs) =>
    getDestinationHighlights(args),
  {
    // The model sees this schema and decides the arguments for the tool call.
    name: TOOL_NAME,
    description:
      "Look up destination context, travel planning angles, and source-backed highlights before making itinerary recommendations.",
    schema: {
      type: "object",
      properties: {
        destination: {
          type: "string",
          description:
            "The destination city, region, country, or travel theme the user is asking about.",
        },
        interests: {
          type: "array",
          items: { type: "string" },
          description:
            "User interests to prioritize, such as beer, museums, food, hiking, nightlife, or budget travel.",
        },
        trip_length_days: {
          type: "number",
          description: "Approximate trip length in days when the user gives one.",
        },
      },
      required: ["destination"],
    },
  }
);

function stringifyMessageContent(content: AIMessage["content"]) {
  // Chat models can return plain text or structured content blocks; the UI only needs display text.
  return typeof content === "string"
    ? content
    : content
        .map((part) =>
          part.type === "text" && "text" in part ? part.text ?? "" : ""
        )
        .join("")
        .trim();
}

function stringifyToolMessageContent(content: ToolMessage["content"]): string {
  return typeof content === "string" ? content : JSON.stringify(content);
}

async function withSpan<T>(name: string, fn: (span: Span) => Promise<T>): Promise<T> {
  return trace.getTracer("langchain-itinerary-app").startActiveSpan(name, async (span) => {
    try {
      return await fn(span);
    } finally {
      span.end();
    }
  });
}

function selectedProvider(): ModelProvider {
  const provider = (process.env.LANGCHAIN_MODEL_PROVIDER ?? "openai").toLowerCase();
  if (provider === "openai" || provider === "anthropic") {
    return provider;
  }

  throw new Error("LANGCHAIN_MODEL_PROVIDER must be either 'openai' or 'anthropic'.");
}

function requiredEnv(name: string): string {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`Missing ${name}. Add it to .env or export it before starting the app.`);
  }
  return value;
}

function selectedModel(provider: ModelProvider): string {
  if (provider === "anthropic") {
    return process.env.ANTHROPIC_MODEL ?? "claude-sonnet-4-6";
  }

  return process.env.OPENAI_MODEL ?? "gpt-4o-mini";
}

function anthropicThinkingEffort(): string | undefined {
  return process.env.ANTHROPIC_THINKING?.trim() || undefined;
}

function createAnthropicChatModel(model: string) {
  const thinking = anthropicThinkingEffort();
  // @ts-expect-error Keep env values as provider pass-through; LangChain/Anthropic validates them.
  return new ChatAnthropic({
    apiKey: requiredEnv("ANTHROPIC_API_KEY"),
    model,
    ...(thinking
      ? {
          thinking: { type: "adaptive", display: "summarized" },
          outputConfig: {
            effort: thinking,
          },
        }
      : {}),
  });
}

function createOpenAIChatModel(model: string) {
  return new ChatOpenAI({
    apiKey: requiredEnv("OPENAI_API_KEY"),
    model,
  });
}

export async function runItineraryPrompt(input: string): Promise<string> {
  const provider = selectedProvider();
  const model = selectedModel(provider);

  let llm: ChatAnthropic | ChatOpenAI;
  let llmWithTools:
    | ReturnType<ChatAnthropic["bindTools"]>
    | ReturnType<ChatOpenAI["bindTools"]>;

  if (provider === "anthropic") {
    llm = createAnthropicChatModel(model);
    llmWithTools = llm.bindTools([lookupDestinationHighlights]);
  } else {
    llm = createOpenAIChatModel(model);
    llmWithTools = llm.bindTools([lookupDestinationHighlights], {
      // Force the first turn to produce a tool call so the demo always exercises tool tracing.
      tool_choice: {
        type: "function",
        function: { name: TOOL_NAME },
      },
    });
  }

  const messages = [new SystemMessage(SYSTEM_PROMPT), new HumanMessage(input)];

  // First LLM call: ask the model to select and populate the destination lookup tool.
  const toolCallResult = await withSpan("itinerary.llm.tool_selection", () =>
    llmWithTools.invoke(messages)
  );
  const toolCalls = toolCallResult.tool_calls ?? [];

  if (toolCalls.length === 0) {
    return stringifyMessageContent(toolCallResult.content);
  }

  const toolMessages = await Promise.all(
    toolCalls.map(async (toolCall) => {
      const toolResult = await withSpan("itinerary.tool.lookup_destination_highlights", () =>
        (
          lookupDestinationHighlights as unknown as {
            invoke(call: ToolCall): Promise<string | ToolMessage>;
          }
        ).invoke(toolCall)
      );

      return ToolMessage.isInstance(toolResult)
        ? toolResult
        : new ToolMessage({
            content: stringifyToolMessageContent(toolResult),
            tool_call_id: toolCall.id ?? "",
            name: toolCall.name,
          });
    })
  );

  const followupMessages = [
    ...messages,
    toolCallResult,
    ...toolMessages,
    new HumanMessage("Use the tool result to answer the original request concisely."),
  ];

  // Second LLM call: feed the tool response back to the model and record the final user-facing answer.
  const result = await withSpan("itinerary.llm.followup", () =>
    llm.invoke(followupMessages)
  );

  return stringifyMessageContent(result.content);
}
