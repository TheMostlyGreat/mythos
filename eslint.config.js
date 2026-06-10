import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default tseslint.config(
  {
    ignores: [
      "**/dist/**",
      "**/.next/**",
      "**/node_modules/**",
      // Python prototype + generated artifacts — not part of the TS rebuild.
      "venv/**",
      "mythos/**",
      "tests/**",
      "stories/**",
      "templates/**",
      ".safeword/**",
    ],
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
);
