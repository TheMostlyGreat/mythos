"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extract;
exports.extractLiteral = extractLiteral;
var _JSXElement = _interopRequireDefault(require("../JSXElement"));
var _JSXFragment = _interopRequireDefault(require("../JSXFragment"));
var _JSXText = _interopRequireDefault(require("../JSXText"));
var _Literal = _interopRequireDefault(require("../Literal"));
var _ArrayExpression = _interopRequireDefault(require("./ArrayExpression"));
var _AssignmentExpression = _interopRequireDefault(require("./AssignmentExpression"));
var _BinaryExpression = _interopRequireDefault(require("./BinaryExpression"));
var _BindExpression = _interopRequireDefault(require("./BindExpression"));
var _CallExpression = _interopRequireDefault(require("./CallExpression"));
var _ChainExpression = _interopRequireDefault(require("./ChainExpression"));
var _ConditionalExpression = _interopRequireDefault(require("./ConditionalExpression"));
var _FunctionExpression = _interopRequireDefault(require("./FunctionExpression"));
var _Identifier = _interopRequireDefault(require("./Identifier"));
var _LogicalExpression = _interopRequireDefault(require("./LogicalExpression"));
var _MemberExpression = _interopRequireDefault(require("./MemberExpression"));
var _NewExpression = _interopRequireDefault(require("./NewExpression"));
var _ObjectExpression = _interopRequireDefault(require("./ObjectExpression"));
var _OptionalCallExpression = _interopRequireDefault(require("./OptionalCallExpression"));
var _OptionalMemberExpression = _interopRequireDefault(require("./OptionalMemberExpression"));
var _SequenceExpression = _interopRequireDefault(require("./SequenceExpression"));
var _SpreadElement = _interopRequireDefault(require("./SpreadElement"));
var _TSNonNullExpression = _interopRequireDefault(require("./TSNonNullExpression"));
var _TaggedTemplateExpression = _interopRequireDefault(require("./TaggedTemplateExpression"));
var _TemplateLiteral = _interopRequireDefault(require("./TemplateLiteral"));
var _ThisExpression = _interopRequireDefault(require("./ThisExpression"));
var _TypeCastExpression = _interopRequireDefault(require("./TypeCastExpression"));
var _UnaryExpression = _interopRequireDefault(require("./UnaryExpression"));
var _UpdateExpression = _interopRequireDefault(require("./UpdateExpression"));
function _interopRequireDefault(e) { return e && e.__esModule ? e : { "default": e }; }
function _typeof(o) { "@babel/helpers - typeof"; return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, _typeof(o); }
function ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function _objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach(function (r) { _defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function _defineProperty(e, r, t) { return (r = _toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: !0, configurable: !0, writable: !0 }) : e[r] = t, e; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == _typeof(i) ? i : i + ""; }
function _toPrimitive(t, r) { if ("object" != _typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != _typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
// Composition map of types to their extractor functions.
var TYPES = {
  Identifier: _Identifier["default"],
  Literal: _Literal["default"],
  JSXElement: _JSXElement["default"],
  JSXFragment: _JSXFragment["default"],
  JSXText: _JSXText["default"],
  TaggedTemplateExpression: _TaggedTemplateExpression["default"],
  TemplateLiteral: _TemplateLiteral["default"],
  ArrowFunctionExpression: _FunctionExpression["default"],
  FunctionExpression: _FunctionExpression["default"],
  LogicalExpression: _LogicalExpression["default"],
  MemberExpression: _MemberExpression["default"],
  ChainExpression: _ChainExpression["default"],
  OptionalCallExpression: _OptionalCallExpression["default"],
  OptionalMemberExpression: _OptionalMemberExpression["default"],
  CallExpression: _CallExpression["default"],
  UnaryExpression: _UnaryExpression["default"],
  ThisExpression: _ThisExpression["default"],
  ConditionalExpression: _ConditionalExpression["default"],
  BinaryExpression: _BinaryExpression["default"],
  ObjectExpression: _ObjectExpression["default"],
  NewExpression: _NewExpression["default"],
  UpdateExpression: _UpdateExpression["default"],
  ArrayExpression: _ArrayExpression["default"],
  BindExpression: _BindExpression["default"],
  SpreadElement: _SpreadElement["default"],
  TypeCastExpression: _TypeCastExpression["default"],
  SequenceExpression: _SequenceExpression["default"],
  TSNonNullExpression: _TSNonNullExpression["default"],
  AssignmentExpression: _AssignmentExpression["default"]
};
var noop = function noop() {
  return null;
};
var errorMessage = function errorMessage(expression) {
  return "The prop value with an expression type of ".concat(expression, " could not be resolved. Please file an issue ( https://github.com/jsx-eslint/jsx-ast-utils/issues/new ) to get this fixed immediately.");
};

/**
 * This function maps an AST value node to its correct extractor function for
 * its given type.
 *
 * This will map correctly for _all_ possible expression types.
 *
 * @param value Value - AST Value object with type `JSXExpressionContainer`
 * @returns The extracted value.
 */
function extract(value) {
  // Value will not have the expression property when we recurse.
  // The type for expression on ArrowFunctionExpression is a boolean.
  var expression;
  expression = typeof value.expression !== 'boolean' && value.expression ? value.expression : value;
  var _expression = expression,
    type = _expression.type;

  // Typescript NonNull Expression is wrapped & it would end up in the wrong extractor
  if (expression.object && expression.object.type === 'TSNonNullExpression') {
    type = 'TSNonNullExpression';
  }
  while (type === 'AsExpression' || type === 'TSAsExpression') {
    var _expression2 = expression;
    type = _expression2.type;
    if (expression.expression) {
      var _expression3 = expression;
      expression = _expression3.expression;
    }
  }
  if (TYPES[type] === undefined) {
    console.error(errorMessage(type));
    return null;
  }
  return TYPES[type](expression);
}

// Composition map of types to their extractor functions to handle literals.
var LITERAL_TYPES = _objectSpread(_objectSpread({}, TYPES), {}, {
  Literal: function Literal(value) {
    var extractedVal = TYPES.Literal.call(undefined, value);
    var isNull = extractedVal === null;
    // This will be convention for attributes that have null
    // value explicitly defined (<div prop={null} /> maps to 'null').
    return isNull ? 'null' : extractedVal;
  },
  Identifier: function Identifier(value) {
    var isUndefined = TYPES.Identifier.call(undefined, value) === undefined;
    return isUndefined ? undefined : null;
  },
  JSXElement: noop,
  JSXFragment: noop,
  JSXText: noop,
  ArrowFunctionExpression: noop,
  FunctionExpression: noop,
  LogicalExpression: noop,
  MemberExpression: noop,
  OptionalCallExpression: noop,
  OptionalMemberExpression: noop,
  CallExpression: noop,
  UnaryExpression: function UnaryExpression(value) {
    var extractedVal = TYPES.UnaryExpression.call(undefined, value);
    return extractedVal === undefined ? null : extractedVal;
  },
  UpdateExpression: function UpdateExpression(value) {
    var extractedVal = TYPES.UpdateExpression.call(undefined, value);
    return extractedVal === undefined ? null : extractedVal;
  },
  ThisExpression: noop,
  ConditionalExpression: noop,
  BinaryExpression: noop,
  ObjectExpression: noop,
  NewExpression: noop,
  ArrayExpression: function ArrayExpression(value) {
    var extractedVal = TYPES.ArrayExpression.call(undefined, value);
    return extractedVal.filter(function (val) {
      return val !== null;
    });
  },
  BindExpression: noop,
  SpreadElement: noop,
  TSNonNullExpression: noop,
  TSAsExpression: noop,
  TypeCastExpression: noop,
  SequenceExpression: noop,
  ChainExpression: noop
});

/**
 * This function maps an AST value node to its correct extractor function for
 * its given type.
 *
 * This will map correctly for _some_ possible types that map to literals.
 *
 * @param value Value - AST Value object with type `JSXExpressionContainer`
 * @returns The extracted value.
 */
function extractLiteral(value) {
  // Value will not have the expression property when we recurse.
  var expression = value.expression || value;
  var type = expression.type;
  if (LITERAL_TYPES[type] === undefined) {
    console.error(errorMessage(type));
    return null;
  }
  return LITERAL_TYPES[type](expression);
}