import { Linter, Rule } from "eslint";

//#region src/cjs-config-builder.d.ts
type CJSConfigs = {
  base: Linter.LegacyConfig;
  recommended: Linter.LegacyConfig;
  all: Linter.LegacyConfig;
  "jsx-a11y-strict": Linter.LegacyConfig;
  "jsx-a11y-recommended": Linter.LegacyConfig;
  "flat/base": Linter.Config[];
  "flat/recommended": Linter.Config[];
  "flat/all": Linter.Config[];
  "flat/jsx-a11y-strict": Linter.Config[];
  "flat/jsx-a11y-recommended": Linter.Config[];
};
//#endregion
//#region src/plugin.d.ts
type AstroPlugin = {
  meta: {
    name: string;
    version: string;
  };
  environments: {
    astro: {
      globals: {
        Astro: boolean;
        Fragment: boolean;
      };
    };
  };
  rules: {
    [key: string]: Rule.RuleModule;
  };
  processors: {
    ".astro": Linter.Processor;
    astro: Linter.Processor;
    "client-side-ts": Linter.Processor;
  };
};
//#endregion
//#region src/index.d.cts
declare const _default: AstroPlugin & {
  configs: CJSConfigs;
};
export = _default;