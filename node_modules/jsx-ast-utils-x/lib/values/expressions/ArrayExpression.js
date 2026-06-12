"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromArrayExpression;
/**
 * Extractor function for an ArrayExpression type value node. An array
 * expression is an expression with [] syntax.
 *
 * @param value
 * @returns - An array of the extracted elements.
 */
function extractValueFromArrayExpression(value) {
  var getValue = require('.')["default"];
  return value.elements.map(function (element) {
    if (element === null) {
      return;
    }
    return getValue(element);
  });
}