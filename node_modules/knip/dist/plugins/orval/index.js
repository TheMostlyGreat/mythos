import { toEntry } from '../../util/input.js';
import { hasDependency } from '../../util/plugin.js';
import { getInputsFromAST } from './resolveFromAST.js';
const title = 'orval';
const enablers = ['orval'];
const isEnabled = ({ dependencies }) => hasDependency(dependencies, enablers);
const config = ['orval.config.{js,mjs,ts,mts}'];
const resolveFromAST = program => [...getInputsFromAST(program)].map(id => toEntry(id));
const plugin = {
    title,
    enablers,
    isEnabled,
    config,
    resolveFromAST,
};
export default plugin;
