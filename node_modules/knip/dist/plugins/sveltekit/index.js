import { toAlias, toIgnore, toProductionEntry } from '../../util/input.js';
import { hasDependency } from '../../util/plugin.js';
import { collectPropertyValues } from '../../typescript/ast-helpers.js';
const title = 'SvelteKit';
const enablers = ['@sveltejs/kit'];
const isEnabled = ({ dependencies }) => hasDependency(dependencies, enablers);
const config = ['svelte.config.js'];
const production = [
    'src/routes/**/+{page,server,page.server,error,layout,layout.server}{,@*}.{js,ts,svelte}',
    'src/hooks.{server,client}.{js,ts}',
    'src/params/*.{js,ts}',
    'src/service-worker.{js,ts}',
    'src/service-worker/index.{js,ts}',
    'src/instrumentation.server.{js,ts}',
];
const getLibPath = (program) => {
    const values = collectPropertyValues(program, 'lib');
    return values.size > 0 ? Array.from(values)[0] : 'src/lib';
};
const resolveFromAST = program => {
    const lib = getLibPath(program);
    return [
        ...production.map(pattern => toProductionEntry(pattern)),
        toAlias('$lib', [`./${lib}`]),
        toAlias('$lib/*', [`./${lib}/*`]),
        toIgnore('\\$app/.+', 'unresolved'),
        toIgnore('\\$env/.+', 'unresolved'),
        toIgnore('\\$service-worker', 'unresolved'),
    ];
};
const plugin = {
    title,
    enablers,
    isEnabled,
    config,
    resolveFromAST,
};
export default plugin;
