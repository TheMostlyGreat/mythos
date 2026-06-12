"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = getValue;
exports.getLiteralValue = getLiteralValue;
var _JSXElement = _interopRequireDefault(require("./JSXElement"));
var _JSXFragment = _interopRequireDefault(require("./JSXFragment"));
var _JSXText = _interopRequireDefault(require("./JSXText"));
var _Literal = _interopRequireDefault(require("./Literal"));
var _expressions = _interopRequireWildcard(require("./expressions"));
function _interopRequireWildcard(e, t) { if ("function" == typeof WeakMap) var r = new WeakMap(), n = new WeakMap(); return (_interopRequireWildcard = function _interopRequireWildcard(e, t) { if (!t && e && e.__esModule) return e; var o, i, f = { __proto__: null, "default": e }; if (null === e || "object" != _typeof(e) && "function" != typeof e) return f; if (o = t ? n : r) { if (o.has(e)) return o.get(e); o.set(e, f); } for (var _t in e) "default" !== _t && {}.hasOwnProperty.call(e, _t) && ((i = (o = Object.defineProperty) && Object.getOwnPropertyDescriptor(e, _t)) && (i.get || i.set) ? o(f, _t, i) : f[_t] = e[_t]); return f; })(e, t); }
function _interopRequireDefault(e) { return e && e.__esModule ? e : { "default": e }; }
function _typeof(o) { "@babel/helpers - typeof"; return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, _typeof(o); }
function ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function _objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach(function (r) { _defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function _defineProperty(e, r, t) { return (r = _toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: !0, configurable: !0, writable: !0 }) : e[r] = t, e; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == _typeof(i) ? i : i + ""; }
function _toPrimitive(t, r) { if ("object" != _typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != _typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
// Composition map of types to their extractor functions.
var TYPES = {
  Literal: _Literal["default"],
  JSXElement: _JSXElement["default"],
  JSXExpressionContainer: _expressions["default"],
  JSXText: _JSXText["default"],
  JSXFragment: _JSXFragment["default"]
};

// Composition map of types to their extractor functions to handle literals.
var LITERAL_TYPES = _objectSpread(_objectSpread({}, TYPES), {}, {
  JSXElement: function JSXElement() {
    return null;
  },
  JSXExpressionContainer: _expressions.extractLiteral
});

/**
 * This function maps an AST value node to its correct extractor function for
 * its given type.
 *
 * This will map correctly for _all_ possible types.
 *
 * @param value - AST Value object on a JSX Attribute.
 */
function getValue(value) {
  if (!TYPES[value.type]) {
    console.log(value.type);
  }
  return TYPES[value.type](value);
}

/**
 * This function maps an AST value node to its correct extractor function for
 * its given type.
 *
 * This will map correctly for _some_ possible types that map to literals.
 *
 * @param value - AST Value object on a JSX Attribute.
 */
function getLiteralValue(value) {
  return LITERAL_TYPES[value.type](value);
}