import { Linter, Rule } from "eslint";

//#region src/esm-config-builder.d.ts
type ESMConfigs = {
  base: Linter.Config[];
  recommended: Linter.Config[];
  all: Linter.Config[];
  "jsx-a11y-strict": Linter.Config[];
  "jsx-a11y-recommended": Linter.Config[];
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
//#region src/index.d.mts
declare const configs: ESMConfigs;
declare const _default: AstroPlugin & {
  configs: ESMConfigs;
};
declare const meta: AstroPlugin["meta"];
declare const rules: AstroPlugin["rules"];
declare const processors: AstroPlugin["processors"];
declare const environments: AstroPlugin["environments"];
//#endregion
export { configs, _default as default, environments, meta, processors, rules };