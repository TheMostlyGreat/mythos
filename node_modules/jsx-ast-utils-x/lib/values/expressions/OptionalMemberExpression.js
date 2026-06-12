"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromOptionalMemberExpression;
/**
 * Extractor function for a OptionalMemberExpression type value node. A member
 * expression is accessing a property on an object `obj.property`.
 *
 * @param value Value - AST Value object with type `OptionalMemberExpression`
 * @returns - The extracted value converted to correct type and maintaining
 *   `obj?.property` convention.
 */
function extractValueFromOptionalMemberExpression(value) {
  var getValue = require('.')["default"];
  return "".concat(getValue(value.object), "?.").concat(getValue(value.property));
}