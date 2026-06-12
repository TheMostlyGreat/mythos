"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromMemberExpression;
/**
 * Extractor function for a MemberExpression type value node. A member
 * expression is accessing a property on an object `obj.property`.
 *
 * @param value Value - AST Value object with type `MemberExpression`
 * @returns - The extracted value converted to correct type and maintaining
 *   `obj.property` convention.
 */
function extractValueFromMemberExpression(value) {
  var getValue = require('.')["default"];
  return "".concat(getValue(value.object)).concat(value.optional ? '?.' : '.').concat(getValue(value.property));
}