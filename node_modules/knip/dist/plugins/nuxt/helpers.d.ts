import { type ParseResult } from 'oxc-parser';
import type { TemplateAstNode, VueSfc } from './types.ts';
export declare const getVueSfc: (cwd: string) => VueSfc;
export declare const readAndParseFile: (filePath: string) => ParseResult;
export declare const collectIdentifiers: (source: string, fileName: string) => Set<string>;
export declare const collectTemplateInfo: (tree: TemplateAstNode) => {
    tags: Set<string>;
    identifiers: Set<string>;
};
export declare const toKebabCase: (s: string) => string;
export declare const collectLocalImportPaths: (filePath: string, result: ParseResult) => Set<string>;
export declare function buildAutoImportMap(filePath: string, result: ParseResult): {
    importMap: Map<string, string>;
    componentMap: Map<string, string[]>;
};
