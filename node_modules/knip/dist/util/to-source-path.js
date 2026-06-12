import { DEFAULT_EXTENSIONS } from '../constants.js';
import { debugLog, debugLogArray } from './debug.js';
import { findFileWithExtensions, isDirectory } from './fs.js';
import { _glob, prependDirToPattern } from './glob.js';
import { isAbsolute, isInternal, join, toRelative } from './path.js';
const defaultExtensions = `.{${[...DEFAULT_EXTENSIONS].map(ext => ext.slice(1)).join(',')}}`;
const hasTSExt = /(?<!\.d)\.(m|c)?tsx?$/;
const matchExt = /(\.d)?\.(m|c)?(j|t)s$/;
const sourceExtensions = [...DEFAULT_EXTENSIONS];
const tsconfigSourceMap = (dir, compilerOptions) => {
    const srcDir = join(dir, 'src');
    const outDirHasSrc = compilerOptions.outDir && isDirectory(compilerOptions.outDir, 'src');
    const resolvedSrc = compilerOptions.rootDir ?? (outDirHasSrc ? dir : isDirectory(srcDir) ? srcDir : dir);
    return { srcDir: resolvedSrc, outDir: compilerOptions.outDir || resolvedSrc };
};
export const augmentWorkspace = (workspace, dir, compilerOptions, pluginSourceMaps = []) => {
    const all = compilerOptions ? [...pluginSourceMaps, tsconfigSourceMap(dir, compilerOptions)] : pluginSourceMaps;
    if (all.length === 0)
        return;
    const seen = new Set();
    const unique = [];
    for (const sm of all) {
        const key = `${sm.srcDir}\0${sm.outDir}`;
        if (seen.has(key))
            continue;
        seen.add(key);
        unique.push(sm);
    }
    workspace.sourceMaps = unique.sort((a, b) => b.outDir.length - a.outDir.length);
};
const isUnderOutDir = (absPath, outDir) => absPath === outDir || absPath.startsWith(`${outDir}/`);
const rewriteOne = (pair, absSpecifier, extensions) => {
    if (pair.srcDir === pair.outDir || !isUnderOutDir(absSpecifier, pair.outDir))
        return;
    return pair.srcDir + absSpecifier.slice(pair.outDir.length).replace(matchExt, extensions);
};
const rewritePattern = (sourceMaps, absSpecifier, extensions) => {
    for (const sm of sourceMaps) {
        const r = rewriteOne(sm, absSpecifier, extensions);
        if (r)
            return r;
    }
};
export const getWorkspaceManifestHandler = (chief) => {
    return (filePath) => {
        const workspace = chief.findWorkspaceByFilePath(filePath);
        if (!workspace)
            return;
        const manifest = chief.workspacePackages.get(workspace.name)?.manifest;
        if (!manifest?.imports)
            return;
        return { dir: workspace.dir, imports: manifest.imports };
    };
};
export const getModuleSourcePathHandler = (chief) => {
    const toSourceMapCache = new Map();
    return (filePath) => {
        if (!isInternal(filePath) || hasTSExt.test(filePath))
            return;
        if (toSourceMapCache.has(filePath))
            return toSourceMapCache.get(filePath);
        const workspace = chief.findWorkspaceByFilePath(filePath);
        let result;
        if (workspace?.sourceMaps) {
            for (const { srcDir, outDir } of workspace.sourceMaps) {
                if (!(isUnderOutDir(filePath, outDir) || srcDir === outDir))
                    continue;
                const basePath = (srcDir + filePath.slice(outDir.length)).replace(matchExt, '');
                const srcFilePath = findFileWithExtensions(basePath, sourceExtensions);
                if (srcFilePath && srcFilePath !== filePath) {
                    debugLog('*', `Source mapping ${toRelative(filePath, chief.cwd)} → ${toRelative(srcFilePath, chief.cwd)}`);
                    result = srcFilePath;
                    break;
                }
            }
        }
        toSourceMapCache.set(filePath, result);
        return result;
    };
};
export const getToSourcePathsHandler = (chief) => {
    return async (specifiers, dir, extensions = defaultExtensions, label) => {
        const patterns = new Set();
        for (const specifier of specifiers) {
            const absSpecifier = isAbsolute(specifier) ? specifier : prependDirToPattern(dir, specifier);
            const ws = chief.findWorkspaceByFilePath(absSpecifier);
            const mapped = ws?.sourceMaps && rewritePattern(ws.sourceMaps, absSpecifier, extensions);
            patterns.add(mapped ?? absSpecifier);
        }
        const filePaths = await _glob({ patterns: Array.from(patterns), cwd: dir, label });
        debugLogArray(toRelative(dir, chief.cwd), 'Source mapping (package.json)', filePaths);
        return filePaths;
    };
};
export const toSourceMappedSpecifiers = (ws, absSpecifier, extensions = defaultExtensions) => {
    const out = [];
    if (ws?.sourceMaps) {
        for (const sm of ws.sourceMaps) {
            const r = rewriteOne(sm, absSpecifier, extensions);
            if (r)
                out.push(r);
        }
    }
    return out;
};
