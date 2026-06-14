import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    // BDD scenarios and unit tests live alongside the engine in packages/core.
    environment: "jsdom",
    include: [
      "packages/*/src/**/*.{test,spec}.ts",
      "packages/*/tests/**/*.{test,spec}.ts",
      "apps/*/tests/**/*.{test,spec}.{ts,tsx}",
    ],
  },
});
