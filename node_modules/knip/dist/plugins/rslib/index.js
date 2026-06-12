import { toProductionEntry } from '../../util/input.js';
import { hasDependency } from '../../util/plugin.js';
import { getEntryFromAST } from './resolveFromAST.js';
const title = 'Rslib';
const enablers = ['@rslib/core'];
const isEnabled = ({ dependencies }) => hasDependency(dependencies, enablers);
const config = ['rslib*.config.{mjs,ts,js,cjs,mts,cts}'];
const resolveFromAST = program => {
    const entries = getEntryFromAST(program);
    return [...entries].map(id => toProductionEntry(id, { allowIncludeExports: true }));
};
const plugin = {
    title,
    enablers,
    isEnabled,
    config,
    resolveFromAST,
};
export default plugin;
