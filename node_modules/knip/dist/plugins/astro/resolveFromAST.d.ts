import type { Program } from 'oxc-parser';
export declare const getSrcDir: (program: Program) => string;
export declare const usesPassthroughImageService: (program: Program) => boolean;
export declare const getViteAliases: (program: Program) => Record<string, string>;
