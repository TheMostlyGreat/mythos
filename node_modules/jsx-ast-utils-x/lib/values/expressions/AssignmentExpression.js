"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromAssignmentExpression;
/**
 * Extractor function for an AssignmentExpression type value node. An assignment
 * expression looks like `x = y` or `x += y` in expression position. This will
 * return the assignment as the value.
 *
 * @param value Value - AST Value object with type `AssignmentExpression`
 * @returns - The extracted value converted to correct type.
 */
function extractValueFromAssignmentExpression(value) {
  var getValue = require('.')["default"];
  return "".concat(getValue(value.left), " ").concat(value.operator, " ").concat(getValue(value.right));
}