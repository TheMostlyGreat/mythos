"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromLiteral;
/**
 * Extractor function for a Literal type value node.
 *
 * @param value Value - AST Value object with type `Literal`
 * @returns {string | boolean} - The extracted value converted to correct type.
 */
function extractValueFromLiteral(value) {
  var extractedValue = value.value;
  var normalizedStringValue = typeof extractedValue === 'string' && extractedValue.toLowerCase();
  if (normalizedStringValue === 'true') {
    return true;
  }
  if (normalizedStringValue === 'false') {
    return false;
  }
  return extractedValue;
}