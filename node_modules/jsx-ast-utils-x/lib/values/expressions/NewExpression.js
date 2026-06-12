"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromNewExpression;
/**
 * Extractor function for a NewExpression type value node. A new expression
 * instantiates an object with `new` keyword.
 *
 * @returns - An empty object.
 */
function extractValueFromNewExpression() {
  return new Object();
}