import { NodeSDK } from "@opentelemetry/sdk-node";
import { OTLPTraceExporter } from "@opentelemetry/exporter-trace-otlp-http";
import { resourceFromAttributes } from "@opentelemetry/resources";

const PROMPTLAYER_TRACE_URL = "https://api.promptlayer.com/v1/traces";
const serviceName = process.env.OTEL_SERVICE_NAME ?? "vercel-chat-app";

declare global {
  var __promptLayerOtelSdk: NodeSDK | undefined;
  var __promptLayerOtelStarted: boolean | undefined;
}

async function startPromptLayerTelemetry() {
  if (globalThis.__promptLayerOtelStarted) {
    return;
  }

  globalThis.__promptLayerOtelStarted = true;

  const apiKey = process.env.PROMPTLAYER_API_KEY;

  if (!apiKey) {
    console.warn(
      "PROMPTLAYER_API_KEY is not set; skipping PromptLayer OpenTelemetry export.",
    );
    return;
  }

  const sdk =
    globalThis.__promptLayerOtelSdk ??
    new NodeSDK({
      resource: resourceFromAttributes({
        "service.name": serviceName,
        "promptlayer.telemetry.source": "vercel-ai-sdk",
      }),
      traceExporter: new OTLPTraceExporter({
        url: PROMPTLAYER_TRACE_URL,
        headers: {
          "X-API-Key": apiKey,
        },
      }),
    });

  globalThis.__promptLayerOtelSdk = sdk;

  await sdk.start();

  process.on("SIGTERM", () => {
    void sdk.shutdown();
  });

  process.on("SIGINT", () => {
    void sdk.shutdown();
  });
}

void startPromptLayerTelemetry();
