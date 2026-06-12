import { Visitor } from 'oxc-parser';
import { blockCommentMatcher, lineCommentMatcher, scriptExtractor } from '../../compilers/compilers.js';
import { findProperty, getImportMap, getStringValues } from '../../typescript/ast-helpers.js';
import { isFile, loadFile } from '../../util/fs.js';
import { toProductionEntry } from '../../util/input.js';
import { join } from '../../util/path.js';
import { getDependenciesFromConfig } from '../babel/index.js';
const babelPluginSources = ['@rolldown/plugin-babel', '@vitejs/plugin-react', 'vite-plugin-babel'];
const isBabelWrappingPlugin = (path) => babelPluginSources.some(source => path === source || path.startsWith(`${source}/`));
export const getBabelInputs = (program) => {
    const pluginNames = new Set();
    for (const [name, path] of getImportMap(program)) {
        if (isBabelWrappingPlugin(path))
            pluginNames.add(name);
    }
    if (pluginNames.size === 0)
        return [];
    const inputs = [];
    const visitor = new Visitor({
        CallExpression(node) {
            if (node.callee?.type !== 'Identifier' || !pluginNames.has(node.callee.name))
                return;
            const options = node.arguments?.[0];
            const plugins = [];
            const presets = [];
            for (const config of [options, findProperty(options, 'babel'), findProperty(options, 'babelConfig')]) {
                plugins.push(...getStringValues(findProperty(config, 'plugins')));
                presets.push(...getStringValues(findProperty(config, 'presets')));
            }
            inputs.push(...getDependenciesFromConfig({ plugins, presets }));
        },
    });
    visitor.visit(program);
    return inputs;
};
const moduleTypePattern = /\btype\s*=\s*["']?module["']?/i;
const srcAttrPattern = /\bsrc\s*=\s*["']([^"']+)["']/i;
const importSpecPattern = /\bimport\b(?:\s*\(\s*|(?:[\w$*,{}\s]*\bfrom\b)?\s*)(['"])([^'"]+)\1/g;
const isFilePath = (specifier) => specifier.startsWith('/') || specifier.startsWith('./') || specifier.startsWith('../');
const normalizeModuleScriptSrc = (value) => value.trim().replace(/^\//, '');
const getModuleScriptSources = (html) => {
    const sources = [];
    for (const [, attrs, body] of html.matchAll(scriptExtractor)) {
        if (!moduleTypePattern.test(attrs))
            continue;
        const srcMatch = attrs.match(srcAttrPattern);
        if (srcMatch) {
            const src = normalizeModuleScriptSrc(srcMatch[1]);
            if (src)
                sources.push(src);
            continue;
        }
        if (body) {
            const code = body.replace(blockCommentMatcher, '').replace(lineCommentMatcher, '');
            for (const importMatch of code.matchAll(importSpecPattern)) {
                const specifier = importMatch[2];
                if (isFilePath(specifier))
                    sources.push(normalizeModuleScriptSrc(specifier));
            }
        }
    }
    return sources;
};
export const getIndexHtmlEntries = async (rootDir) => {
    const indexPath = join(rootDir, 'index.html');
    if (!isFile(indexPath))
        return [];
    const html = await loadFile(indexPath);
    const entries = getModuleScriptSources(html).map(src => join(rootDir, src));
    return entries.map(entry => toProductionEntry(entry));
};
