import { getStringValue } from '../../typescript/ast-nodes.js';
import { collectPropertyValues, findProperty, getPropertyKey, hasImportSpecifier, resolveObjectArg, } from '../../typescript/ast-helpers.js';
export const getSrcDir = (program) => {
    const values = collectPropertyValues(program, 'srcDir');
    return values.size > 0 ? Array.from(values)[0] : 'src';
};
export const usesPassthroughImageService = (program) => hasImportSpecifier(program, 'astro/config', 'passthroughImageService');
const findFirstStringArg = (node) => {
    const literal = getStringValue(node);
    if (literal)
        return literal;
    if (node?.type === 'CallExpression' || node?.type === 'NewExpression') {
        for (const arg of node.arguments ?? []) {
            const found = findFirstStringArg(arg);
            if (found)
                return found;
        }
    }
};
export const getViteAliases = (program) => {
    const aliases = {};
    for (const node of program.body ?? []) {
        if (node.type !== 'ExportDefaultDeclaration')
            continue;
        const decl = node.declaration;
        const root = decl?.type === 'CallExpression' ? resolveObjectArg(decl.arguments?.[0]) : resolveObjectArg(decl);
        const aliasNode = findProperty(findProperty(findProperty(root, 'vite'), 'resolve'), 'alias');
        if (aliasNode?.type !== 'ObjectExpression')
            continue;
        for (const prop of aliasNode.properties ?? []) {
            if (prop.type !== 'Property')
                continue;
            const key = getPropertyKey(prop);
            if (!key)
                continue;
            const raw = findFirstStringArg(prop.value);
            if (raw)
                aliases[key] = raw;
        }
    }
    return aliases;
};
