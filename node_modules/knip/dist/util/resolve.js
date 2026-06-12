import { ResolverFactory } from 'oxc-resolver';
import { DEFAULT_EXTENSIONS, DTS_EXTENSIONS } from '../constants.js';
import { timerify } from './Performance.js';
import { toPosix } from './path.js';
const extensionAlias = {
    '.js': ['.js', '.ts', '.tsx', '.d.ts'],
    '.jsx': ['.jsx', '.tsx'],
    '.mjs': ['.mjs', '.mts', '.d.mts'],
    '.cjs': ['.cjs', '.cts', '.d.cts'],
};
const resolverInstances = [];
const createSyncModuleResolver = (extensions, alias) => {
    const aliasOpt = alias && { alias };
    const baseOptions = {
        extensions,
        extensionAlias,
        conditionNames: ['require', 'import', 'node', 'default'],
        nodePath: false,
        ...aliasOpt,
    };
    const resolver = new ResolverFactory({ tsconfig: 'auto', ...baseOptions });
    const fallbackResolver = new ResolverFactory(baseOptions);
    resolverInstances.push(resolver, fallbackResolver);
    return function resolveSync(specifier, basePath) {
        const resolved = resolver.resolveFileSync(basePath, specifier);
        if (resolved.path)
            return toPosix(resolved.path);
        if (resolved.error) {
            const fallback = fallbackResolver.resolveFileSync(basePath, specifier);
            if (fallback.path)
                return toPosix(fallback.path);
        }
    };
};
const resolveModuleSync = createSyncModuleResolver([...DEFAULT_EXTENSIONS, ...DTS_EXTENSIONS, '.json', '.jsonc']);
export const _resolveModuleSync = timerify(resolveModuleSync, 'resolveModuleSync');
export const _createSyncModuleResolver = (extensions) => timerify(createSyncModuleResolver(extensions), 'resolveModuleSync');
const createSyncResolver = (extensions) => {
    const resolver = new ResolverFactory({
        extensions,
        conditionNames: ['require', 'import', 'node', 'default'],
        nodePath: false,
    });
    resolverInstances.push(resolver);
    return function resolveSync(specifier, baseDir) {
        const resolved = resolver.sync(baseDir, specifier);
        if (resolved.path)
            return toPosix(resolved.path);
    };
};
export function clearResolverCache() {
    for (const resolver of resolverInstances)
        resolver.clearCache();
}
const resolveSync = createSyncResolver([...DEFAULT_EXTENSIONS, '.json', '.jsonc']);
export const _resolveSync = timerify(resolveSync);
