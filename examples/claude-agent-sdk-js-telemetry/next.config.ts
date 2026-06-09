import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Keep the app straightforward while testing SDK behavior locally.
  reactStrictMode: true,
  // These SDKs are Node-only here. Externalizing them prevents Next from trying
  // to bundle PromptLayer's optional provider integrations into the app route.
  serverExternalPackages: ["promptlayer", "@anthropic-ai/claude-agent-sdk"]
};

export default nextConfig;
