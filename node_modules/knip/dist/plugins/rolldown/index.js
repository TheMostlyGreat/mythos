import { toProductionEntry } from '../../util/input.js';
import { hasDependency } from '../../util/plugin.js';
import { getInputFromAST } from './resolveFromAST.js';
const title = 'Rolldown';
const enablers = ['rolldown'];
const isEnabled = ({ dependencies }) => hasDependency(dependencies, enablers);
const config = ['rolldown.config.{js,cjs,mjs,ts,cts,mts}'];
const resolveFromAST = program => {
    const inputs = getInputFromAST(program);
    return [...inputs].map(id => toProductionEntry(id));
};
const plugin = {
    title,
    enablers,
    isEnabled,
    config,
    resolveFromAST,
};
export default plugin;
