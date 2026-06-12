"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromJSXElement;
/**
 * Extractor function for a JSXElement type value node.
 *
 * Returns self-closing element with correct name.
 *
 * @param value
 */
function extractValueFromJSXElement(value) {
  var getValue = require('.')["default"];
  var Tag = value.openingElement.name.name;
  if (value.openingElement.selfClosing) {
    return "<".concat(Tag, " />");
  }
  return "<".concat(Tag, ">").concat([value.children].flat().map(function (x) {
    return getValue(x);
  }).join(''), "</").concat(Tag, ">");
}