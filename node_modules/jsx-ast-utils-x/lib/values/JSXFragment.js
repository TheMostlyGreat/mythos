"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromJSXFragment;
/**
 * Extractor function for a JSXFragment type value node.
 *
 * Returns self-closing element with correct name.
 *
 * @param value
 */
function extractValueFromJSXFragment(value) {
  var getValue = require('.')["default"];
  if (value.children.length === 0) {
    return '<></>';
  }
  return "<>".concat([value.children].flat().map(function (x) {
    return getValue(x);
  }).join(''), "</>");
}