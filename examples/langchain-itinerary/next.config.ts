import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  logging: {
    // Keep local logs readable while inspecting OTEL spans for each API request.
    serverFunctions: false,
  },
};

export default nextConfig;
