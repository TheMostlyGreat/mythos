import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from '../util/path.js';
import { _require } from '../util/require.js';
const monorepoRootCache = new Map();
const findMonorepoRootAbove = (startDir) => {
    if (monorepoRootCache.has(startDir))
        return monorepoRootCache.get(startDir);
    let current = dirname(startDir);
    let result;
    while (current !== dirname(current)) {
        if (existsSync(join(current, 'pnpm-workspace.yaml'))) {
            result = current;
            break;
        }
        try {
            const pkg = JSON.parse(readFileSync(join(current, 'package.json'), 'utf8'));
            if (pkg.workspaces) {
                result = current;
                break;
            }
        }
        catch { }
        current = dirname(current);
    }
    monorepoRootCache.set(startDir, result);
    return result;
};
export const loadPackageManifest = ({ dir, packageName, cwd }) => {
    try {
        return _require(join(dir, 'node_modules', packageName, 'package.json'));
    }
    catch { }
    if (dir !== cwd) {
        try {
            return _require(join(cwd, 'node_modules', packageName, 'package.json'));
        }
        catch { }
        return;
    }
    const root = findMonorepoRootAbove(cwd);
    if (root) {
        try {
            return _require(join(root, 'node_modules', packageName, 'package.json'));
        }
        catch { }
    }
};
export const getFilteredScripts = (scripts) => {
    if (!scripts)
        return [{}, {}];
    const productionScripts = {};
    const developmentScripts = {};
    for (const scriptName in scripts) {
        if (!/^\w/.test(scriptName))
            continue;
        if (scriptName === 'start')
            productionScripts[scriptName] = scripts[scriptName];
        else
            developmentScripts[scriptName] = scripts[scriptName];
    }
    return [productionScripts, developmentScripts];
};
