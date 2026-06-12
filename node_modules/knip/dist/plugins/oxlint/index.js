import { toDependency, toEntry } from '../../util/input.js';
import { isInternal } from '../../util/path.js';
import { hasDependency } from '../../util/plugin.js';
const title = 'Oxlint';
const enablers = ['oxlint'];
const isEnabled = ({ dependencies }) => hasDependency(dependencies, enablers);
const config = ['.oxlintrc.json', 'oxlint.config.ts'];
const args = {
    config: true,
};
const resolveJsPlugins = (jsPlugins) => {
    const inputs = [];
    for (const plugin of jsPlugins ?? []) {
        const specifier = typeof plugin === 'string' ? plugin : plugin.specifier;
        if (!isInternal(specifier))
            inputs.push(toDependency(specifier));
        else
            inputs.push(toEntry(specifier));
    }
    return inputs;
};
const resolveConfig = config => {
    const inputs = resolveJsPlugins(config.jsPlugins);
    for (const override of config.overrides ?? []) {
        for (const input of resolveJsPlugins(override.jsPlugins))
            inputs.push(input);
    }
    return inputs;
};
const plugin = {
    title,
    enablers,
    isEnabled,
    config,
    resolveConfig,
    args,
};
export default plugin;
