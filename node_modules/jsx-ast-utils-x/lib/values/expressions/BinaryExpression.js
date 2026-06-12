"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = extractValueFromBinaryExpression;
/**
 * Extractor function for a BinaryExpression type value node. A binary
 * expression has a left and right side separated by an operator such as `a +
 * b`.
 *
 * @param value Value - AST Value object with type `BinaryExpression`
 * @returns - The extracted value converted to correct type.
 */
function extractValueFromBinaryExpression(value) {
  var getValue = require('.')["default"];
  var operator = value.operator,
    left = value.left,
    right = value.right;
  var leftVal = getValue(left);
  var rightVal = getValue(right);
  switch (operator) {
    case '==':
      {
        return leftVal == rightVal;
      }
    case '!=':
      {
        return leftVal != rightVal;
      }
    case '===':
      {
        return leftVal === rightVal;
      }
    case '!==':
      {
        return leftVal !== rightVal;
      }
    case '<':
      {
        return leftVal < rightVal;
      }
    case '<=':
      {
        return leftVal <= rightVal;
      }
    case '>':
      {
        return leftVal > rightVal;
      }
    case '>=':
      {
        return leftVal >= rightVal;
      }
    case '<<':
      {
        return leftVal << rightVal;
      }
    case '>>':
      {
        return leftVal >> rightVal;
      }
    case '>>>':
      {
        return leftVal >>> rightVal;
      }
    case '+':
      {
        return leftVal + rightVal;
      }
    case '-':
      {
        return leftVal - rightVal;
      }
    case '*':
      {
        return leftVal * rightVal;
      }
    case '/':
      {
        return leftVal / rightVal;
      }
    case '%':
      {
        return leftVal % rightVal;
      }
    case '|':
      {
        return leftVal | rightVal;
      }
    case '^':
      {
        return leftVal ^ rightVal;
      }
    case '&':
      {
        return leftVal & rightVal;
      }
    case 'in':
      {
        try {
          return leftVal in rightVal;
        } catch (_unused) {
          return false;
        }
      }
    case 'instanceof':
      {
        if (typeof rightVal !== 'function') {
          return false;
        }
        return leftVal instanceof rightVal;
      }
    default:
      {
        return;
      }
  }
}