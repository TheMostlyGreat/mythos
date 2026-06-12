import { hasDependency } from '../../util/plugin.js';
import { getInputsFromHandlers } from './resolveFromAST.js';
const title = 'SST';
const enablers = ['sst'];
const isEnabled = ({ dependencies }) => hasDependency(dependencies, enablers);
const config = ['sst.config.ts'];
const resolveFromAST = (program, options) => {
    const inputs = getInputsFromHandlers(program, options);
    return inputs;
};
const plugin = {
    title,
    enablers,
    isEnabled,
    config,
    resolveFromAST,
};
export default plugin;
