import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import type { NextConfig } from "next";

const appDir = dirname(fileURLToPath(import.meta.url));

const nextConfig: NextConfig = {
  // The engine is a workspace package consumed as source; let Next transpile it.
  transpilePackages: ["@mythos/core"],
  turbopack: {
    root: join(appDir, "../.."),
  },
};

export default nextConfig;
