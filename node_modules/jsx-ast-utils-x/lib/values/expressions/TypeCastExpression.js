"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromTypeCastExpression;
/**
 * Extractor function for a TypeCastExpression type value node. A type cast
 * expression looks like `(this.handleClick: (event: MouseEvent) => void))` This
 * will return the expression `this.handleClick`.
 *
 * @param value Value - AST Value object with type `TypeCastExpression`
 * @returns - The extracted value converted to correct type.
 */
function extractValueFromTypeCastExpression(value) {
  var getValue = require('.')["default"];
  return getValue(value.expression);
}