"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = elementType;
function resolveMemberExpressions() {
  var object = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
  var property = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};
  if (object.type === 'JSXMemberExpression') {
    return "".concat(resolveMemberExpressions(object.object, object.property), ".").concat(property.name);
  }
  return "".concat(object.name, ".").concat(property.name);
}

/**
 * Returns the tagName associated with a JSXElement.
 *
 * @param node
 */
function elementType() {
  var node = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
  var name = node.name;
  if (node.type === 'JSXOpeningFragment') {
    return '<>';
  }
  if (!name) {
    throw new Error('The argument provided is not a JSXElement node.');
  }
  if (name.type === 'JSXMemberExpression') {
    var _name$object = name.object,
      object = _name$object === void 0 ? {} : _name$object,
      _name$property = name.property,
      property = _name$property === void 0 ? {} : _name$property;
    return resolveMemberExpressions(object, property);
  }
  if (name.type === 'JSXNamespacedName') {
    return "".concat(name.namespace.name, ":").concat(name.name.name);
  }
  return node.name.name;
}