"use strict";

function _typeof(o) { "@babel/helpers - typeof"; return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, _typeof(o); }
Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = getPropValue;
exports.getLiteralPropValue = getLiteralPropValue;
var _values = _interopRequireWildcard(require("./values"));
function _interopRequireWildcard(e, t) { if ("function" == typeof WeakMap) var r = new WeakMap(), n = new WeakMap(); return (_interopRequireWildcard = function _interopRequireWildcard(e, t) { if (!t && e && e.__esModule) return e; var o, i, f = { __proto__: null, "default": e }; if (null === e || "object" != _typeof(e) && "function" != typeof e) return f; if (o = t ? n : r) { if (o.has(e)) return o.get(e); o.set(e, f); } for (var _t in e) "default" !== _t && {}.hasOwnProperty.call(e, _t) && ((i = (o = Object.defineProperty) && Object.getOwnPropertyDescriptor(e, _t)) && (i.get || i.set) ? o(f, _t, i) : f[_t] = e[_t]); return f; })(e, t); }
var extractValue = function extractValue(attribute, extractor) {
  if (attribute && attribute.type === 'JSXAttribute') {
    if (attribute.value === null) {
      // Null valued attributes imply truthiness.
      // For example: <div aria-hidden />
      // See: https://facebook.github.io/react/docs/jsx-in-depth.html#boolean-attributes
      return true;
    }
    return extractor(attribute.value);
  }
};

/**
 * Returns the value of a given attribute. Different types of attributes have
 * their associated values in different properties on the object.
 *
 * This function should return the most _closely_ associated value with the
 * intention of the JSX.
 *
 * @param attribute - The JSXAttribute collected by AST parser.
 */
function getPropValue(attribute) {
  return extractValue(attribute, _values["default"]);
}

/**
 * Returns the value of a given attribute. Different types of attributes have
 * their associated values in different properties on the object.
 *
 * This function should return a value only if we can extract a literal value
 * from its attribute (i.e. values that have generic types in JavaScript -
 * strings, numbers, booleans, etc.)
 *
 * @param attribute - The JSXAttribute collected by AST parser.
 */
function getLiteralPropValue(attribute) {
  return extractValue(attribute, _values.getLiteralValue);
}