import { toProductionEntry } from '../../util/input.js';
import { hasDependency } from '../../util/plugin.js';
import { getEntryFromAST } from './resolveFromAST.js';
const title = 'tsup';
const enablers = ['tsup'];
const isEnabled = ({ dependencies }) => hasDependency(dependencies, enablers);
const config = ['tsup.config.{js,ts,cjs,mjs,json}', 'package.json'];
const isLoadConfig = ({ configFileName }) => configFileName === 'package.json' || configFileName.endsWith('.json');
const resolveConfig = async (config) => {
    if (typeof config === 'function')
        config = await config({});
    const entryPatterns = [config]
        .flat()
        .flatMap(config => {
        if (!config.entry)
            return [];
        if (Array.isArray(config.entry))
            return config.entry;
        return Object.values(config.entry);
    })
        .map(id => toProductionEntry(id, { allowIncludeExports: true }));
    return entryPatterns;
};
const resolveFromAST = program => {
    const entries = getEntryFromAST(program);
    return [...entries].map(id => toProductionEntry(id, { allowIncludeExports: true }));
};
const args = {
    config: true,
};
const plugin = {
    title,
    enablers,
    isEnabled,
    config,
    isLoadConfig,
    resolveConfig,
    resolveFromAST,
    args,
};
export default plugin;
