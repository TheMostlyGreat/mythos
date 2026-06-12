import { AST_NODE_TYPES } from '@typescript-eslint/utils';
import type { ESLint } from 'eslint';
import { ESLintUtils } from '@typescript-eslint/utils';
import type { Linter } from 'eslint';
import { RuleListener } from '@typescript-eslint/utils/ts-eslint';
import { RuleModule } from '@typescript-eslint/utils/ts-eslint';
import type { TSESLint } from '@typescript-eslint/utils';
import { TSESTree } from '@typescript-eslint/utils';

export declare const ASTUtils: {
    isNodeOfOneOf<T extends AST_NODE_TYPES>(node: TSESTree.Node, types: ReadonlyArray<T>): node is TSESTree.Node & {
        type: T;
    };
    isIdentifier(node: TSESTree.Node): node is TSESTree.Identifier;
    isIdentifierWithName(node: TSESTree.Node, name: string): node is TSESTree.Identifier;
    isIdentifierWithOneOfNames<T extends Array<string>>(node: TSESTree.Node, name: T): node is TSESTree.Identifier & {
        name: T[number];
    };
    isProperty(node: TSESTree.Node): node is TSESTree.Property;
    isObjectExpression(node: TSESTree.Node): node is TSESTree.ObjectExpression;
    isPropertyWithIdentifierKey(node: TSESTree.Node, key: string): node is TSESTree.Property;
    findPropertyWithIdentifierKey(properties: Array<TSESTree.ObjectLiteralElement>, key: string): TSESTree.Property | undefined;
    getNestedIdentifiers(node: TSESTree.Node): Array<TSESTree.Identifier>;
    traverseUpOnly(identifier: TSESTree.Node, allowedNodeTypes: Array<AST_NODE_TYPES>): TSESTree.Node;
    isDeclaredInNode(params: {
        functionNode: TSESTree.Node;
        reference: TSESLint.Scope.Reference;
        scopeManager: TSESLint.Scope.ScopeManager;
    }): boolean;
    getExternalRefs(params: {
        scopeManager: TSESLint.Scope.ScopeManager;
        sourceCode: Readonly<TSESLint.SourceCode>;
        node: TSESTree.Node;
    }): Array<TSESLint.Scope.Reference>;
    mapKeyNodeToText(node: TSESTree.Node, sourceCode: Readonly<TSESLint.SourceCode>): string;
    mapKeyNodeToBaseText(node: TSESTree.Node, sourceCode: Readonly<TSESLint.SourceCode>): string;
    isValidReactComponentOrHookName(identifier: TSESTree.Identifier | null | undefined): boolean;
    getFunctionAncestor(sourceCode: Readonly<TSESLint.SourceCode>, node: TSESTree.Node): TSESTree.ArrowFunctionExpression | TSESTree.FunctionDeclarationWithName | TSESTree.FunctionDeclarationWithOptionalName | TSESTree.FunctionExpression | undefined;
    getReferencedExpressionByIdentifier(params: {
        node: TSESTree.Node;
        context: Readonly<TSESLint.RuleContext<string, ReadonlyArray<unknown>>>;
    }): TSESTree.Expression | null;
    getClosestVariableDeclarator(node: TSESTree.Node): TSESTree.VariableDeclaratorDefiniteAssignment | TSESTree.VariableDeclaratorMaybeInit | undefined;
    getNestedReturnStatements(node: TSESTree.Node): Array<TSESTree.ReturnStatement>;
};

export declare const checkedProperties: readonly ["queryFn", "getPreviousPageParam", "getNextPageParam"];

export declare const checkedProperties_alias_1: readonly ["onMutate", "onError", "onSettled"];

declare type Context = Parameters<Create>[0];

declare type Create = Parameters<ReturnType<typeof ESLintUtils.RuleCreator>>[0]['create'];

export declare function createPropertyOrderRule<TFunc extends string, TProp extends string>(options: Omit<Parameters<typeof createRule>[0], 'create'>, targetFunctions: ReadonlyArray<TFunc> | Array<TFunc>, orderRules: ReadonlyArray<Readonly<[ReadonlyArray<TProp>, ReadonlyArray<TProp>]>>): ESLintUtils.RuleModule<string, readonly unknown[], ExtraRuleDocs, ESLintUtils.RuleListener> & {
    name: string;
};

declare const createRule: <Options extends readonly unknown[], MessageIds extends string>({ meta, name, ...rule }: Readonly<ESLintUtils.RuleWithMetaAndName<Options, MessageIds, ExtraRuleDocs>>) => ESLintUtils.RuleModule<MessageIds, Options, ExtraRuleDocs, ESLintUtils.RuleListener> & {
    name: string;
};

export declare function detectTanstackQueryImports(create: EnhancedCreate): Create;

declare type EnhancedCreate = (context: Context, options: Options, helpers: Helpers) => ReturnType<Create>;

export declare const ExhaustiveDepsUtils: {
    isRelevantReference(params: {
        sourceCode: Readonly<TSESLint.SourceCode>;
        reference: TSESLint.Scope.Reference;
        scopeManager: TSESLint.Scope.ScopeManager;
        node: TSESTree.Node;
        filename: string;
    }): boolean;
    /**
     * Given required refs and existing queryKey entries, compute missing dependency paths
     * respecting allowlisted variables and types.
     */
    computeFilteredMissingPaths(params: {
        requiredRefs: Array<{
            path: string;
            root: string;
            allowlistedByType: boolean;
        }>;
        allowlistedVariables: Set<string>;
        existingRootIdentifiers: Set<string>;
        existingFullPaths: Set<string>;
    }): Array<string>;
    /**
     * Extract existing queryKey deps as root identifiers and full member paths.
     */
    collectQueryKeyDeps(params: {
        sourceCode: Readonly<TSESLint.SourceCode>;
        scopeManager: TSESLint.Scope.ScopeManager;
        queryKeyNode: TSESTree.Node;
    }): {
        roots: Set<string>;
        paths: Set<string>;
    };
    isNode(value: unknown): value is TSESTree.Node;
    /**
     * Checks whether the resolved variable is allowlisted by its type annotation
     */
    variableIsAllowlistedByType(params: {
        allowlistedTypes: Set<string>;
        variable: TSESLint.Scope.Variable | null;
    }): boolean;
    isInstanceOfKind(node: TSESTree.Node): boolean;
    /**
     * Normalizes a chain by removing optional chaining operators
     *
     * Example: `a?.b.c!` -> `a.b.c`
     */
    normalizeChain(text: string): string;
    /**
     * Computes the reference path for an identifier
     *
     * Example: `a.b.c!` -> `{ path: 'a.b.c', root: 'a' }`
     */
    computeRefPath(params: {
        identifier: TSESTree.Identifier;
        sourceCode: Readonly<TSESLint.SourceCode>;
    }): {
        path: string;
        root: string;
        coversRootMembers: boolean;
    } | null;
    collectExternalRefsInFunction(params: {
        functionNode: TSESTree.ArrowFunctionExpression | TSESTree.FunctionExpression;
        scopeManager: TSESLint.Scope.ScopeManager;
    }): Array<TSESLint.Scope.Reference>;
    /**
     * Recursively collects type identifiers from a type annotation
     */
    collectTypeIdentifiers(typeNode: TSESTree.TypeNode, out: Set<string>): void;
    /**
     * Gets the function expression nodes from a queryFn property, handling conditional expressions.
     * When neither branch is skipToken, returns both branches so all deps are scanned.
     */
    getQueryFnNodes(queryFn: TSESTree.Property): Array<TSESTree.Node>;
};

export declare type ExtraRuleDocs = {
    recommended: 'strict' | 'error' | 'warn';
};

export declare const getDocsUrl: (ruleName: string) => string;

declare type Helpers = {
    isSpecificTanstackQueryImport: (node: TSESTree.Identifier, source: string) => boolean;
    isTanstackQueryImport: (node: TSESTree.Identifier) => boolean;
};

export declare type InfiniteQueryFunctions = (typeof infiniteQueryFunctions)[number];

export declare const infiniteQueryFunctions: readonly ["infiniteQueryOptions", "useInfiniteQuery", "useSuspenseInfiniteQuery"];

export declare type InfiniteQueryProperties = (typeof checkedProperties)[number];

export declare type MutationFunctions = (typeof mutationFunctions)[number];

export declare const mutationFunctions: readonly ["useMutation"];

export declare type MutationProperties = (typeof checkedProperties_alias_1)[number];

declare const name_2 = "exhaustive-deps";
export { name_2 as name }

export declare const name_alias_1 = "infinite-query-property-order";

export declare const name_alias_2 = "mutation-property-order";

export declare const name_alias_3 = "no-rest-destructuring";

export declare const name_alias_4 = "no-unstable-deps";

export declare const name_alias_5 = "no-void-query-fn";

export declare const name_alias_6 = "prefer-query-options";

export declare const name_alias_7 = "stable-query-client";

export declare const NoRestDestructuringUtils: {
    isObjectRestDestructuring(node: TSESTree.Node): boolean;
};

declare type Options = Parameters<Create>[1];

declare const plugin: {
    meta: {
        name: string;
    };
    configs: {
        recommended: {
            plugins: string[];
            rules: {
                readonly '@tanstack/query/exhaustive-deps': "error";
                readonly '@tanstack/query/no-rest-destructuring': "warn";
                readonly '@tanstack/query/stable-query-client': "error";
                readonly '@tanstack/query/no-unstable-deps': "error";
                readonly '@tanstack/query/infinite-query-property-order': "error";
                readonly '@tanstack/query/no-void-query-fn': "error";
                readonly '@tanstack/query/mutation-property-order': "error";
            };
        };
        recommendedStrict: {
            plugins: string[];
            rules: {
                readonly '@tanstack/query/prefer-query-options': "error";
                readonly '@tanstack/query/exhaustive-deps': "error";
                readonly '@tanstack/query/no-rest-destructuring': "warn";
                readonly '@tanstack/query/stable-query-client': "error";
                readonly '@tanstack/query/no-unstable-deps': "error";
                readonly '@tanstack/query/infinite-query-property-order': "error";
                readonly '@tanstack/query/no-void-query-fn': "error";
                readonly '@tanstack/query/mutation-property-order': "error";
            };
        };
        'flat/recommended': {
            name: string;
            plugins: {
                '@tanstack/query': {};
            };
            rules: {
                readonly '@tanstack/query/exhaustive-deps': "error";
                readonly '@tanstack/query/no-rest-destructuring': "warn";
                readonly '@tanstack/query/stable-query-client': "error";
                readonly '@tanstack/query/no-unstable-deps': "error";
                readonly '@tanstack/query/infinite-query-property-order': "error";
                readonly '@tanstack/query/no-void-query-fn': "error";
                readonly '@tanstack/query/mutation-property-order': "error";
            };
        }[];
        'flat/recommended-strict': {
            name: string;
            plugins: {
                '@tanstack/query': {};
            };
            rules: {
                readonly '@tanstack/query/prefer-query-options': "error";
                readonly '@tanstack/query/exhaustive-deps': "error";
                readonly '@tanstack/query/no-rest-destructuring': "warn";
                readonly '@tanstack/query/stable-query-client': "error";
                readonly '@tanstack/query/no-unstable-deps': "error";
                readonly '@tanstack/query/infinite-query-property-order': "error";
                readonly '@tanstack/query/no-void-query-fn': "error";
                readonly '@tanstack/query/mutation-property-order': "error";
            };
        }[];
    };
    rules: Record<string, RuleModule<string, readonly unknown[], ExtraRuleDocs, RuleListener>>;
};
export { plugin as default_alias }
export { plugin }

declare interface Plugin_2 extends Omit<ESLint.Plugin, 'rules'> {
    rules: Record<RuleKey, RuleModule<any, any, any>>;
    configs: {
        recommended: ESLint.ConfigData;
        recommendedStrict: ESLint.ConfigData;
        'flat/recommended': Array<Linter.Config>;
        'flat/recommended-strict': Array<Linter.Config>;
    };
}
export { Plugin_2 as Plugin }

export declare const reactHookNames: string[];

export declare const rule: ESLintUtils.RuleModule<string, readonly unknown[], ExtraRuleDocs, ESLintUtils.RuleListener> & {
    name: string;
};

export declare const rule_alias_1: RuleModule<string, readonly unknown[], ExtraRuleDocs, RuleListener> & {
    name: string;
};

export declare const rule_alias_2: RuleModule<string, readonly unknown[], ExtraRuleDocs, RuleListener> & {
    name: string;
};

export declare const rule_alias_3: ESLintUtils.RuleModule<string, readonly unknown[], ExtraRuleDocs, ESLintUtils.RuleListener> & {
    name: string;
};

export declare const rule_alias_4: ESLintUtils.RuleModule<string, readonly unknown[], ExtraRuleDocs, ESLintUtils.RuleListener> & {
    name: string;
};

export declare const rule_alias_5: ESLintUtils.RuleModule<string, readonly unknown[], ExtraRuleDocs, ESLintUtils.RuleListener> & {
    name: string;
};

export declare const rule_alias_6: ESLintUtils.RuleModule<string, readonly unknown[], ExtraRuleDocs, ESLintUtils.RuleListener> & {
    name: string;
};

export declare const rule_alias_7: ESLintUtils.RuleModule<string, readonly unknown[], ExtraRuleDocs, ESLintUtils.RuleListener> & {
    name: string;
};

declare type RuleKey = keyof typeof rules;

export declare const rules: Record<string, ESLintUtils.RuleModule<string, ReadonlyArray<unknown>, ExtraRuleDocs, ESLintUtils.RuleListener>>;

export declare function sortDataByOrder<T, TKey extends keyof T>(data: Array<T> | ReadonlyArray<T>, orderRules: ReadonlyArray<Readonly<[ReadonlyArray<T[TKey]>, ReadonlyArray<T[TKey]>]>>, key: TKey): Array<T> | null;

export declare const sortRules: readonly [readonly [readonly ["queryFn"], readonly ["getPreviousPageParam", "getNextPageParam"]]];

export declare const sortRules_alias_1: readonly [readonly [readonly ["onMutate"], readonly ["onError", "onSettled"]]];

export declare function uniqueBy<T>(arr: Array<T>, fn: (x: T) => unknown): Array<T>;

export declare const useQueryHookNames: string[];

export { }
