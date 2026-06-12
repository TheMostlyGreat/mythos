import { toDependency, toProductionEntry } from '../../util/input.js';
import { isInternal, join } from '../../util/path.js';
import { hasDependency } from '../../util/plugin.js';
const title = 'Serverless Framework';
const enablers = ['serverless'];
const isEnabled = ({ dependencies }) => hasDependency(dependencies, enablers);
const config = ['serverless.{js,cjs,mjs,ts,cts,mts,yml,yaml}'];
const handlerToEntry = (handler) => {
    const dot = handler.lastIndexOf('.');
    return toProductionEntry(`${handler.slice(0, dot)}.{js,ts}`);
};
const pluginToInput = (plugin, dir) => isInternal(plugin) ? toProductionEntry(join(dir, plugin)) : toDependency(plugin);
const resolveConfig = async (config, options) => {
    const functions = config.functions
        ? Object.values(config.functions).flatMap(fn => (fn.handler ? [handlerToEntry(fn.handler)] : []))
        : [];
    const plugins = config.plugins?.filter((plugin) => typeof plugin === 'string') ?? [];
    const esbuild = config.custom?.esbuild || config.build?.esbuild ? [toDependency('esbuild', { optional: true })] : [];
    return [...functions, ...plugins.map(plugin => pluginToInput(plugin, options.configFileDir)), ...esbuild];
};
const plugin = {
    title,
    enablers,
    isEnabled,
    config,
    resolveConfig,
};
export default plugin;
