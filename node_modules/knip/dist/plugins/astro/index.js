import { toDependency, toEntry, toProductionEntry } from '../../util/input.js';
import { hasDependency } from '../../util/plugin.js';
import { getAliasInputs } from '../vitest/helpers.js';
import compiler from './compiler.js';
import mdxCompiler from './compiler-mdx.js';
import { getSrcDir, getViteAliases, usesPassthroughImageService } from './resolveFromAST.js';
const title = 'Astro';
const enablers = ['astro'];
const isEnabled = ({ dependencies }) => hasDependency(dependencies, enablers);
export const config = ['astro.config.{js,cjs,mjs,ts,mts}'];
const entry = ['src/content/config.ts', 'src/content.config.ts'];
const production = [
    'src/pages/**/*.{astro,mdx,js,ts}',
    '!src/pages/**/_*',
    '!src/pages/**/_*/**',
    'src/content/**/*.mdx',
    'src/middleware.{js,ts}',
    'src/middleware/index.{js,ts}',
    'src/actions/index.{js,ts}',
];
const resolveFromAST = (program, options) => {
    const srcDir = getSrcDir(program);
    const setSrcDir = (entry) => entry.replace(/^src\//, `${srcDir}/`);
    const inputs = [
        ...entry.map(setSrcDir).map(path => toEntry(path)),
        ...production.map(setSrcDir).map(path => toProductionEntry(path)),
        ...getAliasInputs(getViteAliases(program), options.cwd),
    ];
    if (!usesPassthroughImageService(program))
        inputs.push(toDependency('sharp', { optional: true }));
    return inputs;
};
const registerCompilers = ({ registerCompiler, hasDependency }) => {
    if (hasDependency('astro'))
        registerCompiler({ extension: '.astro', compiler });
    if (hasDependency('@astrojs/mdx') || hasDependency('@astrojs/starlight')) {
        registerCompiler({ extension: '.mdx', compiler: mdxCompiler });
    }
};
const resolve = options => {
    const { manifest, isProduction } = options;
    const inputs = [];
    if (!isProduction &&
        manifest.scripts &&
        Object.values(manifest.scripts).some(script => /(?<=^|\s)astro(\s|\s.+\s)check(?=\s|$)/.test(script))) {
        inputs.push(toDependency('@astrojs/check'));
    }
    return inputs;
};
const plugin = {
    title,
    enablers,
    isEnabled,
    config,
    entry,
    production,
    registerCompilers,
    resolveFromAST,
    resolve,
};
export default plugin;
