"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromSpreadElement;
/**
 * Extractor function for a SpreadElement type value node. We can't statically
 * evaluate an array spread, so just return undefined.
 */
function extractValueFromSpreadElement() {
  //
}