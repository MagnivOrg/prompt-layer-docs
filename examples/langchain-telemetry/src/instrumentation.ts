import { context, trace } from "@opentelemetry/api";
import { AsyncLocalStorageContextManager } from "@opentelemetry/context-async-hooks";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-proto";
import { BasicTracerProvider, BatchSpanProcessor } from "@opentelemetry/sdk-trace-base";
import { initializeOTEL } from "langsmith/experimental/otel/setup";

export async function register() {
  if (process.env.NEXT_RUNTIME === "edge") {
    return;
  }

  // Next.js calls this once per server runtime; skip tracing entirely unless an OTLP sink is configured.
  if (!process.env.OTEL_EXPORTER_OTLP_ENDPOINT) {
    return;
  }

  // Dev reloads can evaluate this module more than once, but OTEL globals can only be set once.
  if ((globalThis as { __otelInitialized?: boolean }).__otelInitialized) {
    return;
  }

  // PromptLayer accepts the API key as an OTLP header; normalize the env var into the exporter shape.
  const promptLayerApiKey = process.env.OTEL_EXPORTER_OTLP_HEADERS
    ?.replace("X-API-KEY=", "")
    .trim();
  const headers: Record<string, string> | undefined = promptLayerApiKey
    ? { "X-API-KEY": promptLayerApiKey }
    : undefined;

  const exporter = new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT,
    headers,
  });
  const provider = new BasicTracerProvider({
    spanProcessors: [new BatchSpanProcessor(exporter)],
  });
  const contextManager = new AsyncLocalStorageContextManager();
  contextManager.enable();
  // The context manager keeps manually-created spans parented to the LangChain request flow.
  context.setGlobalContextManager(contextManager);
  trace.setGlobalTracerProvider(provider);
  // LangSmith's OTEL bridge translates LangChain callback runs into OTEL spans on this provider.
  initializeOTEL({
    globalTracerProvider: provider,
    globalContextManager: contextManager,
    skipGlobalContextManagerSetup: true,
  });
  (globalThis as { __otelInitialized?: boolean }).__otelInitialized = true;
}
