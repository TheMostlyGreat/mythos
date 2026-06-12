import { hasDependency } from '../../util/plugin.js';
import compiler from './compiler.js';
const title = 'Tailwind';
const enablers = ['tailwindcss', '@tailwindcss/vite', '@tailwindcss/postcss', '@tailwindcss/cli'];
const isEnabled = ({ dependencies }) => hasDependency(dependencies, enablers);
const entry = ['tailwind.config.{js,cjs,mjs,ts,cts,mts}'];
const registerCompilers = ({ registerCompiler, hasDependency }) => {
    if (enablers.some(enabler => hasDependency(enabler)))
        registerCompiler({ extension: '.css', compiler });
};
const plugin = {
    title,
    enablers,
    isEnabled,
    entry,
    registerCompilers,
};
export default plugin;
