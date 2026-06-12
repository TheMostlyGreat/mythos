import type { ArithmeticCommandExpansion, ArithmeticExpression } from "./types.ts";
export declare function drainArithCmdExps(): ArithmeticCommandExpansion[] | null;
export declare function parseArithmeticExpression(src: string, offset?: number): ArithmeticExpression | null;
