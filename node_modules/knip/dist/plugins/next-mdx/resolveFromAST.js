import { Visitor } from 'oxc-parser';
import { findProperty, getDefaultImportName, getImportMap, getStringValues } from '../../typescript/ast-helpers.js';
export const getMdxPlugins = (program) => {
    const plugins = new Set();
    const importMap = getImportMap(program);
    const mdxImportName = getDefaultImportName(importMap, '@next/mdx');
    if (!mdxImportName)
        return plugins;
    const visitor = new Visitor({
        CallExpression(node) {
            if (node.callee?.type !== 'Identifier' || node.callee.name !== mdxImportName)
                return;
            const options = findProperty(node.arguments?.[0], 'options');
            if (options?.type !== 'ObjectExpression')
                return;
            for (const pluginType of ['remarkPlugins', 'rehypePlugins', 'recmaPlugins']) {
                for (const v of getStringValues(findProperty(options, pluginType)))
                    plugins.add(v);
            }
        },
    });
    visitor.visit(program);
    return plugins;
};
