"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromTaggedTemplateExpression;
var _TemplateLiteral = _interopRequireDefault(require("./TemplateLiteral"));
function _interopRequireDefault(e) { return e && e.__esModule ? e : { "default": e }; }
/**
 * Returns the string value of a tagged template literal object. Redirects the
 * bulk of the work to `TemplateLiteral`.
 *
 * @param value
 */
function extractValueFromTaggedTemplateExpression(value) {
  return (0, _TemplateLiteral["default"])(value.quasi);
}