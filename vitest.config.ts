import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    // BDD scenarios and unit tests live alongside the engine in packages/core.
    include: [
      "packages/*/src/**/*.{test,spec}.ts",
      "packages/*/tests/**/*.{test,spec}.ts",
    ],
  },
});
