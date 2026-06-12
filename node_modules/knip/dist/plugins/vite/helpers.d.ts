import type { Program } from 'oxc-parser';
import { type Input } from '../../util/input.ts';
export declare const getBabelInputs: (program: Program) => Input[];
export declare const getIndexHtmlEntries: (rootDir: string) => Promise<Input[]>;
