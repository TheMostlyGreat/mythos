//#region \0rolldown/runtime.js
var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __exportAll = (all, no_symbols) => {
	let target = {};
	for (var name in all) __defProp(target, name, {
		get: all[name],
		enumerable: true
	});
	if (!no_symbols) __defProp(target, Symbol.toStringTag, { value: "Module" });
	return target;
};
var __copyProps = (to, from, except, desc) => {
	if (from && typeof from === "object" || typeof from === "function") for (var keys = __getOwnPropNames(from), i = 0, n = keys.length, key; i < n; i++) {
		key = keys[i];
		if (!__hasOwnProp.call(to, key) && key !== except) __defProp(to, key, {
			get: ((k) => from[k]).bind(null, key),
			enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable
		});
	}
	return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", {
	value: mod,
	enumerable: true
}) : target, mod));
//#endregion
let node_module = require("node:module");
node_module = __toESM(node_module);
let node_path = require("node:path");
node_path = __toESM(node_path);
let _typescript_eslint_types = require("@typescript-eslint/types");
let _eslint_community_eslint_utils = require("@eslint-community/eslint-utils");
let eslint_compat_utils = require("eslint-compat-utils");
let postcss = require("postcss");
postcss = __toESM(postcss);
let postcss_selector_parser = require("postcss-selector-parser");
postcss_selector_parser = __toESM(postcss_selector_parser);
let _jridgewell_sourcemap_codec = require("@jridgewell/sourcemap-codec");
let globals = require("globals");
globals = __toESM(globals);
let astro_eslint_parser = require("astro-eslint-parser");
astro_eslint_parser = __toESM(astro_eslint_parser);
//#region src/configs/has-typescript-eslint-parser.ts
let hasTypescriptEslintParser = false;
let tsESLintParser = null;
try {
	const cwd = process.cwd();
	if (tsESLintParser = (0, node_module.createRequire)(node_path.default.join(cwd, "__placeholder__.js"))("@typescript-eslint/parser")) hasTypescriptEslintParser = true;
} catch {}
//#endregion
//#region src/configs/base.ts
/**
* Build legacy base config
*/
function buildLegacyBase() {
	return {
		plugins: ["astro"],
		overrides: [
			{
				files: ["*.astro"],
				plugins: ["astro"],
				env: {
					node: true,
					"astro/astro": true,
					es2020: true
				},
				parser: require.resolve("astro-eslint-parser"),
				parserOptions: {
					parser: hasTypescriptEslintParser ? "@typescript-eslint/parser" : void 0,
					extraFileExtensions: [".astro"],
					sourceType: "module"
				},
				rules: {}
			},
			{
				files: ["**/*.astro/*.js", "*.astro/*.js"],
				env: {
					browser: true,
					es2020: true
				},
				parserOptions: { sourceType: "module" },
				rules: { "prettier/prettier": "off" }
			},
			{
				files: ["**/*.astro/*.ts", "*.astro/*.ts"],
				env: {
					browser: true,
					es2020: true
				},
				parser: hasTypescriptEslintParser ? "@typescript-eslint/parser" : void 0,
				parserOptions: {
					sourceType: "module",
					project: null
				},
				rules: { "prettier/prettier": "off" }
			}
		]
	};
}
var recommended_default$1 = {
	extends: ["plugin:astro/base"],
	rules: {
		"astro/missing-client-only-directive-value": "error",
		"astro/no-conflict-set-directives": "error",
		"astro/no-deprecated-astro-canonicalurl": "error",
		"astro/no-deprecated-astro-fetchcontent": "error",
		"astro/no-deprecated-astro-resolve": "error",
		"astro/no-deprecated-getentrybyslug": "error",
		"astro/no-unused-define-vars-in-style": "error",
		"astro/valid-compile": "error"
	}
};
//#endregion
//#region src/utils/index.ts
/**
* Define the rule.
* @param ruleName ruleName
* @param rule rule module
*/
function createRule(ruleName, rule) {
	return {
		meta: {
			...rule.meta,
			docs: {
				available: () => true,
				...rule.meta.docs,
				url: `https://ota-meshi.github.io/eslint-plugin-astro/rules/${ruleName}/`,
				ruleId: `astro/${ruleName}`,
				ruleName
			}
		},
		create: rule.create
	};
}
//#endregion
//#region src/utils/compat.ts
/**
* Returns an extended instance of `context.sourceCode` or the result of `context.getSourceCode()`.
* Extended instances can use new APIs such as `getScope(node)` even with old ESLint.
*/
function getSourceCode(context) {
	return (0, eslint_compat_utils.getSourceCode)(context);
}
/**
* Gets the value of `context.filename`, but for older ESLint it returns the result of `context.getFilename()`.
*/
function getFilename(context) {
	return (0, eslint_compat_utils.getFilename)(context);
}
/**
* Gets the value of `context.cwd`, but for older ESLint it returns the result of `context.getCwd()`.
* Versions older than v6.6.0 return a value from the result of `process.cwd()`.
*/
function getCwd(context) {
	return (0, eslint_compat_utils.getCwd)(context);
}
//#endregion
//#region src/utils/ast-utils.ts
const anyFunctionPattern = /^(?:Function(?:Declaration|Expression)|ArrowFunctionExpression)$/u;
/**
* Get the attribute key name from given attribute node
*/
function getAttributeName(node) {
	if (node.type === "JSXSpreadAttribute") return null;
	const { name } = node;
	return getName(name);
}
/**
* Get the element name from given node
*/
function getElementName(node) {
	const nameNode = node.openingElement.name;
	return getName(nameNode);
}
/**
* Find the attribute from the given element node
*/
function findAttribute(node, name) {
	const openingElement = node.openingElement;
	for (const attr of openingElement.attributes) {
		if (attr.type === "JSXSpreadAttribute") continue;
		if (getAttributeName(attr) === name) return attr;
	}
	return null;
}
/**
* Gets the spread attributes from the given element node
*/
function getSpreadAttributes(node) {
	return node.openingElement.attributes.filter((attr) => attr.type === "JSXSpreadAttribute");
}
/**
* Get the static attribute string value from given attribute
*/
function getStaticAttributeStringValue(node, context) {
	const value = getStaticAttributeValue(node, context);
	if (!value) return null;
	return value.value != null ? String(value.value) : value.value;
}
/**
* Get the static attribute value from given attribute
*/
function getStaticAttributeValue(node, context) {
	if (node.value?.type === _typescript_eslint_types.AST_NODE_TYPES.Literal) return { value: node.value.value };
	if (context && node.value?.type === "JSXExpressionContainer" && node.value.expression.type !== "JSXEmptyExpression") {
		const sourceCode = getSourceCode(context);
		const staticValue = (0, _eslint_community_eslint_utils.getStaticValue)(node.value.expression, sourceCode.scopeManager.globalScope);
		if (staticValue != null) return staticValue;
	}
	return null;
}
/** Checks whether given node evaluate type is string */
function isStringCallExpression(node) {
	if (node.type === _typescript_eslint_types.AST_NODE_TYPES.CallExpression) return node.callee.type === _typescript_eslint_types.AST_NODE_TYPES.Identifier && node.callee.name === "String";
	return false;
}
/** Checks whether given node is StringLiteral */
function isStringLiteral(node) {
	return node.type === _typescript_eslint_types.AST_NODE_TYPES.Literal && typeof node.value === "string";
}
/** If it is concatenated with a plus, it gets its elements as an array. */
function extractConcatExpressions(node, sourceCode) {
	if (node.operator !== "+") return null;
	const leftResult = processLeft(node.left);
	if (leftResult == null) return null;
	return [...leftResult, node.right];
	/** Process for left expression */
	function processLeft(expr) {
		if (expr.type === _typescript_eslint_types.AST_NODE_TYPES.BinaryExpression) {
			if (!(0, _eslint_community_eslint_utils.isParenthesized)(expr, sourceCode) && expr.operator !== "*" && expr.operator !== "/") return extractConcatExpressions(expr, sourceCode);
		}
		return [expr];
	}
}
/**
* Get the value of a given node if it's a literal or a template literal.
*/
function getStringIfConstant(node) {
	if (node.type === "Literal") {
		if (typeof node.value === "string") return node.value;
	} else if (node.type === "TemplateLiteral") {
		let str = "";
		const quasis = [...node.quasis];
		const expressions = [...node.expressions];
		let quasi, expr;
		while (quasi = quasis.shift()) {
			str += quasi.value.cooked;
			expr = expressions.shift();
			if (expr) {
				const exprStr = getStringIfConstant(expr);
				if (exprStr == null) return null;
				str += exprStr;
			}
		}
		return str;
	} else if (node.type === "BinaryExpression") {
		if (node.operator === "+") {
			const left = getStringIfConstant(node.left);
			if (left == null) return null;
			const right = getStringIfConstant(node.right);
			if (right == null) return null;
			return left + right;
		}
	}
	return null;
}
/**
* Check if it need parentheses.
*/
function needParentheses(node, kind) {
	if (node.type === "ArrowFunctionExpression" || node.type === "AssignmentExpression" || node.type === "BinaryExpression" || node.type === "ConditionalExpression" || node.type === "LogicalExpression" || node.type === "SequenceExpression" || node.type === "UnaryExpression" || node.type === "UpdateExpression") return true;
	if (kind === "logical") return node.type === "FunctionExpression";
	return false;
}
/**
* Get parenthesized range from the given node
*/
function getParenthesizedTokens(node, sourceCode) {
	let lastLeft = sourceCode.getFirstToken(node);
	let lastRight = sourceCode.getLastToken(node);
	let maybeLeftParen, maybeRightParen;
	while ((maybeLeftParen = sourceCode.getTokenBefore(lastLeft)) && (maybeRightParen = sourceCode.getTokenAfter(lastRight)) && (0, _eslint_community_eslint_utils.isOpeningParenToken)(maybeLeftParen) && (0, _eslint_community_eslint_utils.isClosingParenToken)(maybeRightParen) && maybeLeftParen !== getParentSyntaxParen(node, sourceCode)) {
		lastLeft = maybeLeftParen;
		lastRight = maybeRightParen;
		maybeLeftParen = sourceCode.getTokenBefore(lastLeft);
		maybeRightParen = sourceCode.getTokenAfter(lastRight);
	}
	return {
		left: lastLeft,
		right: lastRight
	};
}
/**
* Get parenthesized range from the given node
*/
function getParenthesizedRange(node, sourceCode) {
	const { left, right } = getParenthesizedTokens(node, sourceCode);
	return [left.range[0], right.range[1]];
}
/**
* Get the left parenthesis of the parent node syntax if it exists.
* E.g., `if (a) {}` then the `(`.
* @param {Node} node The AST node to check.
* @param {SourceCode} sourceCode The source code object to get tokens.
* @returns {Token|null} The left parenthesis of the parent node syntax
*/
function getParentSyntaxParen(node, sourceCode) {
	const parent = node.parent;
	switch (parent.type) {
		case "CallExpression":
		case "NewExpression":
			if (parent.arguments.length === 1 && parent.arguments[0] === node) return sourceCode.getTokenAfter(parent.callee, {
				includeComments: false,
				filter: _eslint_community_eslint_utils.isOpeningParenToken
			});
			return null;
		case "DoWhileStatement":
			if (parent.test === node) return sourceCode.getTokenAfter(parent.body, {
				includeComments: false,
				filter: _eslint_community_eslint_utils.isOpeningParenToken
			});
			return null;
		case "IfStatement":
		case "WhileStatement":
			if (parent.test === node) return sourceCode.getFirstToken(parent, {
				includeComments: false,
				skip: 1
			});
			return null;
		case "ImportExpression":
			if (parent.source === node) return sourceCode.getFirstToken(parent, {
				includeComments: false,
				skip: 1
			});
			return null;
		case "SwitchStatement":
			if (parent.discriminant === node) return sourceCode.getFirstToken(parent, {
				includeComments: false,
				skip: 1
			});
			return null;
		case "WithStatement":
			if (parent.object === node) return sourceCode.getFirstToken(parent, {
				includeComments: false,
				skip: 1
			});
			return null;
		default: return null;
	}
}
/**
* Get the name from given name node
*/
function getName(nameNode) {
	if (nameNode.type === "JSXIdentifier") return nameNode.name;
	if (nameNode.type === "JSXNamespacedName") return `${nameNode.namespace.name}:${nameNode.name.name}`;
	if (nameNode.type === "JSXMemberExpression") return `${getName(nameNode.object)}.${nameNode.property.name}`;
	return null;
}
/**
* Determines whether two adjacent tokens are on the same line.
* @param left The left token object.
* @param right The right token object.
* @returns Whether or not the tokens are on the same line.
* @public
*/
function isTokenOnSameLine(left, right) {
	return left?.loc?.end.line === right?.loc?.start.line;
}
/**
* Gets next location when the result is not out of bound, otherwise returns null.
*
* Assumptions:
*
* - The given location represents a valid location in the given source code.
* - Columns are 0-based.
* - Lines are 1-based.
* - Column immediately after the last character in a line (not incl. linebreaks) is considered to be a valid location.
* - If the source code ends with a linebreak, `sourceCode.lines` array will have an extra element (empty string) at the end.
*   The start (column 0) of that extra line is considered to be a valid location.
*
* Examples of successive locations (line, column):
*
* code: foo
* locations: (1, 0) -> (1, 1) -> (1, 2) -> (1, 3) -> null
*
* code: foo<LF>
* locations: (1, 0) -> (1, 1) -> (1, 2) -> (1, 3) -> (2, 0) -> null
*
* code: foo<CR><LF>
* locations: (1, 0) -> (1, 1) -> (1, 2) -> (1, 3) -> (2, 0) -> null
*
* code: a<LF>b
* locations: (1, 0) -> (1, 1) -> (2, 0) -> (2, 1) -> null
*
* code: a<LF>b<LF>
* locations: (1, 0) -> (1, 1) -> (2, 0) -> (2, 1) -> (3, 0) -> null
*
* code: a<CR><LF>b<CR><LF>
* locations: (1, 0) -> (1, 1) -> (2, 0) -> (2, 1) -> (3, 0) -> null
*
* code: a<LF><LF>
* locations: (1, 0) -> (1, 1) -> (2, 0) -> (3, 0) -> null
*
* code: <LF>
* locations: (1, 0) -> (2, 0) -> null
*
* code:
* locations: (1, 0) -> null
* @param sourceCode The sourceCode
* @param location The location
* @returns Next location
*/
function getNextLocation(sourceCode, { column, line }) {
	if (column < sourceCode.lines[line - 1].length) return {
		column: column + 1,
		line
	};
	if (line < sourceCode.lines.length) return {
		column: 0,
		line: line + 1
	};
	return null;
}
/**
* Finds a function node from ancestors of a node.
* @param node A start node to find.
* @returns A found function node.
*/
function getUpperFunction(node) {
	for (let currentNode = node; currentNode; currentNode = currentNode.parent) if (anyFunctionPattern.test(currentNode.type)) return currentNode;
	return null;
}
//#endregion
//#region src/rules/missing-client-only-directive-value.ts
var missing_client_only_directive_value_default = createRule("missing-client-only-directive-value", {
	meta: {
		docs: {
			description: "the client:only directive is missing the correct component's framework value",
			category: "Possible Errors",
			recommended: true
		},
		schema: [],
		messages: { missingValue: "`client:only` directive is missing a value" },
		type: "problem"
	},
	create(context) {
		if (!getSourceCode(context).parserServices?.isAstro) return {};
		/** VerifyDirectiveValue */
		function verifyDirectiveValue(attr) {
			if (getAttributeName(attr) !== "client:only") return;
			if (getStaticAttributeValue(attr, context) !== null) return;
			context.report({
				node: attr.name,
				messageId: "missingValue"
			});
		}
		return {
			JSXAttribute: verifyDirectiveValue,
			AstroTemplateLiteralAttribute: verifyDirectiveValue
		};
	}
});
//#endregion
//#region src/rules/no-conflict-set-directives.ts
var no_conflict_set_directives_default = createRule("no-conflict-set-directives", {
	meta: {
		docs: {
			description: "disallow conflicting set directives and child contents",
			category: "Possible Errors",
			recommended: true
		},
		schema: [],
		messages: { conflict: "{{name}} conflicts with {{conflictTargets}}." },
		type: "problem"
	},
	create(context) {
		const sourceCode = getSourceCode(context);
		if (!sourceCode.parserServices?.isAstro) return {};
		return { JSXElement(node) {
			const reportData = [];
			for (const attr of node.openingElement.attributes) {
				const directiveName = getAttributeName(attr);
				if (directiveName === "set:text" || directiveName === "set:html") reportData.push({
					loc: attr.loc,
					name: `'${directiveName}'`
				});
			}
			if (reportData.length) {
				const targetChildren = node.children.filter((child) => {
					if (child.type === "AstroHTMLComment") return false;
					if (child.type === "JSXText" || child.type === "AstroRawText") return Boolean(child.value.trim());
					return true;
				}).map((child) => {
					if (child.type === "JSXText" || child.type === "AstroRawText") {
						const leadingSpaces = /^\s*/.exec(child.value)[0];
						const trailingSpaces = /\s*$/.exec(child.value)[0];
						return { loc: {
							start: sourceCode.getLocFromIndex(child.range[0] + leadingSpaces.length),
							end: sourceCode.getLocFromIndex(child.range[1] - trailingSpaces.length)
						} };
					}
					return child;
				});
				if (targetChildren.length) reportData.push({
					loc: {
						start: targetChildren[0].loc.start,
						end: targetChildren[targetChildren.length - 1].loc.end
					},
					name: "child contents"
				});
			}
			if (reportData.length >= 2) for (const data of reportData) {
				const conflictTargets = reportData.filter((d) => d !== data).map((d) => d.name);
				context.report({
					loc: data.loc,
					messageId: "conflict",
					data: {
						name: data.name,
						conflictTargets: [conflictTargets.slice(0, -1).join(", "), conflictTargets.slice(-1)[0]].filter(Boolean).join(", and ")
					}
				});
			}
		} };
	}
});
//#endregion
//#region src/rules/no-deprecated-astro-canonicalurl.ts
var no_deprecated_astro_canonicalurl_default = createRule("no-deprecated-astro-canonicalurl", {
	meta: {
		docs: {
			description: "disallow using deprecated `Astro.canonicalURL`",
			category: "Possible Errors",
			recommended: true
		},
		schema: [],
		messages: { deprecated: "'Astro.canonicalURL' is deprecated. Use 'Astro.url' helper instead." },
		type: "problem"
	},
	create(context) {
		const sourceCode = getSourceCode(context);
		if (!sourceCode.parserServices?.isAstro) return {};
		return { "Program:exit"(node) {
			const tracker = new _eslint_community_eslint_utils.ReferenceTracker(sourceCode.getScope(node));
			for (const { node, path } of tracker.iterateGlobalReferences({ Astro: { canonicalURL: { [_eslint_community_eslint_utils.READ]: true } } })) context.report({
				node,
				messageId: "deprecated",
				data: { name: path.join(".") }
			});
		} };
	}
});
//#endregion
//#region src/rules/no-deprecated-astro-fetchcontent.ts
var no_deprecated_astro_fetchcontent_default = createRule("no-deprecated-astro-fetchcontent", {
	meta: {
		docs: {
			description: "disallow using deprecated `Astro.fetchContent()`",
			category: "Possible Errors",
			recommended: true
		},
		schema: [],
		messages: { deprecated: "'Astro.fetchContent()' is deprecated. Use 'Astro.glob()' instead." },
		type: "problem",
		fixable: "code"
	},
	create(context) {
		const sourceCode = getSourceCode(context);
		if (!sourceCode.parserServices?.isAstro) return {};
		return { "Program:exit"(node) {
			const tracker = new _eslint_community_eslint_utils.ReferenceTracker(sourceCode.getScope(node));
			for (const { node, path } of tracker.iterateGlobalReferences({ Astro: { fetchContent: { [_eslint_community_eslint_utils.READ]: true } } })) context.report({
				node,
				messageId: "deprecated",
				data: { name: path.join(".") },
				fix(fixer) {
					if (node.type !== "MemberExpression" || node.computed) return null;
					return fixer.replaceText(node.property, "glob");
				}
			});
		} };
	}
});
//#endregion
//#region src/rules/no-deprecated-astro-resolve.ts
var no_deprecated_astro_resolve_default = createRule("no-deprecated-astro-resolve", {
	meta: {
		docs: {
			description: "disallow using deprecated `Astro.resolve()`",
			category: "Possible Errors",
			recommended: true
		},
		schema: [],
		messages: { deprecated: "'Astro.resolve()' is deprecated." },
		type: "problem"
	},
	create(context) {
		const sourceCode = getSourceCode(context);
		if (!sourceCode.parserServices?.isAstro) return {};
		return { "Program:exit"(node) {
			const tracker = new _eslint_community_eslint_utils.ReferenceTracker(sourceCode.getScope(node));
			for (const { node, path } of tracker.iterateGlobalReferences({ Astro: { resolve: { [_eslint_community_eslint_utils.READ]: true } } })) context.report({
				node,
				messageId: "deprecated",
				data: { name: path.join(".") }
			});
		} };
	}
});
//#endregion
//#region src/rules/no-deprecated-getentrybyslug.ts
var no_deprecated_getentrybyslug_default = createRule("no-deprecated-getentrybyslug", {
	meta: {
		docs: {
			description: "disallow using deprecated `getEntryBySlug()`",
			category: "Possible Errors",
			recommended: true
		},
		schema: [],
		messages: { deprecated: "'getEntryBySlug()' is deprecated. Use 'getEntry()' instead." },
		type: "problem"
	},
	create(context) {
		if (!getSourceCode(context).parserServices?.isAstro) return {};
		return { ImportSpecifier(node) {
			if (node.imported.type === "Identifier" && node.imported.name === "getEntryBySlug" && node.parent?.type === "ImportDeclaration" && node.parent.source.value === "astro:content") context.report({
				node,
				messageId: "deprecated"
			});
		} };
	}
});
//#endregion
//#region src/rules/no-exports-from-components.ts
const ALLOWED_EXPORTS = new Set([
	"getStaticPaths",
	"partial",
	"prerender"
]);
var no_exports_from_components_default = createRule("no-exports-from-components", {
	meta: {
		docs: {
			description: "disallow value export",
			category: "Possible Errors",
			recommended: false
		},
		schema: [],
		messages: { disallowExport: "Exporting values from components is not allowed." },
		type: "problem"
	},
	create(context) {
		if (!getSourceCode(context).parserServices?.isAstro) return {};
		/**
		* Verify for export declarations
		*/
		function verifyDeclaration(node) {
			if (!node) return;
			if (node.type.startsWith("TS") && !node.type.endsWith("Expression")) return;
			if (node.type === "FunctionDeclaration" && node.id && ALLOWED_EXPORTS.has(node.id.name) || node.type === "VariableDeclaration" && node.declarations.every((decl) => decl.id.type === "Identifier" && ALLOWED_EXPORTS.has(decl.id.name))) return;
			context.report({
				node,
				messageId: "disallowExport"
			});
		}
		return {
			ExportAllDeclaration(node) {
				if (node.exportKind === "type") return;
				context.report({
					node,
					messageId: "disallowExport"
				});
			},
			ExportDefaultDeclaration(node) {
				if (node.exportKind === "type") return;
				verifyDeclaration(node.declaration);
			},
			ExportNamedDeclaration(node) {
				if (node.exportKind === "type") return;
				verifyDeclaration(node.declaration);
				for (const spec of node.specifiers) {
					if (spec.exportKind === "type" || spec.exported.type !== "Identifier") continue;
					if (ALLOWED_EXPORTS.has(spec.exported.name)) continue;
					context.report({
						node: spec,
						messageId: "disallowExport"
					});
				}
			}
		};
	}
});
//#endregion
//#region src/rules/no-prerender-export-outside-pages.ts
const PAGES_DIR_PATTERN = /(?:^|[/\\])pages[/\\]/;
const rule = createRule("no-prerender-export-outside-pages", {
	meta: {
		docs: {
			description: "disallow `prerender` export outside of pages/ directory",
			category: "Possible Errors",
			recommended: false
		},
		schema: [],
		messages: { disallowPrerenderOutsidePages: "'prerender' export is only valid inside a pages/ directory." },
		type: "problem"
	},
	create(context) {
		if (!getSourceCode(context).parserServices?.isAstro) return {};
		const filename = getFilename(context);
		if (PAGES_DIR_PATTERN.test(filename)) return {};
		/**
		* Verify for export declarations
		*/
		function verifyDeclaration(node) {
			if (!node) return;
			if (node.type === "VariableDeclaration" && node.declarations.some((decl) => decl.id.type === "Identifier" && decl.id.name === "prerender")) context.report({
				node,
				messageId: "disallowPrerenderOutsidePages"
			});
		}
		return { ExportNamedDeclaration(node) {
			if (node.exportKind === "type") return;
			verifyDeclaration(node.declaration);
			for (const spec of node.specifiers) {
				if (spec.exportKind === "type") continue;
				if (spec.exported.type === "Identifier" && spec.exported.name === "prerender") context.report({
					node: spec,
					messageId: "disallowPrerenderOutsidePages"
				});
			}
		} };
	}
});
//#endregion
//#region src/rules/no-set-html-directive.ts
var no_set_html_directive_default = createRule("no-set-html-directive", {
	meta: {
		docs: {
			description: "disallow use of `set:html` to prevent XSS attack",
			category: "Security Vulnerability",
			recommended: false
		},
		schema: [],
		messages: { unexpected: "`set:html` can lead to XSS attack." },
		type: "suggestion"
	},
	create(context) {
		if (!getSourceCode(context).parserServices?.isAstro) return {};
		/** Verify */
		function verifyName(attr) {
			if (getAttributeName(attr) !== "set:html") return;
			context.report({
				node: attr.name,
				messageId: "unexpected"
			});
		}
		return {
			JSXAttribute: verifyName,
			AstroTemplateLiteralAttribute: verifyName
		};
	}
});
//#endregion
//#region src/rules/no-set-text-directive.ts
var no_set_text_directive_default = createRule("no-set-text-directive", {
	meta: {
		docs: {
			description: "disallow use of `set:text`",
			category: "Best Practices",
			recommended: false
		},
		schema: [],
		messages: { disallow: "Don't use `set:text`." },
		type: "suggestion",
		fixable: "code"
	},
	create(context) {
		const sourceCode = getSourceCode(context);
		if (!sourceCode.parserServices?.isAstro) return {};
		/** Verify */
		function verifyName(attr) {
			if (getAttributeName(attr) !== "set:text") return;
			context.report({
				node: attr.name,
				messageId: "disallow",
				*fix(fixer) {
					const element = attr.parent.parent;
					if (!attr.value || !element || element.type !== "JSXElement") return;
					if (element.children.some((child) => child.type !== "JSXText" || child.value.trim())) return;
					const valueText = attr.type === "AstroTemplateLiteralAttribute" ? `{${sourceCode.getText(attr.value)}}` : sourceCode.getText(attr.value);
					if (element.openingElement.selfClosing) {
						if (sourceCode.text.slice(element.openingElement.range[1] - 2, element.openingElement.range[1]) !== "/>") return;
						yield fixer.remove(attr);
						yield fixer.removeRange([element.openingElement.range[1] - 2, element.openingElement.range[1] - 1]);
						yield fixer.insertTextAfter(element.openingElement, `${valueText}</${sourceCode.getText(element.openingElement.name)}>`);
					} else {
						yield fixer.remove(attr);
						yield* element.children.map((child) => fixer.remove(child));
						yield fixer.insertTextAfter(element.openingElement, valueText);
					}
				}
			});
		}
		return {
			JSXAttribute: verifyName,
			AstroTemplateLiteralAttribute: verifyName
		};
	}
});
//#endregion
//#region src/rules/no-unsafe-inline-scripts.ts
var no_unsafe_inline_scripts_default = createRule("no-unsafe-inline-scripts", {
	meta: {
		docs: {
			description: "disallow inline `<script>` without `src` to encourage CSP-safe patterns",
			category: "Security Vulnerability",
			recommended: false,
			default: "warn"
		},
		schema: [{
			type: "object",
			properties: {
				allowDefineVars: { type: "boolean" },
				allowModuleScripts: { type: "boolean" },
				allowNonExecutingTypes: {
					type: "array",
					items: { type: "string" }
				},
				allowNonce: { type: "boolean" }
			},
			additionalProperties: false
		}],
		messages: { unexpected: "Unsafe inline <script> detected. Move code to an external file (use src) or a safer pattern." },
		type: "suggestion"
	},
	create(context) {
		if (!getSourceCode(context).parserServices?.isAstro) return {};
		const options = context.options[0] ?? {};
		const allowDefineVars = options.allowDefineVars === true;
		const allowModuleScripts = options.allowModuleScripts === true;
		const allowNonExecutingTypes = new Set((options.allowNonExecutingTypes ?? ["application/ld+json", "application/json"]).map((type) => type.trim().toLowerCase().split(";")[0].trim()));
		const allowNonce = options.allowNonce === true;
		return { JSXElement(node) {
			if (getElementName(node) !== "script") return;
			if (!isInlineScript(node)) return;
			const typeAttr = findAttribute(node, "type");
			if (isAllowedByType(typeAttr, context, allowNonExecutingTypes)) return;
			if (isModuleScript(typeAttr, context, allowModuleScripts)) return;
			const attrs = node.openingElement.attributes;
			if (isDefineVars(attrs, allowDefineVars)) return;
			if (allowNonce && hasNonce(attrs)) return;
			const reportTarget = node.openingElement.name;
			context.report({
				node: reportTarget,
				messageId: "unexpected"
			});
		} };
	}
});
/**
* Normalize a MIME type string by trimming, lowercasing, and dropping parameters.
*/
function normalizeMimeType(value) {
	if (!value) return null;
	return String(value).trim().toLowerCase().split(";")[0].trim();
}
/**
* Determine if the provided type attribute is listed in the allowed MIME type set.
*/
function isAllowedByType(attr, context, allowedTypes) {
	if (!attr) return false;
	const value = getStaticAttributeStringValue(attr, context);
	if (!value) return false;
	const normalizedType = normalizeMimeType(value);
	return normalizedType != null && allowedTypes.has(normalizedType);
}
/**
* Check whether inline scripts with define:vars should be treated as allowed.
*/
function isDefineVars(attrs, allowDefineVars) {
	if (!allowDefineVars) return false;
	for (const attr of attrs) {
		if (attr.type === "JSXSpreadAttribute") continue;
		if (getAttributeName(attr) === "define:vars") return true;
	}
	return false;
}
/**
* Verify if the script's type attribute qualifies as an allowed module script.
*/
function isModuleScript(attr, context, allowModuleScripts) {
	if (!allowModuleScripts) return false;
	if (!attr) return false;
	return normalizeMimeType(getStaticAttributeStringValue(attr, context)) === "module";
}
/**
* Detect the presence of a nonce attribute to satisfy CSP allowances.
*/
function hasNonce(attrs) {
	for (const attr of attrs) {
		if (attr.type === "JSXSpreadAttribute") continue;
		if (getAttributeName(attr) === "nonce") return true;
	}
	return false;
}
/**
* Determine if a <script> element is inline by checking for the absence of src.
*/
function isInlineScript(node) {
	if (findAttribute(node, "src")) return false;
	return true;
}
//#endregion
//#region src/utils/transform/utils.ts
const cache$1 = /* @__PURE__ */ new WeakMap();
/**
* Load module
*/
function loadModule(context, name) {
	const key = getSourceCode(context).ast;
	let modules = cache$1.get(key);
	if (!modules) {
		modules = {};
		cache$1.set(key, modules);
	}
	const mod = modules[name];
	if (mod) return mod;
	try {
		const cwd = getCwd(context);
		const relativeTo = node_path.default.join(cwd, "__placeholder__.js");
		return modules[name] = node_module.default.createRequire(relativeTo)(name);
	} catch {
		return null;
	}
}
/** Get content range */
function getContentRange(node) {
	if (node.closingElement) return [node.openingElement.range[1], node.closingElement.range[0]];
	return [node.openingElement.range[1], node.range[1]];
}
//#endregion
//#region src/utils/transform/postcss.ts
/**
* Transform with postcss
*/
function transform$3(node, context) {
	const postcssLoadConfig = loadPostcssLoadConfig(context);
	if (!postcssLoadConfig) return null;
	const inputRange = getContentRange(node);
	const code = getSourceCode(context).text.slice(...inputRange);
	const filename = `${getFilename(context)}.css`;
	try {
		const config = postcssLoadConfig.sync({
			cwd: getCwd(context) ?? process.cwd(),
			from: filename
		});
		const result = (0, postcss.default)(config.plugins).process(code, {
			...config.options,
			map: { inline: false }
		});
		return {
			inputRange,
			output: result.content,
			mappings: result.map.toJSON().mappings
		};
	} catch {
		return null;
	}
}
/**
* Load postcss-load-config
*/
function loadPostcssLoadConfig(context) {
	return loadModule(context, "postcss-load-config");
}
//#endregion
//#region src/utils/transform/sass.ts
/**
* Transpile with sass
*/
function transform$2(node, context, type) {
	const sass = loadSass(context);
	if (!sass) return null;
	const inputRange = getContentRange(node);
	const code = getSourceCode(context).text.slice(...inputRange);
	try {
		const output = sass.compileString(code, {
			sourceMap: true,
			syntax: type === "sass" ? "indented" : void 0
		});
		if (!output) return null;
		return {
			inputRange,
			output: output.css,
			mappings: output.sourceMap.mappings
		};
	} catch {
		return null;
	}
}
/**
* Load sass
*/
function loadSass(context) {
	return loadModule(context, "sass");
}
//#endregion
//#region src/utils/transform/less.ts
/**
* Transpile with less
*/
function transform$1(node, context) {
	const less = loadLess(context);
	if (!less) return null;
	const inputRange = getContentRange(node);
	const code = getSourceCode(context).text.slice(...inputRange);
	const filename = `${getFilename(context)}.less`;
	try {
		let output;
		less.render(code, {
			sourceMap: {},
			syncImport: true,
			filename,
			lint: false
		}, (_error, result) => {
			output = result;
		});
		if (!output) return null;
		return {
			inputRange,
			output: output.css,
			mappings: JSON.parse(output.map).mappings
		};
	} catch {
		return null;
	}
}
/**
* Load less
*/
function loadLess(context) {
	return loadModule(context, "less");
}
//#endregion
//#region src/utils/transform/stylus.ts
/**
* Transpile with stylus
*/
function transform(node, context) {
	const stylus = loadStylus(context);
	if (!stylus) return null;
	const inputRange = getContentRange(node);
	const code = getSourceCode(context).text.slice(...inputRange);
	const filename = `${getFilename(context)}.stylus`;
	try {
		let output;
		const style = stylus(code, { filename }).set("sourcemap", {});
		style.render((_error, outputCode) => {
			output = outputCode;
		});
		if (output == null) return null;
		return {
			inputRange,
			output,
			mappings: style.sourcemap.mappings
		};
	} catch {
		return null;
	}
}
/**
* Load stylus
*/
function loadStylus(context) {
	return loadModule(context, "stylus");
}
//#endregion
//#region src/utils/transform/lines-and-columns.ts
var LinesAndColumns = class {
	lineStartIndices;
	code;
	constructor(code) {
		const len = code.length;
		const lineStartIndices = [0];
		for (let index = 0; index < len; index++) {
			const c = code[index];
			if (c === "\r") {
				if ((code[index + 1] || "") === "\n") index++;
				lineStartIndices.push(index + 1);
			} else if (c === "\n") lineStartIndices.push(index + 1);
		}
		this.code = code;
		this.lineStartIndices = lineStartIndices;
	}
	getLocFromIndex(index) {
		const lineNumber = sortedLastIndex$1(this.lineStartIndices, index);
		return {
			line: lineNumber,
			column: index - this.lineStartIndices[lineNumber - 1]
		};
	}
	getIndexFromLoc(loc) {
		const lineIndex = loc.line - 1;
		if (this.lineStartIndices.length > lineIndex) return this.lineStartIndices[lineIndex] + loc.column;
		else if (this.lineStartIndices.length === lineIndex) return this.code.length + loc.column;
		return this.code.length + loc.column;
	}
};
/**
* Uses a binary search to determine the highest index at which value should be inserted into array in order to maintain its sort order.
*/
function sortedLastIndex$1(array, value) {
	let lower = 0;
	let upper = array.length;
	while (lower < upper) {
		const mid = Math.floor(lower + (upper - lower) / 2);
		const target = array[mid];
		if (target < value) lower = mid + 1;
		else if (target > value) upper = mid;
		else return mid + 1;
	}
	return upper;
}
//#endregion
//#region src/utils/transform/index.ts
const cache = /* @__PURE__ */ new WeakMap();
/** Get style content css */
function getStyleContentCSS(node, context) {
	const cachedResult = cache.get(node);
	if (cachedResult) return cachedResult;
	const sourceCode = getSourceCode(context);
	const langNode = findAttribute(node, "lang");
	const lang = langNode && getStaticAttributeStringValue(langNode);
	if (!langNode || lang === "css") {
		const inputRange = getContentRange(node);
		return {
			css: sourceCode.text.slice(...inputRange),
			remap: (i) => inputRange[0] + i
		};
	}
	let transform$4 = null;
	if (lang === "postcss") transform$4 = transform$3(node, context);
	else if (lang === "scss" || lang === "sass") transform$4 = transform$2(node, context, lang);
	else if (lang === "less") transform$4 = transform$1(node, context);
	else if (lang === "styl" || lang === "stylus") transform$4 = transform(node, context);
	if (!transform$4) return null;
	const result = transformToStyleContentCSS(transform$4, context);
	cache.set(node, result);
	return result;
}
/** TransformResult to style content css */
function transformToStyleContentCSS(transform, context) {
	const sourceCode = getSourceCode(context);
	let outputLocs = null;
	let inputLocs = null;
	let decoded = null;
	return {
		css: transform.output,
		remap: (index) => {
			outputLocs = outputLocs ?? new LinesAndColumns(transform.output);
			inputLocs = inputLocs ?? new LinesAndColumns(sourceCode.text.slice(...transform.inputRange));
			const inputCodePos = remapPosition(outputLocs.getLocFromIndex(index));
			return inputLocs.getIndexFromLoc(inputCodePos) + transform.inputRange[0];
		}
	};
	/** Remapping source position */
	function remapPosition(pos) {
		decoded = decoded ?? (0, _jridgewell_sourcemap_codec.decode)(transform.mappings);
		const lineMaps = decoded[pos.line - 1];
		if (!lineMaps?.length) {
			for (let line = pos.line - 1; line >= 0; line--) {
				const prevLineMaps = decoded[line];
				if (prevLineMaps?.length) {
					const [, , sourceCodeLine, sourceCodeColumn] = prevLineMaps[prevLineMaps.length - 1];
					return {
						line: sourceCodeLine + 1,
						column: sourceCodeColumn
					};
				}
			}
			return {
				line: -1,
				column: -1
			};
		}
		for (let index = 0; index < lineMaps.length - 1; index++) {
			const [generateCodeColumn, , sourceCodeLine, sourceCodeColumn] = lineMaps[index];
			if (generateCodeColumn <= pos.column && pos.column < lineMaps[index + 1][0]) return {
				line: sourceCodeLine + 1,
				column: sourceCodeColumn + (pos.column - generateCodeColumn)
			};
		}
		const [generateCodeColumn, , sourceCodeLine, sourceCodeColumn] = lineMaps[lineMaps.length - 1];
		return {
			line: sourceCodeLine + 1,
			column: sourceCodeColumn + (pos.column - generateCodeColumn)
		};
	}
}
//#endregion
//#region src/rules/no-unused-css-selector.ts
var no_unused_css_selector_default = createRule("no-unused-css-selector", {
	meta: {
		docs: {
			description: "disallow selectors defined in `style` tag that don't use in HTML",
			category: "Best Practices",
			recommended: false
		},
		schema: [],
		messages: { unused: "Unused CSS selector `{{selector}}`" },
		type: "problem"
	},
	create(context) {
		const sourceCode = getSourceCode(context);
		if (!sourceCode.parserServices?.isAstro) return {};
		const styles = [];
		const rootTree = {
			parent: null,
			node: null,
			childElements: []
		};
		const allTreeElements = [];
		let currTree = rootTree;
		/** Verify for CSS */
		function verifyCSS(css) {
			let root;
			try {
				root = postcss.default.parse(css.css);
			} catch {
				return;
			}
			const ignoreNodes = /* @__PURE__ */ new Set();
			root.walk((psNode) => {
				if (psNode.parent && ignoreNodes.has(psNode.parent)) {
					ignoreNodes.add(psNode);
					return;
				}
				if (psNode.type !== "rule") {
					if (psNode.type === "atrule") {
						if (psNode.name === "keyframes") ignoreNodes.add(psNode);
					}
					return;
				}
				const rule = psNode;
				const raws = rule.raws;
				const rawSelectorText = raws.selector ? raws.selector.raw : rule.selector;
				for (const selector of parseSelector(rawSelectorText, context)) {
					if (selector.error) continue;
					if (allTreeElements.some((tree) => selector.test(tree))) continue;
					reportSelector(rule.source.start.offset + selector.offset, selector.selector);
				}
			});
			/** Report selector */
			function reportSelector(start, selector) {
				const remapStart = css.remap(start);
				const remapEnd = css.remap(start + selector.length);
				context.report({
					loc: {
						start: sourceCode.getLocFromIndex(remapStart),
						end: sourceCode.getLocFromIndex(remapEnd)
					},
					messageId: "unused",
					data: { selector }
				});
			}
		}
		return {
			JSXElement(node) {
				const name = getElementName(node);
				if (name === "Fragment" || name === "slot") return;
				if (name === "style" && !findAttribute(node, "is:global")) styles.push(node);
				const tree = {
					parent: currTree,
					node,
					childElements: []
				};
				allTreeElements.unshift(tree);
				currTree.childElements.push(tree);
				currTree = tree;
			},
			"JSXElement:exit"(node) {
				if (currTree.node === node) {
					if (currTree.node) {
						const expressions = currTree.node.children.filter((e) => e.type === "JSXExpressionContainer");
						if (expressions.length) for (const child of currTree.childElements) child.withinExpression = expressions.some((e) => e.range[0] <= child.node.range[0] && child.node.range[1] <= e.range[1]);
					}
					currTree = currTree.parent;
				}
			},
			"Program:exit"() {
				for (const style of styles) {
					const css = getStyleContentCSS(style, context);
					if (css) verifyCSS(css);
				}
			}
		};
	}
});
var SelectorError = class extends Error {};
/**
* Parses CSS selectors and returns an object with a function that tests JSXElement.
*/
function parseSelector(selector, context) {
	let astSelector;
	try {
		astSelector = (0, postcss_selector_parser.default)().astSync(selector);
	} catch (error) {
		return [{
			error,
			selector,
			offset: 0,
			test: () => false
		}];
	}
	return astSelector.nodes.map((sel) => {
		const nodes = removeGlobals(cleanSelectorChildren(sel));
		try {
			const test = selectorToJSXElementMatcher(nodes, context);
			return {
				selector: sel.toString().trim(),
				offset: sel.sourceIndex ?? sel.nodes[0].sourceIndex,
				test(element) {
					return test(element, null);
				}
			};
		} catch (error) {
			if (error instanceof SelectorError) return {
				error,
				selector: sel.toString().trim(),
				offset: sel.sourceIndex ?? sel.nodes[0].sourceIndex,
				test: () => false
			};
			throw error;
		}
	});
	/** Remove :global() on both sides */
	function removeGlobals(nodes) {
		let start = 0;
		let end = nodes.length;
		while (nodes[end - 1] && isGlobalPseudo(nodes[end - 1])) {
			end--;
			if (nodes[end - 1]?.type === "combinator") end--;
		}
		while (nodes[start] && isGlobalPseudo(nodes[start])) {
			start++;
			if (nodes[start]?.type === "combinator") start++;
		}
		if (nodes.some(isRootPseudo)) {
			while (nodes[start] && !isRootPseudo(nodes[start])) start++;
			start++;
			while (nodes[start] && nodes[start].type !== "combinator") start++;
			if (nodes[start]?.type === "combinator") start++;
		}
		return nodes.slice(start, end);
	}
}
/**
* Convert nodes to JSXElementMatcher
* @param {parser.Selector[]} selectorNodes
* @returns {JSXElementMatcher}
*/
function selectorsToJSXElementMatcher(selectorNodes, context) {
	const selectors = selectorNodes.map((n) => selectorToJSXElementMatcher(cleanSelectorChildren(n), context));
	return (element, subject) => selectors.some((sel) => sel(element, subject));
}
/**
* @param {parser.Node|null} node
* @returns {node is parser.Combinator}
*/
function isDescendantCombinator(node) {
	return Boolean(node && node.type === "combinator" && !node.value.trim());
}
/**
* Clean and get the selector child nodes.
* @param {parser.Selector} selector
* @returns {ChildNode[]}
*/
function cleanSelectorChildren(selector) {
	const nodes = [];
	let last = null;
	for (const node of selector.nodes) {
		if (node.type === "root") throw new SelectorError("Unexpected state type=root");
		if (node.type === "comment") continue;
		if ((last == null || last.type === "combinator") && isDescendantCombinator(node)) continue;
		if (isDescendantCombinator(last) && node.type === "combinator") nodes.pop();
		nodes.push(node);
		last = node;
	}
	if (isDescendantCombinator(last)) nodes.pop();
	return nodes;
}
/**
* Convert Selector child nodes to JSXElementMatcher
* @param {ChildNode[]} selectorChildren
* @returns {JSXElementMatcher}
*/
function selectorToJSXElementMatcher(selectorChildren, context) {
	const nodes = [...selectorChildren];
	let node = nodes.shift();
	let result = null;
	while (node) {
		if (node.type === "combinator") {
			const combinator = node.value;
			node = nodes.shift();
			if (!node) throw new SelectorError(`Expected selector after '${combinator}'.`);
			if (node.type === "combinator") throw new SelectorError(`Unexpected combinator '${node.value}'.`);
			const right = nodeToJSXElementMatcher(node, context);
			result = combination(result || ((element, subject) => element === subject), combinator, right);
		} else {
			const sel = nodeToJSXElementMatcher(node, context);
			result = result ? compound(result, sel) : sel;
		}
		node = nodes.shift();
	}
	if (!result) return () => true;
	return result;
}
/**
* @param {JSXElementMatcher} left
* @param {string} combinator
* @param {JSXElementMatcher} right
* @returns {JSXElementMatcher}
*/
function combination(left, combinator, right) {
	switch (combinator.trim()) {
		case "": return (element, subject) => {
			if (right(element, null)) {
				let parent = element.parent;
				while (parent.node) {
					if (left(parent, subject)) return true;
					parent = parent.parent;
				}
			}
			return false;
		};
		case ">": return (element, subject) => {
			if (right(element, null)) {
				const parent = element.parent;
				if (parent.node) return left(parent, subject);
			}
			return false;
		};
		case "+": return (element, subject) => {
			if (right(element, null)) {
				const before = getBeforeElement(element);
				if (before) return left(before, subject);
			}
			return false;
		};
		case "~": return (element, subject) => {
			if (right(element, null)) {
				for (const before of getBeforeElements(element)) if (left(before, subject)) return true;
			}
			return false;
		};
		default: throw new SelectorError(`Unknown combinator: ${combinator}.`);
	}
}
/**
* Convert node to JSXElementMatcher
* @param {Exclude<parser.Node, {type:'combinator'|'comment'|'root'|'selector'}>} selector
* @returns {JSXElementMatcher}
*/
function nodeToJSXElementMatcher(selector, context) {
	const baseMatcher = (() => {
		switch (selector.type) {
			case "attribute": return attributeNodeToJSXElementMatcher(selector, context);
			case "class": return classNameNodeToJSXElementMatcher(selector, context);
			case "id": return identifierNodeToJSXElementMatcher(selector, context);
			case "tag": return tagNodeToJSXElementMatcher(selector);
			case "universal": return universalNodeToJSXElementMatcher(selector);
			case "pseudo": return pseudoNodeToJSXElementMatcher(selector, context);
			case "nesting": throw new SelectorError("Unsupported nesting selector.");
			case "string": throw new SelectorError(`Unknown selector: ${selector.value}.`);
			default: throw new SelectorError(`Unknown selector: ${selector.value}.`);
		}
	})();
	return (element, subject) => {
		if (isComponentElement(element)) return false;
		return baseMatcher(element, subject);
	};
}
/**
* Convert Attribute node to JSXElementMatcher
* @param {parser.Attribute} selector
* @returns {JSXElementMatcher}
*/
function attributeNodeToJSXElementMatcher(selector, context) {
	const key = selector.attribute;
	if (!selector.operator) return (element, _) => {
		return hasAttribute(element, key, context);
	};
	const value = selector.value || "";
	switch (selector.operator) {
		case "=": return buildJSXElementMatcher(value, (attr, val) => attr === val);
		case "~=": return buildJSXElementMatcher(value, (attr, val) => attr.split(/\s+/u).includes(val));
		case "|=": return buildJSXElementMatcher(value, (attr, val) => attr === val || attr.startsWith(`${val}-`));
		case "^=": return buildJSXElementMatcher(value, (attr, val) => attr.startsWith(val));
		case "$=": return buildJSXElementMatcher(value, (attr, val) => attr.endsWith(val));
		case "*=": return buildJSXElementMatcher(value, (attr, val) => attr.includes(val));
		default: throw new SelectorError(`Unsupported operator: ${selector.operator}.`);
	}
	/**
	* @param {string} selectorValue
	* @param {(attrValue:string, selectorValue: string)=>boolean} test
	* @returns {JSXElementMatcher}
	*/
	function buildJSXElementMatcher(selectorValue, test) {
		const val = selector.insensitive ? selectorValue.toLowerCase() : selectorValue;
		return (element) => {
			const attr = getAttribute(element, key, context);
			if (attr == null) return false;
			if (attr.unknown || !attr.staticValue) return true;
			const attrValue = attr.staticValue.value;
			return test(selector.insensitive ? attrValue.toLowerCase() : attrValue, val);
		};
	}
}
/**
* Convert ClassName node to JSXElementMatcher
* @param {parser.ClassName} selector
* @returns {JSXElementMatcher}
*/
function classNameNodeToJSXElementMatcher(selector, context) {
	const className = selector.value;
	return (element) => {
		const attr = getAttribute(element, "class", context);
		if (attr == null) return false;
		if (attr.unknown || !attr.staticValue) return true;
		return attr.staticValue.value.split(/\s+/u).includes(className);
	};
}
/**
* Convert Identifier node to JSXElementMatcher
* @param {parser.Identifier} selector
* @returns {JSXElementMatcher}
*/
function identifierNodeToJSXElementMatcher(selector, context) {
	const id = selector.value;
	return (element) => {
		const attr = getAttribute(element, "id", context);
		if (attr == null) return false;
		if (attr.unknown || !attr.staticValue) return true;
		return attr.staticValue.value === id;
	};
}
/**
* Convert Tag node to JSXElementMatcher
* @param {parser.Tag} selector
* @returns {JSXElementMatcher}
*/
function tagNodeToJSXElementMatcher(selector) {
	const name = selector.value;
	return (element) => {
		return getElementName(element.node) === name;
	};
}
/**
* Convert Universal node to JSXElementMatcher
* @param {parser.Universal} _selector
* @returns {JSXElementMatcher}
*/
function universalNodeToJSXElementMatcher(_selector) {
	return () => true;
}
/**
* Convert Pseudo node to JSXElementMatcher
* @param {parser.Pseudo} selector
* @returns {JSXElementMatcher}
*/
function pseudoNodeToJSXElementMatcher(selector, context) {
	switch (selector.value) {
		case ":is":
		case ":where": return selectorsToJSXElementMatcher(selector.nodes, context);
		case ":has": return pseudoHasSelectorsToJSXElementMatcher(selector.nodes, context);
		case ":empty": return (element) => element.node.children.every((child) => child.type === "JSXText" && !child.value.trim() || child.type === "AstroHTMLComment");
		case ":global": return () => true;
		default: return () => true;
	}
}
/**
* Convert :has() selector nodes to JSXElementMatcher
* @param {parser.Selector[]} selectorNodes
* @returns {JSXElementMatcher}
*/
function pseudoHasSelectorsToJSXElementMatcher(selectorNodes, context) {
	const selectors = selectorNodes.map((n) => pseudoHasSelectorToJSXElementMatcher(n, context));
	return (element, subject) => selectors.some((sel) => sel(element, subject));
}
/**
* Convert :has() selector node to JSXElementMatcher
* @param {parser.Selector} selector
* @returns {JSXElementMatcher}
*/
function pseudoHasSelectorToJSXElementMatcher(selector, context) {
	const nodes = cleanSelectorChildren(selector);
	const selectors = selectorToJSXElementMatcher(nodes, context);
	const firstNode = nodes[0];
	if (firstNode.type === "combinator" && (firstNode.value === "+" || firstNode.value === "~")) return buildJSXElementMatcher((element) => getAfterElements(element));
	return buildJSXElementMatcher((element) => element.childElements);
	/**
	* @param {(element: JSXElementTreeNode) => JSXElementTreeNode[]} getStartElements
	* @returns {JSXElementMatcher}
	*/
	function buildJSXElementMatcher(getStartElements) {
		return (element) => {
			const elements = [...getStartElements(element)];
			let curr;
			while (curr = elements.shift()) {
				const el = curr;
				if (selectors(el, element)) return true;
				elements.push(...el.childElements);
			}
			return false;
		};
	}
}
/**
* @param {JSXElementTreeNode} element
*/
function getBeforeElement(element) {
	return getBeforeElements(element).pop() || null;
}
/**
* @param {JSXElementTreeNode} element
*/
function getBeforeElements(element) {
	const parent = element.parent;
	if (!parent) return [];
	const index = parent.childElements.indexOf(element);
	return parent.childElements.slice(0, element.withinExpression ? index + 1 : index);
}
/**
* @param {JSXElementTreeNode} element
*/
function getAfterElements(element) {
	const parent = element.parent;
	if (!parent) return [];
	const index = parent.childElements.indexOf(element);
	return parent.childElements.slice(element.withinExpression ? index : index + 1);
}
/**
* @param {JSXElementMatcher} a
* @param {JSXElementMatcher} b
* @returns {JSXElementMatcher}
*/
function compound(a, b) {
	return (element, subject) => a(element, subject) && b(element, subject);
}
/**
* Checks whether the given element is component.
*/
function isComponentElement(element) {
	const elementName = getElementName(element.node);
	return elementName == null || elementName.toLowerCase() !== elementName;
}
/**
* Checks whether the given node is :global.
*/
function isGlobalPseudo(node) {
	return node.type === "pseudo" && node.value === ":global";
}
/**
* Checks whether the given node is :root.
*/
function isRootPseudo(node) {
	return node.type === "pseudo" && node.value === ":root";
}
/**
* Checks whether the given element has the given attribute.
* @param {JSXElementTreeNode} element The element node.
* @param {string} attribute The attribute name.
*/
function hasAttribute(element, attribute, context) {
	if (getAttribute(element, attribute, context)) return true;
	return false;
}
/**
* Get attribute from given element.
* @param {JSXElementTreeNode} element The element node.
* @param {string} attribute The attribute name.
*/
function getAttribute(element, attribute, context) {
	const attr = findAttribute(element.node, attribute);
	if (attr) {
		if (attr.value == null) return {
			unknown: false,
			hasAttr: true,
			staticValue: { value: "" }
		};
		const value = getStaticAttributeStringValue(attr, context);
		if (value == null) return {
			unknown: false,
			hasAttr: true,
			staticValue: null
		};
		return {
			unknown: false,
			hasAttr: true,
			staticValue: { value }
		};
	}
	if (attribute === "class") {
		const result = getClassListAttribute(element, context);
		if (result) return result;
	}
	if (getSpreadAttributes(element.node).length === 0) return null;
	return { unknown: true };
}
/**
* Get class:list attribute from given element.
* @param {JSXElementTreeNode} element The element node.
*/
function getClassListAttribute(element, context) {
	const attr = findAttribute(element.node, "class:list");
	if (attr) {
		if (attr.value == null) return {
			unknown: false,
			hasAttr: true,
			staticValue: { value: "" }
		};
		const classList = extractClassList(attr, context);
		if (classList === null) return {
			unknown: false,
			hasAttr: true,
			staticValue: null
		};
		return {
			unknown: false,
			hasAttr: true,
			staticValue: { value: classList.classList.join(" ") }
		};
	}
	return null;
}
/** Extract class:list class names */
function extractClassList(node, context) {
	if (node.value?.type === _typescript_eslint_types.AST_NODE_TYPES.Literal) return { classList: [String(node.value.value)] };
	if (node.value?.type === "JSXExpressionContainer" && node.value.expression.type !== "JSXEmptyExpression") {
		const classList = [];
		for (const className of extractClassListFromExpression(node.value.expression, context)) {
			if (className == null) return null;
			classList.push(className);
		}
		return { classList };
	}
	return null;
}
/** Extract class:list class names */
function* extractClassListFromExpression(node, context) {
	if (node.type === _typescript_eslint_types.AST_NODE_TYPES.ArrayExpression) {
		for (const element of node.elements) {
			if (element == null) continue;
			if (element.type === _typescript_eslint_types.AST_NODE_TYPES.SpreadElement) yield* extractClassListFromExpression(element.argument, context);
			else yield* extractClassListFromExpression(element, context);
		}
		return;
	}
	if (node.type === _typescript_eslint_types.AST_NODE_TYPES.ObjectExpression) {
		for (const prop of node.properties) if (prop.type === _typescript_eslint_types.AST_NODE_TYPES.SpreadElement) yield* extractClassListFromExpression(prop.argument, context);
		else if (!prop.computed) if (prop.key.type === _typescript_eslint_types.AST_NODE_TYPES.Literal) yield String(prop.key.value);
		else yield prop.key.name;
		else yield* extractClassListFromExpression(prop.key, context);
		return;
	}
	const staticValue = (0, _eslint_community_eslint_utils.getStaticValue)(node, getSourceCode(context).scopeManager.globalScope);
	if (staticValue) {
		yield* extractClassListFromUnknown(staticValue.value);
		return;
	}
	yield null;
}
/** Extract class:list class names */
function* extractClassListFromUnknown(value) {
	if (!value) return;
	if (Array.isArray(value)) {
		for (const e of value) yield* extractClassListFromUnknown(e);
		return;
	}
	if (typeof value === "object") {
		yield* Object.keys(value);
		return;
	}
	yield String(value);
}
//#endregion
//#region src/utils/style/tokenizer.ts
const EOF = -1;
const NULL = 0;
const TABULATION = 9;
const CARRIAGE_RETURN = 13;
const LINE_FEED = 10;
const FORM_FEED = 12;
const SPACE = 32;
const QUOTATION_MARK = 34;
const APOSTROPHE = 39;
const LEFT_PARENTHESIS = 40;
const RIGHT_PARENTHESIS = 41;
const ASTERISK = 42;
const COMMA = 44;
const SOLIDUS = 47;
const COLON = 58;
const SEMICOLON = 59;
const LEFT_SQUARE_BRACKET = 91;
const REVERSE_SOLIDUS = 92;
const RIGHT_SQUARE_BRACKET = 93;
const LEFT_CURLY_BRACKET = 123;
const RIGHT_CURLY_BRACKET = 125;
/**
* Check whether the code point is a whitespace.
* @param cp The code point to check.
* @returns `true` if the code point is a whitespace.
*/
function isWhitespace(cp) {
	return cp === TABULATION || cp === LINE_FEED || cp === FORM_FEED || cp === CARRIAGE_RETURN || cp === SPACE;
}
let CSSTokenType = /* @__PURE__ */ function(CSSTokenType) {
	CSSTokenType["quoted"] = "Quoted";
	CSSTokenType["block"] = "Block";
	CSSTokenType["line"] = "Line";
	CSSTokenType["word"] = "Word";
	CSSTokenType["punctuator"] = "Punctuator";
	return CSSTokenType;
}({});
/**
* A simplified CSS tokenizer.
* The tokenizer is implemented with reference to the CSS specification,
* but it does not follow it. This tokenizer only does the tokenization needed to properly handle `v-bind()`.
* @see https://drafts.csswg.org/css-syntax/#tokenization
*/
var CSSTokenizer = class {
	text;
	options;
	cp;
	offset;
	nextOffset;
	reconsuming;
	/**
	* Initialize this tokenizer.
	* @param text The source code to tokenize.
	* @param options The tokenizer options.
	*/
	constructor(text, startOffset, options) {
		this.text = text;
		this.options = { inlineComment: options?.inlineComment ?? false };
		this.cp = NULL;
		this.offset = startOffset - 1;
		this.nextOffset = startOffset;
		this.reconsuming = false;
	}
	/**
	* Get the next token.
	* @returns The next token or null.
	*/
	nextToken() {
		let cp;
		if (this.reconsuming) {
			cp = this.cp;
			this.reconsuming = false;
		} else cp = this.consumeNextCodePoint();
		while (isWhitespace(cp)) cp = this.consumeNextCodePoint();
		if (cp === EOF) return null;
		const start = this.offset;
		return this.consumeNextToken(cp, start);
	}
	/**
	* Get the next code point.
	* @returns The code point.
	*/
	nextCodePoint() {
		if (this.nextOffset >= this.text.length) return EOF;
		return this.text.codePointAt(this.nextOffset);
	}
	/**
	* Consume the next code point.
	* @returns The consumed code point.
	*/
	consumeNextCodePoint() {
		if (this.offset >= this.text.length) {
			this.cp = EOF;
			return EOF;
		}
		this.offset = this.nextOffset;
		if (this.offset >= this.text.length) {
			this.cp = EOF;
			return EOF;
		}
		let cp = this.text.codePointAt(this.offset);
		if (cp === CARRIAGE_RETURN) {
			this.nextOffset = this.offset + 1;
			if (this.text.codePointAt(this.nextOffset) === LINE_FEED) this.nextOffset++;
			cp = LINE_FEED;
		} else this.nextOffset = this.offset + (cp >= 65536 ? 2 : 1);
		this.cp = cp;
		return cp;
	}
	consumeNextToken(cp, start) {
		if (cp === SOLIDUS) {
			const nextCp = this.nextCodePoint();
			if (nextCp === ASTERISK) return this.consumeComment(start);
			if (nextCp === SOLIDUS && this.options.inlineComment) return this.consumeInlineComment(start);
		}
		if (isQuote(cp)) return this.consumeString(start, cp);
		if (isPunctuator(cp)) return {
			type: CSSTokenType.punctuator,
			range: [start, start + 1],
			value: String.fromCodePoint(cp)
		};
		return this.consumeWord(start);
	}
	/**
	* Consume word
	*/
	consumeWord(start) {
		let cp = this.consumeNextCodePoint();
		while (!isWhitespace(cp) && !isPunctuator(cp) && !isQuote(cp)) cp = this.consumeNextCodePoint();
		this.reconsuming = true;
		const range = [start, this.offset];
		const text = this.text;
		let value;
		return {
			type: CSSTokenType.word,
			range,
			get value() {
				return value ?? (value = text.slice(...range));
			}
		};
	}
	/**
	* https://drafts.csswg.org/css-syntax/#consume-string-token
	*/
	consumeString(start, quote) {
		let valueEndOffset = null;
		let cp = this.consumeNextCodePoint();
		while (cp !== EOF) {
			if (cp === quote) {
				valueEndOffset = this.offset;
				break;
			}
			if (cp === REVERSE_SOLIDUS) this.consumeNextCodePoint();
			cp = this.consumeNextCodePoint();
		}
		const text = this.text;
		let value;
		const valueRange = [start + 1, valueEndOffset ?? this.nextOffset];
		return {
			type: CSSTokenType.quoted,
			range: [start, this.nextOffset],
			valueRange,
			get value() {
				return value ?? (value = text.slice(...valueRange));
			},
			quote: String.fromCodePoint(quote)
		};
	}
	/**
	* https://drafts.csswg.org/css-syntax/#consume-comment
	*/
	consumeComment(start) {
		this.consumeNextCodePoint();
		let valueEndOffset = null;
		let cp = this.consumeNextCodePoint();
		while (cp !== EOF) {
			if (cp === ASTERISK) {
				cp = this.consumeNextCodePoint();
				if (cp === SOLIDUS) {
					valueEndOffset = this.offset - 1;
					break;
				}
			}
			cp = this.consumeNextCodePoint();
		}
		const valueRange = [start + 2, valueEndOffset ?? this.nextOffset];
		const text = this.text;
		let value;
		return {
			type: CSSTokenType.block,
			range: [start, this.nextOffset],
			valueRange,
			get value() {
				return value ?? (value = text.slice(...valueRange));
			}
		};
	}
	/**
	* Consume inline comment
	*/
	consumeInlineComment(start) {
		this.consumeNextCodePoint();
		let valueEndOffset = null;
		let cp = this.consumeNextCodePoint();
		while (cp !== EOF) {
			if (cp === LINE_FEED) {
				valueEndOffset = this.offset - 1;
				break;
			}
			cp = this.consumeNextCodePoint();
		}
		const valueRange = [start + 2, valueEndOffset ?? this.nextOffset];
		const text = this.text;
		let value;
		return {
			type: CSSTokenType.line,
			range: [start, this.nextOffset],
			valueRange,
			get value() {
				return value ?? (value = text.slice(...valueRange));
			}
		};
	}
};
/** Checks whether given code point is punctuator */
function isPunctuator(cp) {
	return cp === COLON || cp === SEMICOLON || cp === COMMA || cp === LEFT_PARENTHESIS || cp === RIGHT_PARENTHESIS || cp === LEFT_CURLY_BRACKET || cp === RIGHT_CURLY_BRACKET || cp === LEFT_SQUARE_BRACKET || cp === RIGHT_SQUARE_BRACKET || cp === SOLIDUS || cp === ASTERISK;
}
/** Checks whether given code point is quotes */
function isQuote(cp) {
	return cp === APOSTROPHE || cp === QUOTATION_MARK;
}
//#endregion
//#region src/utils/style/index.ts
var CSSTokenScanner = class {
	reconsuming = [];
	tokenizer;
	constructor(text, options) {
		this.tokenizer = new CSSTokenizer(text, 0, options);
	}
	nextToken() {
		return this.reconsuming.shift() || this.tokenizer.nextToken();
	}
	reconsume(...tokens) {
		this.reconsuming.push(...tokens);
	}
};
/**
* Iterate the CSS variables.
*/
function* iterateCSSVars(code, cssOptions) {
	const tokenizer = new CSSTokenScanner(code, cssOptions);
	let token;
	while (token = tokenizer.nextToken()) if (token.type === CSSTokenType.word || token.value.startsWith("--")) yield token.value;
}
//#endregion
//#region src/rules/no-unused-define-vars-in-style.ts
var no_unused_define_vars_in_style_default = createRule("no-unused-define-vars-in-style", {
	meta: {
		docs: {
			description: "disallow unused `define:vars={...}` in `style` tag",
			category: "Possible Errors",
			recommended: true
		},
		schema: [],
		messages: { unused: "'{{varName}}' is defined but never used." },
		type: "problem"
	},
	create(context) {
		const sourceCode = getSourceCode(context);
		if (!sourceCode.parserServices?.isAstro) return {};
		return { "JSXElement > JSXOpeningElement[name.type='JSXIdentifier'][name.name='style']"(node) {
			const defineVars = node.attributes.find((attr) => getAttributeName(attr) === "define:vars");
			if (!defineVars) return;
			if (!defineVars.value || defineVars.value.type !== _typescript_eslint_types.AST_NODE_TYPES.JSXExpressionContainer || defineVars.value.expression.type !== _typescript_eslint_types.AST_NODE_TYPES.ObjectExpression) return;
			if (node.parent.children.length !== 1) return;
			const textNode = node.parent.children[0];
			if (!textNode || textNode.type !== "AstroRawText") return;
			const definedVars = defineVars.value.expression.properties.filter((prop) => prop.type === _typescript_eslint_types.AST_NODE_TYPES.Property).map((prop) => ({
				prop,
				name: (0, _eslint_community_eslint_utils.getPropertyName)(prop, sourceCode.getScope(node))
			})).filter((data) => Boolean(data.name));
			if (!definedVars.length) return;
			const lang = node.attributes.find((attr) => getAttributeName(attr) === "lang");
			const langValue = lang && lang.value && lang.value.type === _typescript_eslint_types.AST_NODE_TYPES.Literal && lang.value.value;
			let unusedDefinedVars = [...definedVars];
			for (const cssVar of iterateCSSVars(textNode.value, { inlineComment: Boolean(langValue) && langValue !== "css" })) {
				const variable = cssVar.slice(2);
				unusedDefinedVars = unusedDefinedVars.filter((v) => v.name !== variable);
			}
			for (const unused of unusedDefinedVars) context.report({
				node: unused.prop.key,
				messageId: "unused",
				data: { varName: unused.name }
			});
		} };
	}
});
//#endregion
//#region src/rules/prefer-class-list-directive.ts
var prefer_class_list_directive_default = createRule("prefer-class-list-directive", {
	meta: {
		docs: {
			description: "require `class:list` directives instead of `class` with expressions",
			category: "Stylistic Issues",
			recommended: false
		},
		schema: [],
		messages: { unexpected: "Unexpected `class` using expression. Use 'class:list' instead." },
		fixable: "code",
		type: "suggestion"
	},
	create(context) {
		if (!getSourceCode(context).parserServices?.isAstro) return {};
		/** Verify */
		function verifyAttr(attr) {
			if (getAttributeName(attr) !== "class") return;
			if (!attr.value || attr.value.type !== "JSXExpressionContainer" || attr.value.expression.type === "JSXEmptyExpression") return;
			context.report({
				node: attr.name,
				messageId: "unexpected",
				fix(fixer) {
					if (attr.type === "AstroShorthandAttribute") return fixer.insertTextBefore(attr, "class:list=");
					return fixer.insertTextAfter(attr.name, ":list");
				}
			});
		}
		return {
			JSXAttribute: verifyAttr,
			AstroTemplateLiteralAttribute: verifyAttr
		};
	}
});
//#endregion
//#region src/rules/prefer-object-class-list.ts
var prefer_object_class_list_default = createRule("prefer-object-class-list", {
	meta: {
		docs: {
			description: "require use object instead of ternary expression in `class:list`",
			category: "Stylistic Issues",
			recommended: false
		},
		schema: [],
		messages: { unexpected: "Unexpected class using the ternary operator." },
		fixable: "code",
		type: "suggestion"
	},
	create(context) {
		const sourceCode = getSourceCode(context);
		if (!sourceCode.parserServices?.isAstro) return {};
		class NewObjectProps {
			props = [];
			toObjectString() {
				return `{${this.toPropsString()}}`;
			}
			fixObject({ fixer, object }) {
				const closeBrace = sourceCode.getLastToken(object);
				const maybeComma = sourceCode.getTokenBefore(closeBrace);
				let text;
				if ((0, _eslint_community_eslint_utils.isCommaToken)(maybeComma)) text = this.toPropsString();
				else text = `,${this.toPropsString()}`;
				return fixer.insertTextAfterRange(maybeComma.range, text);
			}
			toPropsString() {
				return `${this.props.map(({ key, value }) => `${key}: ${value}`).join(", ")}`;
			}
		}
		/**
		* Returns a map of expressions and strings from ConditionalExpression.
		* Returns null if it has an unknown string.
		*/
		function parseConditionalExpression(node) {
			const result = /* @__PURE__ */ new Map();
			if (!processItems({ node: node.test }, node.consequent)) return null;
			if (!processItems({
				not: true,
				node: node.test
			}, node.alternate)) return null;
			return result;
			/** Process items */
			function processItems(key, e) {
				if (e.type === "ConditionalExpression") {
					const sub = parseConditionalExpression(e);
					if (sub == null) return false;
					for (const [expr, str] of sub) result.set({
						...key,
						chains: expr
					}, str);
				} else {
					const str = getStringIfConstant(e);
					if (str == null) return false;
					result.set(key, str);
				}
				return true;
			}
		}
		/**
		* Expr to string
		*/
		function exprToString({ node, not }) {
			let text = sourceCode.text.slice(...node.range);
			if (not) {
				if (node.type === "BinaryExpression") {
					if (node.operator === "===" || node.operator === "==" || node.operator === "!==" || node.operator === "!=") {
						const left = sourceCode.text.slice(...node.left.range);
						const op = sourceCode.text.slice(node.left.range[1], node.right.range[0]);
						const right = sourceCode.text.slice(...node.right.range);
						return `${left}${node.operator === "===" || node.operator === "==" ? op.replace(/[=](={1,2})/g, "!$1") : op.replace(/!(={1,2})/g, "=$1")}${right}`;
					}
				} else if (node.type === "UnaryExpression") {
					if (node.operator === "!" && node.prefix) return sourceCode.text.slice(...node.argument.range);
				}
				if (needParentheses(node, "not")) text = `(${text})`;
				text = `!${text}`;
			}
			return text;
		}
		/**
		* Returns all possible strings.
		*/
		function getStrings(node) {
			if (node.type === "TemplateElement") return node.value.cooked != null ? [node.value.cooked] : null;
			if (node.type === "ConditionalExpression") {
				const values = parseConditionalExpression(node);
				if (values == null) return null;
				return [...values.values()];
			}
			const str = getStringIfConstant(node);
			if (str == null) return null;
			return [str];
		}
		/**
		* Checks if the last character is a non word.
		*/
		function endsWithSpace(elements) {
			for (let i = elements.length - 1; i >= 0; i--) {
				const valueNode = elements[i];
				const strings = getStrings(valueNode);
				if (strings == null) {
					if (valueNode.type === _typescript_eslint_types.AST_NODE_TYPES.TemplateLiteral) {
						const quasiValue = valueNode.quasis[valueNode.quasis.length - 1].value.cooked;
						if (quasiValue && !quasiValue[quasiValue.length - 1].trim()) return true;
					}
					return false;
				}
				let hasEmpty = false;
				for (const str of strings) if (str) {
					if (str[str.length - 1].trim()) return false;
				} else hasEmpty = true;
				if (!hasEmpty) return true;
			}
			return null;
		}
		/**
		* Checks if the first character is a non word.
		*/
		function startsWithSpace(elements) {
			for (let i = 0; i < elements.length; i++) {
				const valueNode = elements[i];
				const strings = getStrings(valueNode);
				if (strings == null) {
					if (valueNode.type === _typescript_eslint_types.AST_NODE_TYPES.TemplateLiteral) {
						const quasiValue = valueNode.quasis[0].value.cooked;
						if (quasiValue && !quasiValue[0].trim()) return true;
					}
					return false;
				}
				let hasEmpty = false;
				for (const str of strings) if (str) {
					if (str[0].trim()) return false;
				} else hasEmpty = true;
				if (!hasEmpty) return true;
			}
			return null;
		}
		/** Report */
		function report(node, map, state) {
			context.report({
				node,
				messageId: "unexpected",
				*fix(fixer) {
					const classProps = new NewObjectProps();
					let beforeSpaces = "";
					let afterSpaces = "";
					for (const [expr, className] of map) {
						const trimmedClassName = className.trim();
						if (trimmedClassName) classProps.props.push({
							key: JSON.stringify(trimmedClassName),
							value: exprToString(expr)
						});
						else if (!classProps.props.length) beforeSpaces += className;
						else afterSpaces += className;
					}
					yield* state.fixExpression({
						newProps: classProps,
						beforeSpaces,
						afterSpaces,
						node,
						fixer
					});
				}
			});
		}
		/** Verify for ConditionalExpression */
		function verifyConditionalExpression(node, state) {
			const map = parseConditionalExpression(node);
			if (map == null) return;
			let canTransform = true;
			for (const className of map.values()) if (className) {
				if (className[0].trim() && state.beforeIsWord() || className[className.length - 1].trim() && state.afterIsWord()) {
					canTransform = false;
					break;
				}
			} else if (state.beforeIsWord() && state.afterIsWord()) {
				canTransform = false;
				break;
			}
			if (!canTransform) return;
			report(node, map, state);
		}
		/** Verify attr */
		function verifyAttr(attr) {
			if (getAttributeName(attr) !== "class:list") return;
			if (!attr.value || attr.value.type !== _typescript_eslint_types.AST_NODE_TYPES.JSXExpressionContainer || attr.value.expression.type === _typescript_eslint_types.AST_NODE_TYPES.JSXEmptyExpression) return;
			const expression = attr.value.expression;
			for (const element of extractElements(expression)) visitElementExpression(element.node, {
				beforeIsWord: () => false,
				afterIsWord: () => false,
				*fixArrayElement(data) {
					yield data.fixer.removeRange(getParenthesizedRange(data.node, sourceCode));
					if (!element.array) {
						let open, close;
						if (attr.type === "AstroTemplateLiteralAttribute") {
							open = "{[";
							close = "]}";
						} else {
							open = "[";
							close = "]";
						}
						yield data.fixer.insertTextBeforeRange(expression.range, open);
						yield data.fixer.insertTextAfterRange(expression.range, `,${data.newProps.toObjectString()}${close}`);
						return;
					}
					const object = findClosestObject(element.array, element.node);
					if (object) {
						yield data.newProps.fixObject({
							fixer: data.fixer,
							object
						});
						return;
					}
					const tokens = getParenthesizedTokens(element.node, sourceCode);
					const maybeComma = sourceCode.getTokenAfter(tokens.right);
					let insertOffset, text;
					if ((0, _eslint_community_eslint_utils.isCommaToken)(maybeComma)) {
						insertOffset = maybeComma.range[1];
						text = data.newProps.toObjectString();
					} else {
						insertOffset = tokens.right.range[1];
						text = `,${data.newProps.toObjectString()}`;
					}
					if (element.array.elements[element.array.elements.length - 1] !== element.node) text += ",";
					yield data.fixer.insertTextAfterRange([insertOffset, insertOffset], text);
				},
				*fixExpression(data) {
					if (element.array) {
						const object = findClosestObject(element.array, element.node);
						if (object) {
							yield data.fixer.removeRange(getParenthesizedRange(data.node, sourceCode));
							const tokens = getParenthesizedTokens(element.node, sourceCode);
							const maybeComma = sourceCode.getTokenAfter(tokens.right);
							if ((0, _eslint_community_eslint_utils.isCommaToken)(maybeComma)) yield data.fixer.removeRange(maybeComma.range);
							else {
								const maybeBeforeComma = sourceCode.getTokenBefore(tokens.left);
								if ((0, _eslint_community_eslint_utils.isCommaToken)(maybeBeforeComma)) yield data.fixer.removeRange(maybeBeforeComma.range);
							}
							yield data.newProps.fixObject({
								fixer: data.fixer,
								object
							});
							return;
						}
					}
					yield data.fixer.replaceTextRange(getParenthesizedRange(data.node, sourceCode), data.newProps.toObjectString());
				}
			});
			/**
			* Finds the object expression that is closest to the given array element.
			*/
			function findClosestObject(array, target) {
				const index = array.elements.indexOf(target);
				const afterElements = array.elements.slice(index + 1);
				const beforeElements = array.elements.slice(0, index).reverse();
				const length = Math.max(afterElements.length, beforeElements.length);
				for (let index = 0; index < length; index++) {
					const after = afterElements[index];
					if (after?.type === _typescript_eslint_types.AST_NODE_TYPES.ObjectExpression) return after;
					const before = beforeElements[index];
					if (before?.type === _typescript_eslint_types.AST_NODE_TYPES.ObjectExpression) return before;
				}
				return null;
			}
			/** Visit expression */
			function visitElementExpression(node, state) {
				if (node.type === _typescript_eslint_types.AST_NODE_TYPES.ConditionalExpression) verifyConditionalExpression(node, state);
				else if (node.type === _typescript_eslint_types.AST_NODE_TYPES.TemplateLiteral) {
					const quasis = [...node.quasis];
					let beforeQuasiWk = quasis.shift();
					for (const expression of node.expressions) {
						const beforeQuasi = beforeQuasiWk;
						const afterQuasi = quasis.shift();
						visitElementExpression(expression, {
							beforeIsWord() {
								const beforeElements = [];
								const targetIndex = node.expressions.indexOf(expression);
								for (let index = 0; index < targetIndex; index++) beforeElements.push(node.quasis[index], node.expressions[index]);
								beforeElements.push(node.quasis[targetIndex]);
								const isSpace = endsWithSpace(beforeElements);
								return isSpace == null ? state.beforeIsWord() : !isSpace;
							},
							afterIsWord() {
								const targetIndex = node.expressions.indexOf(expression);
								const afterElements = [node.quasis[targetIndex + 1]];
								for (let index = targetIndex + 1; index < node.expressions.length; index++) afterElements.push(node.expressions[index], node.quasis[index + 1]);
								const isSpace = startsWithSpace(afterElements);
								return isSpace == null ? state.afterIsWord() : !isSpace;
							},
							fixArrayElement: state.fixArrayElement,
							*fixExpression(data) {
								const fixer = data.fixer;
								if (beforeQuasi.value.cooked?.trim() || afterQuasi.value.cooked?.trim() || node.expressions.length > 1) {
									yield fixer.replaceTextRange([beforeQuasi.range[1] - 2, beforeQuasi.range[1]], data.beforeSpaces);
									yield fixer.replaceTextRange([afterQuasi.range[0], afterQuasi.range[0] + 1], data.afterSpaces);
									yield* state.fixArrayElement(data);
									return;
								}
								const tokens = getParenthesizedTokens(node, sourceCode);
								yield fixer.removeRange([tokens.left.range[0], beforeQuasi.range[1]]);
								yield fixer.removeRange([afterQuasi.range[0], tokens.right.range[1]]);
								yield* state.fixExpression({
									...data,
									beforeSpaces: beforeQuasi.value.cooked + data.beforeSpaces,
									afterSpaces: data.afterSpaces + afterQuasi.value.cooked
								});
							}
						});
						beforeQuasiWk = afterQuasi;
					}
				} else if (node.type === _typescript_eslint_types.AST_NODE_TYPES.CallExpression) {
					if (isStringCallExpression(node) && node.arguments[0] && node.arguments[0].type !== _typescript_eslint_types.AST_NODE_TYPES.SpreadElement) visitElementExpression(node.arguments[0], {
						beforeIsWord: state.beforeIsWord,
						afterIsWord: state.afterIsWord,
						fixArrayElement: state.fixArrayElement,
						*fixExpression(data) {
							const openParen = sourceCode.getTokenAfter(getParenthesizedTokens(node.callee, sourceCode).right);
							const stripStart = sourceCode.getTokenAfter(getParenthesizedTokens(node.arguments[0], sourceCode).right);
							const tokens = getParenthesizedTokens(node, sourceCode);
							yield data.fixer.removeRange([tokens.left.range[0], openParen.range[1]]);
							yield data.fixer.removeRange([stripStart.range[0], tokens.right.range[1]]);
							yield* state.fixExpression(data);
						}
					});
					else if (node.callee.type === _typescript_eslint_types.AST_NODE_TYPES.MemberExpression && (0, _eslint_community_eslint_utils.getPropertyName)(node.callee) === "trim") {
						const men = node.callee;
						visitElementExpression(men.object, {
							beforeIsWord: state.beforeIsWord,
							afterIsWord: state.afterIsWord,
							fixArrayElement: state.fixArrayElement,
							*fixExpression(data) {
								const tokens = getParenthesizedTokens(men.object, sourceCode);
								yield data.fixer.removeRange([tokens.right.range[1], node.range[1]]);
								yield* state.fixExpression(data);
							}
						});
					}
				} else if (node.type === _typescript_eslint_types.AST_NODE_TYPES.BinaryExpression) {
					const elements = extractConcatExpressions(node, sourceCode);
					if (!elements) return;
					for (const expression of elements) visitElementExpression(expression, {
						beforeIsWord() {
							const index = elements.indexOf(expression);
							const isSpace = endsWithSpace(elements.slice(0, index));
							return isSpace == null ? state.beforeIsWord() : !isSpace;
						},
						afterIsWord() {
							const index = elements.indexOf(expression);
							const isSpace = startsWithSpace(elements.slice(index + 1));
							return isSpace == null ? state.afterIsWord() : !isSpace;
						},
						fixArrayElement: state.fixArrayElement,
						*fixExpression(data) {
							const fixer = data.fixer;
							const index = elements.indexOf(expression);
							const beforeElements = elements.slice(0, index);
							const afterElements = elements.slice(index + 1);
							const tokens = getParenthesizedTokens(expression, sourceCode);
							if (beforeElements.some((element) => {
								const str = getStringIfConstant(element);
								return str == null || Boolean(str.trim());
							}) || afterElements.some((element) => {
								const str = getStringIfConstant(element);
								return str == null || Boolean(str.trim());
							})) {
								const beforeElement = beforeElements[beforeElements.length - 1];
								const afterElement = afterElements[0];
								if (beforeElement && isStringLiteral(beforeElement) && afterElement && isStringLiteral(afterElement)) {
									if (sourceCode.text[beforeElement.range[0]] !== sourceCode.text[afterElement.range[0]]) {
										const targetIsBefore = sourceCode.text[beforeElement.range[0]] === "'";
										const replaceLiteral = targetIsBefore ? beforeElement : afterElement;
										yield fixer.replaceTextRange([replaceLiteral.range[0] + 1, replaceLiteral.range[1] - 1], JSON.stringify(replaceLiteral.value).slice(1, -1));
										yield fixer.replaceTextRange(targetIsBefore ? [replaceLiteral.range[0], replaceLiteral.range[0] + 1] : [replaceLiteral.range[1] - 1, replaceLiteral.range[1]], "\"");
									}
									yield fixer.replaceTextRange([beforeElement.range[1] - 1, tokens.left.range[0]], data.beforeSpaces);
									yield fixer.replaceTextRange([tokens.right.range[1], afterElement.range[0] + 1], data.afterSpaces);
								} else {
									const beforeToken = sourceCode.getTokenBefore(tokens.left);
									if (beforeToken?.value === "+") yield fixer.removeRange(beforeToken.range);
									else {
										const afterToken = sourceCode.getTokenAfter(tokens.right);
										yield fixer.removeRange(afterToken.range);
									}
								}
								yield* state.fixArrayElement(data);
								return;
							}
							if (beforeElements.length) {
								const beforeToken = sourceCode.getTokenBefore(tokens.left);
								yield fixer.removeRange([beforeElements[0].range[0], beforeToken.range[1]]);
							}
							if (afterElements.length) {
								const afterToken = sourceCode.getTokenAfter(tokens.right);
								yield fixer.removeRange([afterToken.range[0], afterElements[afterElements.length - 1].range[1]]);
							}
							yield* state.fixExpression({
								...data,
								beforeSpaces: beforeElements.map((e) => getStringIfConstant(e)).join("") + data.beforeSpaces,
								afterSpaces: data.afterSpaces + afterElements.map((e) => getStringIfConstant(e)).join("")
							});
						}
					});
				}
			}
		}
		/** Extract array element expressions */
		function extractElements(node) {
			if (node.type === _typescript_eslint_types.AST_NODE_TYPES.ArrayExpression) {
				const result = [];
				for (const element of node.elements) {
					if (!element || element.type === _typescript_eslint_types.AST_NODE_TYPES.SpreadElement) continue;
					result.push(...extractElements(element).map((e) => {
						if (e.array == null) return {
							array: node,
							node: e.node
						};
						return e;
					}));
				}
				return result;
			}
			return [{
				node,
				array: null
			}];
		}
		return {
			JSXAttribute: verifyAttr,
			AstroTemplateLiteralAttribute: verifyAttr
		};
	}
});
//#endregion
//#region src/utils/string-literal-parser/tokenizer.ts
const CP_BACK_SLASH = "\\".codePointAt(0);
const CP_BACKTICK = "`".codePointAt(0);
const CP_CR = "\r".codePointAt(0);
const CP_LF = "\n".codePointAt(0);
const CP_OPENING_BRACE = "{".codePointAt(0);
const CP_a = "a".codePointAt(0);
const CP_A = "A".codePointAt(0);
const CP_n = "n".codePointAt(0);
const CP_r = "r".codePointAt(0);
const CP_t = "t".codePointAt(0);
const CP_b = "b".codePointAt(0);
const CP_v = "v".codePointAt(0);
const CP_f = "f".codePointAt(0);
const CP_u = "u".codePointAt(0);
const CP_x = "x".codePointAt(0);
const CP_0 = "0".codePointAt(0);
const CP_7 = "7".codePointAt(0);
const CP_8 = "8".codePointAt(0);
const CP_9 = "9".codePointAt(0);
var Tokenizer = class {
	source;
	pos;
	end;
	ecmaVersion;
	constructor(source, options) {
		this.source = source;
		this.pos = options.start;
		this.end = options.end ?? null;
		this.ecmaVersion = options.ecmaVersion;
	}
	*parseTokens(quote) {
		const inTemplate = quote === CP_BACKTICK;
		const endIndex = this.end ?? this.source.length;
		while (this.pos < endIndex) {
			const start = this.pos;
			const cp = this.source.codePointAt(start);
			if (cp == null) throw new Error("Unterminated string constant");
			this.pos = inc(start, cp);
			if (cp === quote) break;
			if (cp === CP_BACK_SLASH) {
				const { value, kind } = this.readEscape(inTemplate);
				yield {
					type: "EscapeToken",
					kind,
					value,
					range: [start, this.pos]
				};
			} else if (cp === CP_CR || cp === CP_LF) if (inTemplate) {
				if (cp === CP_CR && this.source.codePointAt(this.pos) === CP_LF) this.pos++;
				yield {
					type: "CharacterToken",
					value: "\n",
					range: [start, this.pos]
				};
			} else throw new Error("Unterminated string constant");
			else {
				if (this.ecmaVersion >= 2019 && (cp === 8232 || cp === 8233) && !inTemplate) throw new Error("Unterminated string constant");
				yield {
					type: "CharacterToken",
					value: String.fromCodePoint(cp),
					range: [start, this.pos]
				};
			}
		}
	}
	readEscape(inTemplate) {
		const cp = this.source.codePointAt(this.pos);
		if (cp == null) throw new Error("Invalid or unexpected token");
		this.pos = inc(this.pos, cp);
		switch (cp) {
			case CP_n: return {
				value: "\n",
				kind: "special"
			};
			case CP_r: return {
				value: "\r",
				kind: "special"
			};
			case CP_t: return {
				value: "	",
				kind: "special"
			};
			case CP_b: return {
				value: "\b",
				kind: "special"
			};
			case CP_v: return {
				value: "\v",
				kind: "special"
			};
			case CP_f: return {
				value: "\f",
				kind: "special"
			};
			case CP_CR: if (this.source.codePointAt(this.pos) === CP_LF) this.pos++;
			case CP_LF: return {
				value: "",
				kind: "eol"
			};
			case CP_x: return {
				value: String.fromCodePoint(this.readHex(2)),
				kind: "hex"
			};
			case CP_u: return {
				value: String.fromCodePoint(this.readUnicode()),
				kind: "unicode"
			};
			default:
				if (CP_0 <= cp && cp <= CP_7) {
					let octalStr = /^[0-7]+/u.exec(this.source.slice(this.pos - 1, this.pos + 2))[0];
					let octal = parseInt(octalStr, 8);
					if (octal > 255) {
						octalStr = octalStr.slice(0, -1);
						octal = parseInt(octalStr, 8);
					}
					this.pos += octalStr.length - 1;
					const nextCp = this.source.codePointAt(this.pos);
					if ((octalStr !== "0" || nextCp === CP_8 || nextCp === CP_9) && inTemplate) throw new Error("Octal literal in template string");
					return {
						value: String.fromCodePoint(octal),
						kind: "octal"
					};
				}
				return {
					value: String.fromCodePoint(cp),
					kind: "char"
				};
		}
	}
	readUnicode() {
		const cp = this.source.codePointAt(this.pos);
		if (cp === CP_OPENING_BRACE) {
			if (this.ecmaVersion < 2015) throw new Error(`Unexpected character '${String.fromCodePoint(cp)}'`);
			this.pos++;
			const endIndex = this.source.indexOf("}", this.pos);
			if (endIndex < 0) throw new Error("Invalid Unicode escape sequence");
			const code = this.readHex(endIndex - this.pos);
			this.pos++;
			if (code > 1114111) throw new Error("Code point out of bounds");
			return code;
		}
		return this.readHex(4);
	}
	readHex(length) {
		let total = 0;
		for (let i = 0; i < length; i++, this.pos++) {
			const cp = this.source.codePointAt(this.pos);
			if (cp == null) throw new Error(`Invalid hexadecimal escape sequence`);
			let val;
			if (CP_a <= cp) val = cp - CP_a + 10;
			else if (CP_A <= cp) val = cp - CP_A + 10;
			else if (CP_0 <= cp && cp <= CP_9) val = cp - CP_0;
			else throw new Error(`Invalid hexadecimal escape sequence`);
			if (val >= 16) throw new Error(`Invalid hexadecimal escape sequence`);
			total = total * 16 + val;
		}
		return total;
	}
};
/**
* Get next index
*/
function inc(pos, cp) {
	return pos + (cp >= 65536 ? 2 : 1);
}
//#endregion
//#region src/utils/string-literal-parser/parser.ts
/** Parse for string tokens */
function* parseStringTokens(source, option) {
	const startIndex = option?.start ?? 0;
	const ecmaVersion = option?.ecmaVersion ?? Infinity;
	yield* new Tokenizer(source, {
		start: startIndex,
		end: option?.end,
		ecmaVersion: ecmaVersion >= 6 && ecmaVersion < 2015 ? ecmaVersion + 2009 : ecmaVersion
	}).parseTokens();
}
//#endregion
//#region src/rules/prefer-split-class-list.ts
var prefer_split_class_list_default = createRule("prefer-split-class-list", {
	meta: {
		docs: {
			description: "require use split array elements in `class:list`",
			category: "Stylistic Issues",
			recommended: false
		},
		schema: [{
			type: "object",
			properties: { splitLiteral: { type: "boolean" } },
			additionalProperties: false
		}],
		messages: {
			uselessClsx: "Using `clsx()` for the `class:list` has no effect.",
			split: "Can split elements with spaces."
		},
		fixable: "code",
		type: "suggestion"
	},
	create(context) {
		const sourceCode = getSourceCode(context);
		if (!sourceCode.parserServices?.isAstro) return {};
		const splitLiteral = Boolean(context.options[0]?.splitLiteral);
		/** Check if it should be reported. */
		function shouldReport(state) {
			if (state.isFirstElement) {
				if (state.isLeading) return false;
			}
			if (state.isLastElement) {
				if (state.isTrailing) return false;
			}
			if (splitLiteral) return true;
			return state.isLeading || state.isTrailing;
		}
		/** Verify attr */
		function verifyAttr(attr) {
			if (getAttributeName(attr) !== "class:list") return;
			if (!attr.value || attr.value.type !== _typescript_eslint_types.AST_NODE_TYPES.JSXExpressionContainer || attr.value.expression.type === _typescript_eslint_types.AST_NODE_TYPES.JSXEmptyExpression) return;
			const expression = attr.value.expression;
			verifyExpression(expression, function* (fixer) {
				if (expression.type === _typescript_eslint_types.AST_NODE_TYPES.ArrayExpression) return;
				yield fixer.insertTextBeforeRange(expression.range, "[");
				yield fixer.insertTextAfterRange(expression.range, "]");
			});
		}
		/** Verify expression */
		function verifyExpression(node, transformArray, call) {
			if (node.type === _typescript_eslint_types.AST_NODE_TYPES.TemplateLiteral) {
				const first = node.quasis[0];
				const last = node.quasis[node.quasis.length - 1];
				for (const quasi of node.quasis) verifyTemplateElement(quasi, {
					isFirstElement: first === quasi,
					isLastElement: last === quasi,
					transformArray,
					call
				});
			} else if (node.type === _typescript_eslint_types.AST_NODE_TYPES.BinaryExpression) verifyBinaryExpression(node, transformArray);
			else if (node.type === _typescript_eslint_types.AST_NODE_TYPES.ArrayExpression) {
				for (const element of node.elements) if (element) verifyExpression(element, transformArray);
			} else if (node.type === _typescript_eslint_types.AST_NODE_TYPES.Literal) {
				if (splitLiteral && isStringLiteral(node)) verifyStringLiteral(node, {
					isFirstElement: true,
					isLastElement: true,
					transformArray,
					call
				});
			} else if (node.type === _typescript_eslint_types.AST_NODE_TYPES.CallExpression) {
				if (node.callee.type === _typescript_eslint_types.AST_NODE_TYPES.MemberExpression && (0, _eslint_community_eslint_utils.getPropertyName)(node.callee) === "trim") verifyExpression(node.callee.object, transformArray, ".trim()");
			}
		}
		/** Verify TemplateElement */
		function verifyTemplateElement(node, state) {
			const stringEndOffset = node.tail ? node.range[1] - 1 : node.range[1] - 2;
			let isLeading = true;
			const spaces = [];
			for (const ch of parseStringTokens(sourceCode.text, {
				start: node.range[0] + 1,
				end: stringEndOffset
			})) if (ch.value.trim()) {
				if (spaces.length) {
					if (shouldReport({
						...state,
						isLeading,
						isTrailing: false
					})) reportRange([spaces[0].range[0], spaces[spaces.length - 1].range[1]]);
					spaces.length = 0;
				}
				isLeading = false;
			} else spaces.push(ch);
			if (spaces.length) {
				if (shouldReport({
					...state,
					isLeading,
					isTrailing: true
				})) reportRange([spaces[0].range[0], spaces[spaces.length - 1].range[1]]);
				spaces.length = 0;
			}
			/** Report */
			function reportRange(range) {
				context.report({
					loc: {
						start: sourceCode.getLocFromIndex(range[0]),
						end: sourceCode.getLocFromIndex(range[1])
					},
					messageId: "split",
					*fix(fixer) {
						yield* state.transformArray(fixer);
						yield fixer.replaceTextRange(range, `\`${state.call || ""},\``);
					}
				});
			}
		}
		/** Verify BinaryExpression */
		function verifyBinaryExpression(node, transformArray) {
			const elements = extractConcatExpressions(node, sourceCode);
			if (elements == null) return;
			const first = elements[0];
			const last = elements[elements.length - 1];
			for (const element of elements) if (isStringLiteral(element)) verifyStringLiteral(element, {
				isFirstElement: first === element,
				isLastElement: last === element,
				transformArray
			});
		}
		/** Verify StringLiteral */
		function verifyStringLiteral(node, state) {
			const quote = sourceCode.text[node.range[0]];
			let isLeading = true;
			const spaces = [];
			for (const ch of parseStringTokens(sourceCode.text, {
				start: node.range[0] + 1,
				end: node.range[1] - 1
			})) if (ch.value.trim()) {
				if (spaces.length) {
					if (shouldReport({
						...state,
						isLeading,
						isTrailing: false
					})) reportRange([spaces[0].range[0], spaces[spaces.length - 1].range[1]], {
						isLeading,
						isTrailing: false
					});
					spaces.length = 0;
				}
				isLeading = false;
			} else spaces.push(ch);
			if (spaces.length) {
				if (shouldReport({
					...state,
					isLeading,
					isTrailing: true
				})) reportRange([spaces[0].range[0], spaces[spaces.length - 1].range[1]], {
					isLeading,
					isTrailing: true
				});
				spaces.length = 0;
			}
			/** Report */
			function reportRange(range, spaceState) {
				context.report({
					loc: {
						start: sourceCode.getLocFromIndex(range[0]),
						end: sourceCode.getLocFromIndex(range[1])
					},
					messageId: "split",
					*fix(fixer) {
						yield* state.transformArray(fixer);
						let leftQuote = quote;
						let rightQuote = quote;
						const bin = node.parent;
						if (spaceState.isLeading && bin.right === node && isStringType(bin.left)) leftQuote = "";
						if (spaceState.isTrailing && bin.left === node && isStringType(bin.right)) rightQuote = "";
						const replaceRange = [...range];
						if (!leftQuote || !rightQuote) {
							if (!leftQuote) replaceRange[0]--;
							if (!rightQuote) replaceRange[1]++;
							yield fixer.remove(sourceCode.getTokensBetween(bin.left, bin.right, {
								includeComments: false,
								filter: (t) => t.value === bin.operator
							})[0]);
						}
						yield fixer.replaceTextRange(replaceRange, `${leftQuote}${state.call || ""},${rightQuote}`);
					}
				});
			}
		}
		/** Verify clsx */
		function verifyClsx(clsxCall) {
			if (clsxCall.node.type !== _typescript_eslint_types.AST_NODE_TYPES.CallExpression) return;
			const callNode = clsxCall.node;
			const parent = callNode.parent;
			if (!parent || parent.type !== _typescript_eslint_types.AST_NODE_TYPES.JSXExpressionContainer || parent.expression !== callNode) return;
			const parentParent = parent.parent;
			if (!parentParent || parentParent.type !== _typescript_eslint_types.AST_NODE_TYPES.JSXAttribute || parentParent.value !== parent || getAttributeName(parentParent) !== "class:list") return;
			context.report({
				node: clsxCall.node.callee,
				messageId: "uselessClsx",
				*fix(fixer) {
					const openToken = sourceCode.getTokenAfter(callNode.callee, {
						includeComments: false,
						filter: _eslint_community_eslint_utils.isOpeningParenToken
					});
					const closeToken = sourceCode.getLastToken(callNode);
					yield fixer.removeRange([callNode.range[0], openToken.range[1]]);
					yield fixer.remove(closeToken);
				}
			});
		}
		return {
			Program(node) {
				const referenceTracker = new _eslint_community_eslint_utils.ReferenceTracker(getSourceCode(context).getScope(node));
				for (const call of referenceTracker.iterateEsmReferences({ clsx: { [_eslint_community_eslint_utils.ReferenceTracker.CALL]: true } })) verifyClsx(call);
			},
			JSXAttribute: verifyAttr,
			AstroTemplateLiteralAttribute: verifyAttr
		};
	}
});
/** Checks whether given node evaluate type is string */
function isStringType(node) {
	if (node.type === _typescript_eslint_types.AST_NODE_TYPES.Literal) return typeof node.value === "string";
	else if (node.type === _typescript_eslint_types.AST_NODE_TYPES.TemplateLiteral) return true;
	else if (node.type === _typescript_eslint_types.AST_NODE_TYPES.BinaryExpression) return isStringType(node.left) || isStringType(node.right);
	return isStringCallExpression(node);
}
//#endregion
//#region src/utils/fix-tracker.ts
/**
* A helper class to combine fix options into a fix command. Currently, it
* exposes some "retain" methods that extend the range of the text being
* replaced so that other fixes won't touch that region in the same pass.
*/
var FixTracker = class {
	retainedRange;
	fixer;
	sourceCode;
	/**
	* Create a new FixTracker.
	* @param fixer A ruleFixer instance.
	* @param sourceCode A SourceCode object for the current code.
	*/
	constructor(fixer, sourceCode) {
		this.fixer = fixer;
		this.sourceCode = sourceCode;
		this.retainedRange = null;
	}
	/**
	* Mark the given range as "retained", meaning that other fixes may not
	* may not modify this region in the same pass.
	* @param range The range to retain.
	* @returns The same RuleFixer, for chained calls.
	*/
	retainRange(range) {
		this.retainedRange = range;
		return this;
	}
	/**
	* Given a node, find the function containing it (or the entire program) and
	* mark it as retained, meaning that other fixes may not modify it in this
	* pass. This is useful for avoiding conflicts in fixes that modify control
	* flow.
	* @param node The node to use as a starting point.
	* @returns The same RuleFixer, for chained calls.
	*/
	retainEnclosingFunction(node) {
		const functionNode = getUpperFunction(node);
		return this.retainRange(functionNode ? functionNode.range : this.sourceCode.ast.range);
	}
	/**
	* Given a node or token, find the token before and afterward, and mark that
	* range as retained, meaning that other fixes may not modify it in this
	* pass. This is useful for avoiding conflicts in fixes that make a small
	* change to the code where the AST should not be changed.
	* @param nodeOrToken The node or token to use as a starting
	*      point. The token to the left and right are use in the range.
	* @returns The same RuleFixer, for chained calls.
	*/
	retainSurroundingTokens(nodeOrToken) {
		const tokenBefore = this.sourceCode.getTokenBefore(nodeOrToken) || nodeOrToken;
		const tokenAfter = this.sourceCode.getTokenAfter(nodeOrToken) || nodeOrToken;
		return this.retainRange([tokenBefore.range[0], tokenAfter.range[1]]);
	}
	/**
	* Create a fix command that replaces the given range with the given text,
	* accounting for any retained ranges.
	* @param range The range to remove in the fix.
	* @param text The text to insert in place of the range.
	* @returns The fix command.
	*/
	replaceTextRange(range, text) {
		let actualRange;
		if (this.retainedRange) actualRange = [Math.min(this.retainedRange[0], range[0]), Math.max(this.retainedRange[1], range[1])];
		else actualRange = range;
		return this.fixer.replaceTextRange(actualRange, this.sourceCode.text.slice(actualRange[0], range[0]) + text + this.sourceCode.text.slice(range[1], actualRange[1]));
	}
	/**
	* Create a fix command that removes the given node or token, accounting for
	* any retained ranges.
	* @param nodeOrToken The node or token to remove.
	* @returns The fix command.
	*/
	remove(nodeOrToken) {
		return this.replaceTextRange(nodeOrToken.range, "");
	}
};
//#endregion
//#region src/rules/semi.ts
var semi_default = createRule("semi", {
	meta: {
		docs: {
			description: "Require or disallow semicolons instead of ASI",
			category: "Extension Rules",
			recommended: false,
			extensionRule: "semi"
		},
		type: "layout",
		fixable: "code",
		schema: { anyOf: [{
			type: "array",
			items: [{
				type: "string",
				enum: ["never"]
			}, {
				type: "object",
				properties: { beforeStatementContinuationChars: {
					type: "string",
					enum: [
						"always",
						"any",
						"never"
					]
				} },
				additionalProperties: false
			}],
			minItems: 0,
			maxItems: 2
		}, {
			type: "array",
			items: [{
				type: "string",
				enum: ["always"]
			}, {
				type: "object",
				properties: {
					omitLastInOneLineBlock: { type: "boolean" },
					omitLastInOneLineClassBody: { type: "boolean" }
				},
				additionalProperties: false
			}],
			minItems: 0,
			maxItems: 2
		}] },
		messages: {
			missingSemi: "Missing semicolon.",
			extraSemi: "Extra semicolon."
		}
	},
	create(context) {
		const sourceCode = getSourceCode(context);
		if (!sourceCode.parserServices?.isAstro) return {};
		const OPT_OUT_PATTERN = /^[(+\-/[`]/u;
		const unsafeClassFieldNames = new Set([
			"get",
			"set",
			"static"
		]);
		const unsafeClassFieldFollowers = new Set([
			"*",
			"in",
			"instanceof"
		]);
		const options = context.options[1];
		const never = context.options[0] === "never";
		const exceptOneLine = Boolean(options && "omitLastInOneLineBlock" in options && options.omitLastInOneLineBlock);
		const exceptOneLineClassBody = Boolean(options && "omitLastInOneLineClassBody" in options && options.omitLastInOneLineClassBody);
		const beforeStatementContinuationChars = options && "beforeStatementContinuationChars" in options && options.beforeStatementContinuationChars || "any";
		/**
		* Reports a semicolon error with appropriate location and message.
		* @param node The node with an extra or missing semicolon.
		* @param missing True if the semicolon is missing.
		*/
		function report(node, missing = false) {
			const lastToken = sourceCode.getLastToken(node);
			let messageId = "missingSemi";
			let fix, loc;
			if (!missing) {
				loc = {
					start: lastToken.loc.end,
					end: getNextLocation(sourceCode, lastToken.loc.end)
				};
				fix = function(fixer) {
					return fixer.insertTextAfter(lastToken, ";");
				};
			} else {
				messageId = "extraSemi";
				loc = lastToken.loc;
				fix = function(fixer) {
					/**
					* Expand the replacement range to include the surrounding
					* tokens to avoid conflicting with no-extra-semi.
					* https://github.com/eslint/eslint/issues/7928
					*/
					return new FixTracker(fixer, sourceCode).retainSurroundingTokens(lastToken).remove(lastToken);
				};
			}
			context.report({
				node,
				loc,
				messageId,
				fix
			});
		}
		/**
		* Check whether a given semicolon token is redundant.
		* @param semiToken A semicolon token to check.
		* @returns `true` if the next token is `;` or `}`.
		*/
		function isRedundantSemi(semiToken) {
			const nextToken = sourceCode.getTokenAfter(semiToken);
			return !nextToken || (0, _eslint_community_eslint_utils.isClosingBraceToken)(nextToken) || (0, _eslint_community_eslint_utils.isSemicolonToken)(nextToken);
		}
		/**
		* Check whether a given token is the closing brace of an arrow function.
		* @param lastToken A token to check.
		* @returns `true` if the token is the closing brace of an arrow function.
		*/
		function isEndOfArrowBlock(lastToken) {
			if (!(0, _eslint_community_eslint_utils.isClosingBraceToken)(lastToken)) return false;
			const node = sourceCode.getNodeByRangeIndex(lastToken.range[0]);
			return node.type === "BlockStatement" && node.parent.type === "ArrowFunctionExpression";
		}
		/**
		* Checks if a given PropertyDefinition node followed by a semicolon
		* can safely remove that semicolon. It is not to safe to remove if
		* the class field name is "get", "set", or "static", or if
		* followed by a generator method.
		* @param node The node to check.
		* @returns `true` if the node cannot have the semicolon
		*      removed.
		*/
		function maybeClassFieldAsiHazard(node) {
			if (node.type !== "PropertyDefinition") return false;
			/**
			* Certain names are problematic unless they also have a
			* a way to distinguish between keywords and property
			* names.
			*/
			if (!node.computed && node.key.type === "Identifier" && "name" in node.key && unsafeClassFieldNames.has(node.key.name)) {
				/**
				* For other unsafe names, we only care if there is no
				* initializer. No initializer = hazard.
				*/
				if (!(node.static && node.key.name === "static") && !node.value) return true;
			}
			const followingToken = sourceCode.getTokenAfter(node);
			return unsafeClassFieldFollowers.has(followingToken.value);
		}
		/**
		* Check whether a given node is on the same line with the next token.
		* @param node A statement node to check.
		* @returns `true` if the node is on the same line with the next token.
		*/
		function isOnSameLineWithNextToken(node) {
			const prevToken = sourceCode.getLastToken(node, 1);
			const nextToken = sourceCode.getTokenAfter(node);
			return Boolean(nextToken) && isTokenOnSameLine(prevToken, nextToken);
		}
		/**
		* Check whether a given node can connect the next line if the next line is unreliable.
		* @param node A statement node to check.
		* @returns `true` if the node can connect the next line.
		*/
		function maybeAsiHazardAfter(node) {
			const t = node.type;
			if (t === "DoWhileStatement" || t === "BreakStatement" || t === "ContinueStatement" || t === "DebuggerStatement" || t === "ImportDeclaration" || t === "ExportAllDeclaration") return false;
			if (t === "ReturnStatement") return Boolean(node.argument);
			if (t === "ExportNamedDeclaration") return Boolean(node.declaration);
			if (isEndOfArrowBlock(sourceCode.getLastToken(node, 1))) return false;
			return true;
		}
		/**
		* Check whether a given token can connect the previous statement.
		* @param token A token to check.
		* @returns `true` if the token is one of `[`, `(`, `/`, `+`, `-`, ```, `++`, and `--`.
		*/
		function maybeAsiHazardBefore(token) {
			return Boolean(token) && OPT_OUT_PATTERN.test(token.value) && token.value !== "++" && token.value !== "--" && token.value !== "---";
		}
		/**
		* Check if the semicolon of a given node is unnecessary, only true if:
		*   - next token is a valid statement divider (`;` or `}`).
		*   - next token is on a new line and the node is not connectable to the new line.
		* @param node A statement node to check.
		* @returns whether the semicolon is unnecessary.
		*/
		function canRemoveSemicolon(node) {
			if (isRedundantSemi(sourceCode.getLastToken(node))) return true;
			if (maybeClassFieldAsiHazard(node)) return false;
			if (isOnSameLineWithNextToken(node)) return false;
			if (node.type !== "PropertyDefinition" && beforeStatementContinuationChars === "never" && !maybeAsiHazardAfter(node)) return true;
			if (!maybeAsiHazardBefore(sourceCode.getTokenAfter(node))) return true;
			return false;
		}
		/**
		* Checks a node to see if it's the last item in a one-liner block.
		* Block is any `BlockStatement` or `StaticBlock` node. Block is a one-liner if its
		* braces (and consequently everything between them) are on the same line.
		* @param node The node to check.
		* @returns whether the node is the last item in a one-liner block.
		*/
		function isLastInOneLinerBlock(node) {
			const parent = node.parent;
			const nextToken = sourceCode.getTokenAfter(node);
			if (!nextToken || nextToken.value !== "}") return false;
			if (parent.type === "BlockStatement") return parent.loc.start.line === parent.loc.end.line;
			if (parent.type === "StaticBlock") return sourceCode.getFirstToken(parent, { skip: 1 }).loc.start.line === parent.loc.end.line;
			return false;
		}
		/**
		* Checks a node to see if it's the last item in a one-liner `ClassBody` node.
		* ClassBody is a one-liner if its braces (and consequently everything between them) are on the same line.
		* @param node The node to check.
		* @returns whether the node is the last item in a one-liner ClassBody.
		*/
		function isLastInOneLinerClassBody(node) {
			const parent = node.parent;
			const nextToken = sourceCode.getTokenAfter(node);
			if (!nextToken || nextToken.value !== "}") return false;
			if (parent.type === "ClassBody") return parent.loc.start.line === parent.loc.end.line;
			return false;
		}
		/**
		* Checks a node to see if it's followed by a semicolon.
		* @param node The node to check.
		*/
		function checkForSemicolon(node) {
			const isSemi = (0, _eslint_community_eslint_utils.isSemicolonToken)(sourceCode.getLastToken(node));
			if (never) {
				const nextToken = sourceCode.getTokenAfter(node);
				if (isSemi && canRemoveSemicolon(node)) report(node, true);
				else if (!isSemi && beforeStatementContinuationChars === "always" && node.type !== "PropertyDefinition" && maybeAsiHazardBefore(nextToken)) report(node);
			} else {
				const oneLinerBlock = exceptOneLine && isLastInOneLinerBlock(node);
				const oneLinerClassBody = exceptOneLineClassBody && isLastInOneLinerClassBody(node);
				const oneLinerBlockOrClassBody = oneLinerBlock || oneLinerClassBody;
				if (isSemi && oneLinerBlockOrClassBody) report(node, true);
				else if (!isSemi && !oneLinerBlockOrClassBody) report(node);
			}
		}
		/**
		* Checks to see if there's a semicolon after a variable declaration.
		* @param node The node to check.
		*/
		function checkForSemicolonForVariableDeclaration(node) {
			const parent = node.parent;
			if ((parent.type !== "ForStatement" || parent.init !== node) && (!/^For(?:In|Of)Statement/u.test(parent.type) || parent.left !== node)) checkForSemicolon(node);
		}
		return {
			VariableDeclaration: checkForSemicolonForVariableDeclaration,
			ExpressionStatement: checkForSemicolon,
			ReturnStatement: checkForSemicolon,
			ThrowStatement: checkForSemicolon,
			DoWhileStatement: checkForSemicolon,
			DebuggerStatement: checkForSemicolon,
			BreakStatement: checkForSemicolon,
			ContinueStatement: checkForSemicolon,
			ImportDeclaration: checkForSemicolon,
			ExportAllDeclaration: checkForSemicolon,
			ExportNamedDeclaration(node) {
				if (!node.declaration) checkForSemicolon(node);
			},
			ExportDefaultDeclaration(node) {
				if (node.declaration.type === "TSInterfaceDeclaration") return;
				if (!/(?:Class|Function)Declaration/u.test(node.declaration.type)) checkForSemicolon(node);
			},
			PropertyDefinition: checkForSemicolon,
			TSAbstractPropertyDefinition: checkForSemicolon,
			TSDeclareFunction: checkForSemicolon,
			TSExportAssignment: checkForSemicolon,
			TSImportEqualsDeclaration: checkForSemicolon,
			TSTypeAliasDeclaration: checkForSemicolon,
			TSEmptyBodyFunctionExpression: checkForSemicolon
		};
	}
});
//#endregion
//#region src/rules/sort-attributes.ts
var sort_attributes_default = createRule("sort-attributes", {
	meta: {
		docs: {
			description: "enforce sorting of attributes",
			category: "Stylistic Issues",
			recommended: false
		},
		schema: [{
			type: "object",
			properties: {
				type: {
					type: "string",
					enum: ["alphabetical", "line-length"]
				},
				ignoreCase: { type: "boolean" },
				order: {
					type: "string",
					enum: ["asc", "desc"]
				}
			},
			additionalProperties: false
		}],
		messages: { unexpectedAstroAttributesOrder: "Expected \"{{right}}\" to come before \"{{left}}\"." },
		fixable: "code",
		type: "suggestion"
	},
	create(context) {
		const sourceCode = getSourceCode(context);
		if (!sourceCode.parserServices?.isAstro) return {};
		return { JSXElement(node) {
			const { openingElement } = node;
			const { attributes } = openingElement;
			if (attributes.length <= 1) return;
			/**
			*
			*/
			function pairwise(nodes, callback) {
				if (nodes.length > 1) for (let i = 1; i < nodes.length; i++) {
					const left = nodes.at(i - 1);
					const right = nodes.at(i);
					if (left && right) callback(left, right, i - 1);
				}
			}
			const compareFunc = context.options[0]?.type === "line-length" ? (a, b) => a.size - b.size : (a, b) => formatName(a.name).localeCompare(formatName(b.name));
			const compare = context.options[0]?.order === "desc" ? (left, right) => compareFunc(right, left) : (left, right) => compareFunc(left, right);
			const parts = attributes.reduce((accumulator, attribute) => {
				if (attribute.type === "JSXSpreadAttribute") {
					accumulator.push([]);
					return accumulator;
				}
				const name = typeof attribute.name.name === "string" ? attribute.name.name : sourceCode.text.slice(...attribute.name.range);
				accumulator[accumulator.length - 1].push({
					name,
					node: attribute,
					size: attribute.range[1] - attribute.range[0]
				});
				return accumulator;
			}, [[]]);
			for (const nodes of parts) pairwise(nodes, (left, right) => {
				if (compare(left, right) > 0) context.report({
					node: left.node,
					messageId: "unexpectedAstroAttributesOrder",
					data: {
						left: left.name,
						right: right.name
					},
					fix(fixer) {
						return fixer.replaceTextRange([left.node.range[0], right.node.range[1]], sourceCode.text.slice(...right.node.range) + " ".repeat(right.node.range[0] - left.node.range[1]) + sourceCode.text.slice(...left.node.range));
					}
				});
			});
			/**
			* Format the name based on the ignoreCase option.
			*/
			function formatName(name) {
				return context.options[0]?.ignoreCase === false ? name : name.toLowerCase();
			}
		} };
	}
});
//#endregion
//#region src/rules/valid-compile.ts
var valid_compile_default = createRule("valid-compile", {
	meta: {
		docs: {
			description: "disallow warnings when compiling.",
			category: "Possible Errors",
			recommended: true
		},
		schema: [],
		messages: {},
		type: "problem"
	},
	create(context) {
		const sourceCode = getSourceCode(context);
		if (!sourceCode.parserServices?.isAstro) return {};
		const diagnostics = sourceCode.parserServices?.getAstroResult?.().diagnostics;
		if (!diagnostics) return {};
		return { Program() {
			for (const { text, code, location, severity } of diagnostics) if (severity === 2) context.report({
				loc: {
					start: location,
					end: location
				},
				message: `${text} [${code}]`
			});
		} };
	}
});
//#endregion
//#region src/utils/resolve-parser/require-user.ts
/** Require from user local */
function requireUserLocal(id) {
	try {
		const cwd = process.cwd();
		return (0, node_module.createRequire)(node_path.default.join(cwd, "__placeholder__.js"))(id);
	} catch {
		return null;
	}
}
//#endregion
//#region src/a11y/load.ts
let pluginJsxA11yCache = null;
let loaded = false;
/**
* Load `eslint-plugin-jsx-a11y` from the user local.
*/
function getPluginJsxA11y() {
	if (loaded) return pluginJsxA11yCache;
	if (!pluginJsxA11yCache) pluginJsxA11yCache = requireUserLocal("eslint-plugin-jsx-a11y");
	if (!pluginJsxA11yCache) {
		if (typeof require !== "undefined") try {
			pluginJsxA11yCache = require("eslint-plugin-jsx-a11y");
		} catch {
			loaded = true;
		}
	}
	return pluginJsxA11yCache || null;
}
//#endregion
//#region src/a11y/keys.ts
const plugin$1 = getPluginJsxA11y();
const a11yRuleKeys = plugin$1?.rules ? Object.keys(plugin$1.rules).filter((s) => !plugin$1?.rules?.[s]?.meta?.deprecated) : [
	"alt-text",
	"anchor-ambiguous-text",
	"anchor-has-content",
	"anchor-is-valid",
	"aria-activedescendant-has-tabindex",
	"aria-props",
	"aria-proptypes",
	"aria-role",
	"aria-unsupported-elements",
	"autocomplete-valid",
	"click-events-have-key-events",
	"control-has-associated-label",
	"heading-has-content",
	"html-has-lang",
	"iframe-has-title",
	"img-redundant-alt",
	"interactive-supports-focus",
	"label-has-associated-control",
	"lang",
	"media-has-caption",
	"mouse-events-have-key-events",
	"no-access-key",
	"no-aria-hidden-on-focusable",
	"no-autofocus",
	"no-distracting-elements",
	"no-interactive-element-to-noninteractive-role",
	"no-noninteractive-element-interactions",
	"no-noninteractive-element-to-interactive-role",
	"no-noninteractive-tabindex",
	"no-redundant-roles",
	"no-static-element-interactions",
	"prefer-tag-over-role",
	"role-has-required-aria-props",
	"role-supports-aria-props",
	"scope",
	"tabindex-no-positive"
];
const a11yConfigKeys = plugin$1?.configs ? Object.keys(plugin$1.configs) : ["recommended", "strict"];
//#endregion
//#region src/environments/index.ts
const environments = { astro: { globals: {
	Astro: false,
	Fragment: false
} } };
//#endregion
//#region src/utils/resolve-parser/espree.ts
let espreeCache = null;
/** Checks if given path is linter path */
function isLinterPath(p) {
	return p.includes(`eslint${node_path.default.sep}lib${node_path.default.sep}linter${node_path.default.sep}linter.js`);
}
/**
* Load `espree` from the loaded ESLint.
* If the loaded ESLint was not found, just returns `require("espree")`.
*/
function getEspree() {
	if (!espreeCache) {
		const linterPath = Object.keys(require.cache || {}).find(isLinterPath);
		if (linterPath) try {
			espreeCache = (0, node_module.createRequire)(linterPath)("espree");
		} catch {}
	}
	if (!espreeCache) espreeCache = requireUserLocal("espree");
	if (!espreeCache) espreeCache = require("espree");
	return espreeCache;
}
//#endregion
//#region src/utils/resolve-parser/index.ts
/** Resolve parser */
function resolveParser() {
	for (const id of [
		"@typescript-eslint/parser",
		"@babel/eslint-parser",
		"espree"
	]) {
		const parser = toParserForESLint(requireUserLocal(id));
		if (!parser) continue;
		return parser;
	}
	try {
		return toParserForESLint(require("@typescript-eslint/parser"));
	} catch {}
	return toParserForESLint(getEspree());
}
/** To the parser for ESLint */
function toParserForESLint(mod) {
	for (const m of [mod, mod && mod.default]) {
		if (!m) continue;
		if (typeof m.parseForESLint === "function") return m;
		if (typeof m.parse === "function") return { parseForESLint(...args) {
			return { ast: m.parse(...args) };
		} };
	}
	return null;
}
//#endregion
//#region src/shared/client-script/parse-expression.ts
/**
* Parse expression
*/
function parseExpression(code) {
	const result = resolveParser().parseForESLint(`(
${code}
)`, {
		range: true,
		loc: true
	});
	const expression = result.ast.body[0].expression;
	(0, astro_eslint_parser.traverseNodes)(expression, {
		visitorKeys: result.visitorKeys,
		enterNode(node) {
			node.loc.start = {
				...node.loc.start,
				line: node.loc.start.line - 1
			};
			node.loc.end = {
				...node.loc.end,
				line: node.loc.end.line - 1
			};
			node.range = [node.range[0] - 2, node.range[1] - 2];
		},
		leaveNode() {}
	});
	return expression;
}
//#endregion
//#region src/shared/client-script/index.ts
const RE_LEADING_SPACES = /^[\t ]+/u;
let seq = 0;
var Locs = class {
	lineStartIndices;
	constructor(lines) {
		const lineStartIndices = [0];
		let index = 0;
		for (const line of lines[lines.length - 1] ? lines : lines.slice(0, -1)) {
			index += line.length;
			lineStartIndices.push(index);
		}
		this.lineStartIndices = lineStartIndices;
	}
	getLocFromIndex(index) {
		const lineNumber = sortedLastIndex(this.lineStartIndices, index);
		return {
			line: lineNumber,
			column: index - this.lineStartIndices[lineNumber - 1]
		};
	}
};
var ClientScript = class {
	id;
	code;
	script;
	parsed;
	block;
	constructor(code, script, parsed) {
		this.code = code;
		this.script = script;
		this.parsed = parsed;
		this.id = ++seq;
		this.block = this.initBlock();
	}
	initBlock() {
		const textNode = this.script.children[0];
		const startOffset = textNode.position.start.offset;
		const endOffset = this.parsed.getEndOffset(textNode);
		const startLoc = this.parsed.getLocFromIndex(startOffset);
		const lines = this.code.slice(startOffset, endOffset).split(/(?<=\n)/u);
		const firstLine = lines.shift();
		const textLines = [];
		const remapColumnOffsets = [];
		const remapLines = [];
		const defineVars = this.extractDefineVars();
		if (defineVars.length) {
			textLines.push("/* global\n");
			remapLines.push(-1);
			remapColumnOffsets.push(-1);
			for (const defineVar of defineVars) {
				textLines.push(`${defineVar.name}\n`);
				remapLines.push(defineVar.loc.line);
				remapColumnOffsets.push(defineVar.loc.column);
			}
			textLines.push("-- define:vars */\n");
			remapLines.push(-1);
			remapColumnOffsets.push(-1);
		}
		if (firstLine.trim()) {
			const firstLineIndent = (RE_LEADING_SPACES.exec(firstLine) || [""])[0].length;
			textLines.push(firstLine.slice(firstLineIndent));
			remapLines.push(startLoc.line);
			remapColumnOffsets.push(firstLineIndent + startLoc.column);
		}
		const indent = getIndent(lines);
		for (let index = 0; index < lines.length; index++) {
			const line = lines[index];
			const lineIndent = Math.min(indent, line.length);
			if (line.slice(lineIndent)) {
				textLines.push(line.slice(lineIndent));
				remapColumnOffsets.push(lineIndent);
			} else if (line.endsWith("\n")) {
				const eol = line.endsWith("\r\n") ? "\r\n" : "\n";
				textLines.push(eol);
				remapColumnOffsets.push(line.length - eol.length);
			} else {
				textLines.push("");
				remapColumnOffsets.push(lineIndent);
			}
			remapLines.push(startLoc.line + index + 1);
		}
		const text = textLines.join("");
		const textLocs = new Locs(textLines);
		/** Remap loc */
		const remapLoc = (loc) => {
			const lineIndex = loc.line - 1;
			if (remapLines.length > lineIndex) return {
				line: remapLines[lineIndex],
				column: loc.column + remapColumnOffsets[lineIndex]
			};
			if (remapLines.length === lineIndex) return this.parsed.getLocFromIndex(endOffset + loc.column);
			return {
				line: -1,
				column: loc.column + 0
			};
		};
		/** Remap range */
		const remapRange = (range) => {
			const startLoc = textLocs.getLocFromIndex(range[0]);
			const normalEndLoc = textLocs.getLocFromIndex(range[1]);
			const endLoc = normalEndLoc.column > 0 ? normalEndLoc : textLocs.getLocFromIndex(range[1] - 1);
			const remappedStartLoc = remapLoc(startLoc);
			const remappedEndLoc = remapLoc(endLoc);
			if (remappedStartLoc.line < 0 || remappedEndLoc.line < 0) return null;
			return [this.parsed.getIndexFromLoc(remappedStartLoc), this.parsed.getIndexFromLoc(remappedEndLoc) + (normalEndLoc.column > 0 ? 0 : 1)];
		};
		return {
			text,
			remapMessage(message) {
				const loc = remapLoc(message);
				message.line = loc.line;
				message.column = loc.column;
				if (typeof message.endLine === "number" && typeof message.endColumn === "number") {
					const loc = remapLoc({
						line: message.endLine,
						column: message.endColumn
					});
					message.endLine = loc.line;
					message.endColumn = loc.column;
				}
				if (message.fix) {
					const remappedRange = remapRange(message.fix.range);
					if (remappedRange) message.fix.range = remappedRange;
					else delete message.fix;
				}
				if (message.suggestions) for (const suggestion of [...message.suggestions]) {
					const remappedRange = remapRange(suggestion.fix.range);
					if (remappedRange) suggestion.fix.range = remappedRange;
					else message.suggestions.splice(message.suggestions.indexOf(suggestion), 1);
				}
				return message;
			}
		};
	}
	extractDefineVars() {
		const defineVars = this.script.attributes.find((attr) => attr.kind === "expression" && attr.name === "define:vars");
		if (!defineVars) return [];
		const valueStart = this.parsed.calcAttributeValueStartOffset(defineVars);
		const valueEnd = this.parsed.calcAttributeEndOffset(defineVars);
		let expression;
		try {
			expression = parseExpression(this.code.slice(valueStart + 1, valueEnd - 1));
		} catch {
			return [];
		}
		if (expression.type !== _typescript_eslint_types.AST_NODE_TYPES.ObjectExpression) return [];
		const startLoc = this.parsed.getLocFromIndex(valueStart + 1);
		return expression.properties.filter((p) => p.type === _typescript_eslint_types.AST_NODE_TYPES.Property).filter((p) => !p.computed).map((p) => {
			return {
				name: p.key.type === _typescript_eslint_types.AST_NODE_TYPES.Identifier ? p.key.name : p.key.value,
				loc: {
					line: p.key.loc.start.line + startLoc.line - 1,
					column: p.key.loc.start.column + (p.key.loc.start.line === 1 ? startLoc.column : 0)
				}
			};
		});
	}
	getProcessorFile(ext) {
		return {
			text: this.block.text,
			filename: `${this.id}${ext}`
		};
	}
	remapMessages(messages) {
		return messages.filter((m) => !this.isIgnoreMessage(m)).map((m) => this.block.remapMessage(m)).filter((m) => m.line >= 0);
	}
	isIgnoreMessage(message) {
		if ((message.ruleId === "eol-last" || message.ruleId === "rule-to-test/eol-last") && message.messageId === "unexpected") return true;
		return false;
	}
};
/** Get indent */
function getIndent(lines) {
	let indent = null;
	for (const line of lines) {
		if (!line.trim()) continue;
		const lineIndent = (RE_LEADING_SPACES.exec(line) || [""])[0].length;
		if (indent == null) indent = lineIndent;
		else indent = Math.min(indent, lineIndent);
		if (indent === 0) break;
	}
	return indent || 0;
}
/**
* Uses a binary search to determine the highest index at which value should be inserted into array in order to maintain its sort order.
*/
function sortedLastIndex(array, value) {
	let lower = 0;
	let upper = array.length;
	while (lower < upper) {
		const mid = Math.floor(lower + (upper - lower) / 2);
		const target = array[mid];
		if (target < value) lower = mid + 1;
		else if (target > value) upper = mid;
		else return mid + 1;
	}
	return upper;
}
//#endregion
//#region src/shared/index.ts
var Shared = class {
	clientScripts = [];
	addClientScript(code, node, parsed) {
		const clientScript = new ClientScript(code, node, parsed);
		this.clientScripts.push(clientScript);
		return clientScript;
	}
};
const sharedMap = /* @__PURE__ */ new Map();
/** Start sharing and make the data available. */
function beginShared(filename) {
	const result = new Shared();
	sharedMap.set(filename, result);
	return result;
}
/** Get the shared data and end the sharing. */
function terminateShared(filename) {
	const result = sharedMap.get(filename);
	sharedMap.delete(filename);
	return result ?? null;
}
//#endregion
//#region package.json
var name$1 = "eslint-plugin-astro";
var version$1 = "1.7.0";
//#endregion
//#region src/meta.ts
var meta_exports = /* @__PURE__ */ __exportAll({
	name: () => name,
	version: () => version
});
const name = name$1;
const version = version$1;
//#endregion
//#region src/processor/index.ts
const astroProcessor = {
	preprocess(code, filename) {
		return preprocess(code, filename, ".js");
	},
	postprocess,
	supportsAutofix: true,
	meta: meta_exports
};
const clientSideTsProcessor = {
	preprocess(code, filename) {
		return preprocess(code, filename, ".ts");
	},
	postprocess,
	supportsAutofix: true,
	meta: {
		...meta_exports,
		name: "astro/client-side-ts"
	}
};
/** preprocess */
function preprocess(code, filename, virtualFileExt) {
	if (filename) {
		const shared = beginShared(filename);
		let parsed;
		try {
			parsed = (0, astro_eslint_parser.parseTemplate)(code);
		} catch {
			return [code];
		}
		parsed.walk(parsed.result.ast, (node) => {
			if (node.type === "element" && node.name === "script" && node.children.length && !node.attributes.some(({ name, value }) => name === "type" && /json$|importmap/i.test(value))) shared.addClientScript(code, node, parsed);
		});
		return [code, ...shared.clientScripts.map((cs) => cs.getProcessorFile(virtualFileExt))];
	}
	return [code];
}
/** postprocess */
function postprocess([messages, ...blockMessages], filename) {
	const shared = terminateShared(filename);
	if (shared) return messages.concat(...blockMessages.map((m, i) => shared.clientScripts[i].remapMessages(m)));
	return messages;
}
//#endregion
//#region src/plugin.ts
let _plugin;
/**
* Get ESLint Plugin object
*/
function getPlugin() {
	const rules$1 = rules.reduce((obj, r) => {
		obj[r.meta.docs.ruleName] = r;
		return obj;
	}, {});
	return _plugin ??= {
		meta: {
			name,
			version
		},
		environments,
		rules: rules$1,
		processors: {
			".astro": astroProcessor,
			astro: astroProcessor,
			"client-side-ts": clientSideTsProcessor
		}
	};
}
//#endregion
//#region src/configs/flat/base.ts
var base_default = [
	{
		name: "astro/base/plugin",
		plugins: { get astro() {
			return getPlugin();
		} }
	},
	{
		name: "astro/base",
		files: ["*.astro", "**/*.astro"],
		languageOptions: {
			globals: {
				...globals.default.node,
				...environments.astro.globals
			},
			parser: astro_eslint_parser,
			sourceType: "module",
			parserOptions: {
				parser: tsESLintParser ?? void 0,
				extraFileExtensions: [".astro"]
			}
		},
		rules: {},
		processor: hasTypescriptEslintParser ? "astro/client-side-ts" : "astro/astro"
	},
	{
		name: "astro/base/javascript",
		files: ["**/*.astro/*.js", "*.astro/*.js"],
		languageOptions: {
			globals: { ...globals.default.browser },
			sourceType: "module"
		},
		rules: { "prettier/prettier": "off" }
	},
	{
		name: "astro/base/typescript",
		files: ["**/*.astro/*.ts", "*.astro/*.ts"],
		languageOptions: {
			globals: { ...globals.default.browser },
			parser: tsESLintParser ?? void 0,
			sourceType: "module",
			parserOptions: { project: null }
		},
		rules: { "prettier/prettier": "off" }
	}
];
//#endregion
//#region src/a11y/configs.ts
/** Build a11y configs */
function buildFlatConfigs() {
	const configs = {};
	for (const configName of a11yConfigKeys) Object.defineProperty(configs, `jsx-a11y-${configName}`, {
		enumerable: true,
		get() {
			const base = getPluginJsxA11y();
			const baseRules = (base?.configs?.[configName] ?? {}).rules ?? {};
			const newRules = {};
			for (const ruleName of Object.keys(baseRules)) newRules[`astro/${ruleName}`] = baseRules[ruleName];
			return [...base_default, {
				plugins: { "jsx-a11y": base },
				rules: newRules
			}];
		}
	});
	return configs;
}
/** Build a11y configs */
function buildLegacyConfigs() {
	const baseExtend = "plugin:astro/base";
	const configs = {};
	for (const configName of a11yConfigKeys) Object.defineProperty(configs, `jsx-a11y-${configName}`, {
		enumerable: true,
		get() {
			const baseConfig = getPluginJsxA11y()?.configs?.[configName] ?? {};
			const baseRules = baseConfig.rules ?? {};
			const newRules = {};
			for (const ruleName of Object.keys(baseRules)) newRules[`astro/${ruleName}`] = baseRules[ruleName];
			return {
				...baseConfig,
				plugins: ["jsx-a11y"],
				extends: [baseExtend],
				rules: newRules
			};
		}
	});
	return configs;
}
//#endregion
//#region src/a11y/rules.ts
const TYPE_MAP = {
	AstroRawText: "JSXText",
	AstroTemplateLiteralAttribute: "JSXAttribute",
	AstroShorthandAttribute: "JSXAttribute"
};
const ATTRIBUTE_MAP = {
	"set:html": "dangerouslySetInnerHTML",
	"set:text": "children",
	autofocus: "autoFocus",
	for: "htmlFor"
};
/** Get `eslint-plugin-jsx-a11y` rule. */
function getPluginJsxA11yRule(ruleName) {
	return getPluginJsxA11y()?.rules?.[ruleName];
}
/** Build a11y rules */
function buildRules() {
	const rules = [];
	for (const ruleKey of a11yRuleKeys) {
		const jsxRuleName = `jsx-a11y/${ruleKey}`;
		const astroRuleName = `astro/${jsxRuleName}`;
		const ruleWithoutMeta = createRule(jsxRuleName, {
			meta: {
				messages: {},
				schema: [],
				type: "problem",
				docs: {
					description: `apply \`${jsxRuleName}\` rule to Astro components`,
					category: "A11Y Extension Rules",
					recommended: false,
					available: () => Boolean(getPluginJsxA11y())
				}
			},
			create(context) {
				const baseRule = getPluginJsxA11yRule(ruleKey);
				if (!baseRule) {
					context.report({
						loc: {
							line: 0,
							column: 0
						},
						message: `If you want to use ${astroRuleName} rule, you need to install eslint-plugin-jsx-a11y.`
					});
					return {};
				}
				return defineWrapperListener(baseRule, context);
			}
		});
		const docs = {
			...ruleWithoutMeta.meta.docs,
			extensionRule: {
				plugin: "eslint-plugin-jsx-a11y",
				get url() {
					return getPluginJsxA11yRule(ruleKey)?.meta?.docs?.url ?? `https://github.com/jsx-eslint/eslint-plugin-jsx-a11y/blob/main/docs/rules/${ruleKey}.md`;
				}
			}
		};
		const newRule = {
			meta: new Proxy(ruleWithoutMeta.meta, { get(_t, key) {
				if (key === "docs") return docs;
				return (getPluginJsxA11yRule(ruleKey)?.meta)?.[key] ?? ruleWithoutMeta.meta[key];
			} }),
			create: ruleWithoutMeta.create
		};
		rules.push(newRule);
	}
	return rules;
}
/**
* Define the wrapped plugin rule.
*/
function defineWrapperListener(coreRule, context) {
	if (!getSourceCode(context).parserServices?.isAstro) return {};
	const listener = coreRule.create(context);
	const astroListener = {};
	for (const key of Object.keys(listener)) {
		const original = listener[key];
		if (!original) continue;
		const wrappedListener = function(node, ...args) {
			original.call(this, getProxyNode(node), ...args);
		};
		astroListener[key] = wrappedListener;
		const astroKey = key.replace(/(?:^|\b)AstroRawText(?:\b|$)/gu, "JSXText").replace(/(?:^|\b)(?:AstroTemplateLiteralAttribute|AstroShorthandAttribute)(?:\b|$)/gu, "JSXAttribute");
		if (astroKey !== key) astroListener[astroKey] = wrappedListener;
	}
	/**
	*  Check whether a given value is a node.
	*/
	function isNode(data) {
		return data && typeof data.type === "string" && Array.isArray(data.range) && data.range.length === 2 && typeof data.range[0] === "number" && typeof data.range[1] === "number";
	}
	/**
	* Get the proxy node
	*/
	function getProxyNode(node, overrides) {
		const cache = {
			type: TYPE_MAP[node.type] || node.type,
			...overrides ?? {}
		};
		if (node.type === "JSXAttribute") {
			const attrName = getAttributeName(node);
			const converted = attrName != null && ATTRIBUTE_MAP[attrName];
			if (converted) cache.name = getProxyNode(node.name, {
				type: "JSXIdentifier",
				namespace: null,
				name: converted
			});
		}
		return new Proxy(node, { get(_t, key) {
			if (key in cache) return cache[key];
			const data = node[key];
			if (isNode(data)) return cache[key] = getProxyNode(data);
			if (Array.isArray(data)) return cache[key] = data.map((e) => isNode(e) ? getProxyNode(e) : e);
			return data;
		} });
	}
	return astroListener;
}
//#endregion
//#region src/a11y/index.ts
/** Build a11y rules */
function buildA11yRules() {
	return buildRules();
}
/** Build a11y configs */
function buildA11yFlatConfigs() {
	return buildFlatConfigs();
}
/** Build a11y configs */
function buildA11yLegacyConfigs() {
	return buildLegacyConfigs();
}
const rules = [...[
	missing_client_only_directive_value_default,
	no_conflict_set_directives_default,
	no_deprecated_astro_canonicalurl_default,
	no_deprecated_astro_fetchcontent_default,
	no_deprecated_astro_resolve_default,
	no_deprecated_getentrybyslug_default,
	no_exports_from_components_default,
	rule,
	no_set_html_directive_default,
	no_set_text_directive_default,
	no_unsafe_inline_scripts_default,
	no_unused_css_selector_default,
	no_unused_define_vars_in_style_default,
	prefer_class_list_directive_default,
	prefer_object_class_list_default,
	prefer_split_class_list_default,
	semi_default,
	sort_attributes_default,
	valid_compile_default
], ...buildA11yRules()];
//#endregion
//#region src/configs/all.ts
const all$1 = {};
for (const rule of rules.filter((rule) => rule.meta.docs.available() && !rule.meta.deprecated)) all$1[rule.meta.docs.ruleId] = "error";
var all_default$1 = {
	extends: recommended_default$1.extends,
	rules: {
		...all$1,
		...recommended_default$1.rules
	}
};
//#endregion
//#region src/configs/flat/recommended.ts
var recommended_default = [...base_default, {
	name: "astro/recommended",
	rules: {
		"astro/missing-client-only-directive-value": "error",
		"astro/no-conflict-set-directives": "error",
		"astro/no-deprecated-astro-canonicalurl": "error",
		"astro/no-deprecated-astro-fetchcontent": "error",
		"astro/no-deprecated-astro-resolve": "error",
		"astro/no-deprecated-getentrybyslug": "error",
		"astro/no-unused-define-vars-in-style": "error",
		"astro/valid-compile": "error"
	}
}];
//#endregion
//#region src/configs/flat/all.ts
const all = {};
for (const rule of rules.filter((rule) => rule.meta.docs.available() && !rule.meta.deprecated)) all[rule.meta.docs.ruleId] = "error";
var all_default = [...recommended_default, { rules: {
	...all,
	...recommended_default[recommended_default.length - 1].rules
} }];
//#endregion
//#region src/cjs-config-builder.ts
/**
* Build configs for CJS Module
*/
function buildCjsConfigs() {
	const cjsConfigs = {
		base: buildLegacyBase(),
		recommended: recommended_default$1,
		all: all_default$1,
		"jsx-a11y-strict": null,
		"jsx-a11y-recommended": null,
		"flat/base": base_default,
		"flat/recommended": recommended_default,
		"flat/all": all_default,
		"flat/jsx-a11y-strict": null,
		"flat/jsx-a11y-recommended": null
	};
	const a11yFlatConfigs = buildA11yFlatConfigs();
	for (const configName of Object.keys(a11yFlatConfigs)) Object.defineProperty(cjsConfigs, `flat/${configName}`, {
		enumerable: true,
		get() {
			return a11yFlatConfigs[configName];
		}
	});
	const a11yLegacyConfigs = buildA11yLegacyConfigs();
	for (const configName of Object.keys(a11yLegacyConfigs)) Object.defineProperty(cjsConfigs, configName, {
		enumerable: true,
		get() {
			return a11yLegacyConfigs[configName];
		}
	});
	return cjsConfigs;
}
//#endregion
//#region src/index.cts
const plugin = getPlugin();
const configs = buildCjsConfigs();
module.exports = Object.assign(plugin, { configs });
//#endregion
