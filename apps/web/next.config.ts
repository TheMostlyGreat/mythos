import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // The engine is a workspace package consumed as source; let Next transpile it.
  transpilePackages: ["@mythos/core"],
};

export default nextConfig;
