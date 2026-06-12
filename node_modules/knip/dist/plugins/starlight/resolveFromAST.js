import { findCallArg, getDefaultImportName, getImportMap, getPropertyValues } from '../../typescript/ast-helpers.js';
export const getComponentPathsFromSourceFile = (program) => {
    const importMap = getImportMap(program);
    const starlightImportName = getDefaultImportName(importMap, '@astrojs/starlight');
    if (!starlightImportName)
        return new Set();
    const arg = findCallArg(program, starlightImportName);
    return arg ? getPropertyValues(arg, 'components') : new Set();
};
