import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { Visitor } from 'oxc-parser';
import { scriptBodies } from '../../compilers/compilers.js';
import { _parseFile } from '../../typescript/ast-nodes.js';
import { basename, dirname, isInNodeModules, join } from '../../util/path.js';
export const getVueSfc = (cwd) => {
    try {
        return createRequire(join(cwd, 'package.json'))('vue/compiler-sfc');
    }
    catch { }
    return {
        parse: (source, path) => ({
            descriptor: { script: { content: scriptBodies(source, path) }, scriptSetup: null, template: { content: '' } },
        }),
    };
};
const readFile = (filePath) => {
    try {
        return readFileSync(filePath, 'utf8');
    }
    catch {
        return '';
    }
};
export const readAndParseFile = (filePath) => _parseFile(filePath, readFile(filePath));
export const collectIdentifiers = (source, fileName) => {
    const identifiers = new Set();
    const visitor = new Visitor({
        Identifier(node) {
            identifiers.add(node.name);
        },
    });
    visitor.visit(_parseFile(fileName, source).program);
    return identifiers;
};
export const collectTemplateInfo = (tree) => {
    const tags = new Set();
    const identifiers = new Set();
    const addExprIdentifiers = (expr) => {
        for (const id of collectIdentifiers(expr, 'expr.ts'))
            identifiers.add(id);
    };
    const visit = (node) => {
        if (node.tag)
            tags.add(node.tag);
        if (node.type === 5 && node.content && !node.content.isStatic)
            addExprIdentifiers(node.content.content);
        if (node.props) {
            for (const prop of node.props) {
                if (prop.type === 7) {
                    if (prop.exp && !prop.exp.isStatic)
                        addExprIdentifiers(prop.exp.content);
                    if (prop.arg && !prop.arg.isStatic)
                        addExprIdentifiers(prop.arg.content);
                }
            }
        }
        if (node.children)
            for (const child of node.children)
                visit(child);
    };
    visit(tree);
    return { tags, identifiers };
};
export const toKebabCase = (s) => s.replace(/[A-Z]/g, (m, i) => (i ? '-' : '') + m.toLowerCase());
const isLocalSpecifier = (specifier) => specifier.startsWith('.') && !isInNodeModules(specifier);
export const collectLocalImportPaths = (filePath, result) => {
    const dir = dirname(filePath);
    const paths = new Set();
    const visitor = new Visitor({
        TSImportType(node) {
            const specifier = node.source.value;
            if (isLocalSpecifier(specifier))
                paths.add(join(dir, specifier));
        },
    });
    visitor.visit(result.program);
    return paths;
};
export function buildAutoImportMap(filePath, result) {
    const dir = dirname(filePath);
    const isComponents = basename(filePath) === 'components.d.ts';
    const importMap = new Map();
    const componentMap = new Map();
    const importTypes = [];
    const collectVisitor = new Visitor({
        TSImportType(node) {
            importTypes.push({ start: node.start, end: node.end, specifier: node.source.value });
        },
    });
    collectVisitor.visit(result.program);
    const matchVisitor = new Visitor({
        VariableDeclarator(node) {
            if (node.id?.type !== 'Identifier')
                return;
            const name = node.id.name;
            if (name.startsWith('Lazy'))
                return;
            const importType = importTypes.find(it => it.start >= node.start && it.end <= node.end);
            if (!importType)
                return;
            if (!isLocalSpecifier(importType.specifier))
                return;
            const absSpecifier = join(dir, importType.specifier);
            if (isComponents) {
                const components = componentMap.get(name);
                if (components)
                    components.push(absSpecifier);
                else
                    componentMap.set(name, [absSpecifier]);
            }
            else {
                importMap.set(name, absSpecifier);
            }
        },
        ExportNamedDeclaration(node) {
            if (!node.source)
                return;
            const specifier = node.source.value;
            if (!isLocalSpecifier(specifier))
                return;
            const absSpecifier = join(dir, specifier);
            for (const s of node.specifiers) {
                const name = s.exported.type === 'Identifier' ? s.exported.name : s.exported.value;
                if (name)
                    importMap.set(name, absSpecifier);
            }
        },
    });
    matchVisitor.visit(result.program);
    return { importMap, componentMap };
}
