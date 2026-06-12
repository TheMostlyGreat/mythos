"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromUnaryExpression;
/**
 * Extractor function for a UnaryExpression type value node. A unary expression
 * is an expression with a unary operator. For example, !"foobar" will evaluate
 * to false, so this will return false.
 *
 * @param value Value - AST Value object with type `UnaryExpression`
 * @returns - The extracted value converted to correct type.
 */
function extractValueFromUnaryExpression(value) {
  var getValue = require('.')["default"];
  var operator = value.operator,
    argument = value.argument;
  switch (operator) {
    case '-':
      {
        return -getValue(argument);
      }
    case '+':
      {
        return +getValue(argument);
      }
    case '!':
      {
        return !getValue(argument);
      }
    case '~':
      {
        return ~getValue(argument);
      }
    case 'delete':
      {
        // I believe delete statements evaluate to true.
        return true;
      }
    // eslint-disable-next-line unicorn-x/no-useless-switch-case
    case 'typeof':
    // eslint-disable-next-line unicorn-x/no-useless-switch-case, no-fallthrough
    case 'void':
    default:
      {
        return;
      }
  }
}