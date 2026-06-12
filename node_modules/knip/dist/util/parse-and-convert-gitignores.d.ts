export declare const toExtendedIgnorePattern: (pattern: string) => string;
export declare const expandIgnorePatterns: (patterns: Iterable<string>) => string[];
export declare const convertGitignoreToPicomatchIgnorePatterns: (pattern: string) => {
    negated: boolean;
    pattern: string;
};
export declare const parseAndConvertGitignorePatterns: (patterns: string, ancestor?: string) => {
    negated: boolean;
    pattern: string;
}[];
