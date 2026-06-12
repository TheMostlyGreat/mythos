import type { Program } from 'oxc-parser';
export declare const getSrcDir: (program: Program) => string;
export declare const getRoutesDirs: (program: Program, srcDir: string) => string[];
