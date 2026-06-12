type ParsedValue = any;
export interface ParsedArgs {
    _: string[];
    '--'?: string[];
    [key: string]: ParsedValue;
}
interface Opts {
    string?: string[];
    boolean?: string[];
    alias?: Record<string, string | string[]>;
    '--'?: boolean;
}
declare const parseArgs: (argv: string[], opts?: Opts) => ParsedArgs;
export default parseArgs;
