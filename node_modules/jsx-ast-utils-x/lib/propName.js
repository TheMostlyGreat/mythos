"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = propName;
/**
 * Returns the name of the prop given the JSXAttribute object.
 *
 * @param prop
 */
function propName() {
  var prop = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
  if (!prop.type || prop.type !== 'JSXAttribute') {
    throw new Error('The prop must be a JSXAttribute collected by the AST parser.');
  }
  if (prop.name.type === 'JSXNamespacedName') {
    return "".concat(prop.name.namespace.name, ":").concat(prop.name.name.name);
  }
  return prop.name.name;
}