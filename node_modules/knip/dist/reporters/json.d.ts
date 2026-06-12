import type { ReporterOptions } from '../types/issues.ts';
export interface JSONReportNamedItem {
    name: string;
}
export interface JSONReportItem extends JSONReportNamedItem {
    namespace?: string;
    pos?: number;
    line?: number;
    col?: number;
}
export type JSONReportEntry = {
    file: string;
    owners?: Array<JSONReportNamedItem>;
    binaries?: Array<JSONReportNamedItem>;
    catalog?: Array<JSONReportItem>;
    dependencies?: Array<JSONReportItem>;
    devDependencies?: Array<JSONReportItem>;
    duplicates?: Array<Array<JSONReportItem>>;
    enumMembers?: Array<JSONReportItem>;
    exports?: Array<JSONReportItem>;
    files?: Array<JSONReportItem>;
    namespaceMembers?: Array<JSONReportItem>;
    nsExports?: Array<JSONReportItem>;
    nsTypes?: Array<JSONReportItem>;
    optionalPeerDependencies?: Array<JSONReportItem>;
    types?: Array<JSONReportItem>;
    unlisted?: Array<JSONReportNamedItem>;
    unresolved?: Array<JSONReportItem>;
};
export type JSONReport = {
    issues: Array<JSONReportEntry>;
};
declare const _default: ({ report, issues, options, cwd }: ReporterOptions) => Promise<void>;
export default _default;
