import type { SourceMap } from '../types/config.ts';
import type { CompilerOptions } from '../types/project.ts';
import type { ConfigurationChief, Workspace } from '../ConfigurationChief.ts';
export declare const augmentWorkspace: (workspace: Workspace, dir: string, compilerOptions: CompilerOptions | undefined, pluginSourceMaps?: SourceMap[]) => void;
export type WorkspaceManifestHandler = (filePath: string) => {
    dir: string;
    imports: unknown;
} | undefined;
export declare const getWorkspaceManifestHandler: (chief: ConfigurationChief) => WorkspaceManifestHandler;
export declare const getModuleSourcePathHandler: (chief: ConfigurationChief) => (filePath: string) => string | undefined;
export declare const getToSourcePathsHandler: (chief: ConfigurationChief) => (specifiers: Set<string>, dir: string, extensions: (string | undefined) | undefined, label: string) => Promise<string[]>;
export declare const toSourceMappedSpecifiers: (ws: Workspace | undefined, absSpecifier: string, extensions?: string) => string[];
export type ToSourceFilePath = ReturnType<typeof getModuleSourcePathHandler>;
