"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromTSNonNullExpression;
var extractValueFromCallExpression = require('./CallExpression')["default"];
var extractValueFromThisExpression = require('./ThisExpression')["default"];
function navigate(obj, prop, value) {
  if (value.computed) {
    return value.optional ? "".concat(obj, "?.[").concat(prop, "]") : "".concat(obj, "[").concat(prop, "]");
  }
  return value.optional ? "".concat(obj, "?.").concat(prop) : "".concat(obj, ".").concat(prop);
}

/**
 * Extractor function for a TSNonNullExpression type value node. A
 * TSNonNullExpression is accessing a TypeScript Non-Null Assertion Operator !
 *
 * @param value Value - AST Value object with type `TSNonNullExpression`
 * @returns - The extracted value converted to correct type and maintaining
 *   `obj.property` convention.
 */
// eslint-disable-next-line sonarjs/cognitive-complexity
function extractValueFromTSNonNullExpression(value) {
  var errorMessage = 'The prop value with an expression type of TSNonNullExpression could not be resolved. Please file an issue ( https://github.com/jsx-eslint/jsx-ast-utils/issues/new ) to get this fixed immediately.';

  // it's just the name
  if (value.type === 'Identifier') {
    var name = value.name;
    return name;
  }
  if (value.type === 'Literal') {
    return value.value;
  }
  if (value.type === 'TSAsExpression') {
    return extractValueFromTSNonNullExpression(value.expression);
  }
  if (value.type === 'CallExpression') {
    return extractValueFromCallExpression(value);
  }
  if (value.type === 'ThisExpression') {
    return extractValueFromThisExpression();
  }

  // does not contains properties & is not parenthesized
  if (value.type === 'TSNonNullExpression' && (!value.extra || value.extra.parenthesized === false)) {
    var expression = value.expression;
    return "".concat(extractValueFromTSNonNullExpression(expression), '!');
  }

  // does not contains properties & is parenthesized
  if (value.type === 'TSNonNullExpression' && value.extra && value.extra.parenthesized === true) {
    var _expression = value.expression;
    return '('.concat(extractValueFromTSNonNullExpression(_expression), '!', ')');
  }
  if (value.type === 'MemberExpression') {
    // contains a property & is not parenthesized
    if (!value.extra || value.extra.parenthesized === false) {
      return navigate(extractValueFromTSNonNullExpression(value.object), extractValueFromTSNonNullExpression(value.property), value);
    }

    // contains a property & is parenthesized
    if (value.extra && value.extra.parenthesized === true) {
      var result = navigate(extractValueFromTSNonNullExpression(value.object), extractValueFromTSNonNullExpression(value.property), value);
      return "(".concat(result, ")");
    }
  }

  // try to fail silently, if specs for TSNonNullExpression change
  // not throw, only log error. Similar to how it was done previously
  if (value.expression) {
    var _expression2 = value.expression;
    while (_expression2) {
      if (_expression2.type === 'Identifier') {
        console.error(errorMessage);
        return _expression2.name;
      }
      var _expression3 = _expression2;
      _expression2 = _expression3.expression;
    }
  }
  console.error(errorMessage);
  return '';
}