import type { ParseResult, Visitor } from 'oxc-parser';
import type { GetImportsAndExportsOptions, IgnoreExportsUsedInFile, PluginVisitorContext } from '../types/config.ts';
import type { FileNode } from '../types/module-graph.ts';
import { type ResolveModule } from './ast-nodes.ts';
export declare const _getImportsAndExports: (filePath: string, sourceText: string, resolveModule: ResolveModule, options: GetImportsAndExportsOptions, ignoreExportsUsedInFile: IgnoreExportsUsedInFile, skipExportsForFile: boolean, visitor: Visitor, pluginCtx: PluginVisitorContext | undefined, cachedParseResult?: ParseResult) => FileNode;
