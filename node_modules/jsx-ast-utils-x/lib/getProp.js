"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports["default"] = getProp;
var _propName = _interopRequireDefault(require("./propName"));
var _excluded = ["expressions", "quasis"],
  _excluded2 = ["loc"];
function _interopRequireDefault(e) { return e && e.__esModule ? e : { "default": e }; }
function _typeof(o) { "@babel/helpers - typeof"; return _typeof = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (o) { return typeof o; } : function (o) { return o && "function" == typeof Symbol && o.constructor === Symbol && o !== Symbol.prototype ? "symbol" : typeof o; }, _typeof(o); }
function _objectWithoutProperties(e, t) { if (null == e) return {}; var o, r, i = _objectWithoutPropertiesLoose(e, t); if (Object.getOwnPropertySymbols) { var n = Object.getOwnPropertySymbols(e); for (r = 0; r < n.length; r++) o = n[r], -1 === t.indexOf(o) && {}.propertyIsEnumerable.call(e, o) && (i[o] = e[o]); } return i; }
function _objectWithoutPropertiesLoose(r, e) { if (null == r) return {}; var t = {}; for (var n in r) if ({}.hasOwnProperty.call(r, n)) { if (-1 !== e.indexOf(n)) continue; t[n] = r[n]; } return t; }
function _slicedToArray(r, e) { return _arrayWithHoles(r) || _iterableToArrayLimit(r, e) || _unsupportedIterableToArray(r, e) || _nonIterableRest(); }
function _nonIterableRest() { throw new TypeError("Invalid attempt to destructure non-iterable instance.\nIn order to be iterable, non-array objects must have a [Symbol.iterator]() method."); }
function _unsupportedIterableToArray(r, a) { if (r) { if ("string" == typeof r) return _arrayLikeToArray(r, a); var t = {}.toString.call(r).slice(8, -1); return "Object" === t && r.constructor && (t = r.constructor.name), "Map" === t || "Set" === t ? Array.from(r) : "Arguments" === t || /^(?:Ui|I)nt(?:8|16|32)(?:Clamped)?Array$/.test(t) ? _arrayLikeToArray(r, a) : void 0; } }
function _arrayLikeToArray(r, a) { (null == a || a > r.length) && (a = r.length); for (var e = 0, n = Array(a); e < a; e++) n[e] = r[e]; return n; }
function _iterableToArrayLimit(r, l) { var t = null == r ? null : "undefined" != typeof Symbol && r[Symbol.iterator] || r["@@iterator"]; if (null != t) { var e, n, i, u, a = [], f = !0, o = !1; try { if (i = (t = t.call(r)).next, 0 === l) { if (Object(t) !== t) return; f = !1; } else for (; !(f = (e = i.call(t)).done) && (a.push(e.value), a.length !== l); f = !0); } catch (r) { o = !0, n = r; } finally { try { if (!f && null != t["return"] && (u = t["return"](), Object(u) !== u)) return; } finally { if (o) throw n; } } return a; } }
function _arrayWithHoles(r) { if (Array.isArray(r)) return r; }
function ownKeys(e, r) { var t = Object.keys(e); if (Object.getOwnPropertySymbols) { var o = Object.getOwnPropertySymbols(e); r && (o = o.filter(function (r) { return Object.getOwnPropertyDescriptor(e, r).enumerable; })), t.push.apply(t, o); } return t; }
function _objectSpread(e) { for (var r = 1; r < arguments.length; r++) { var t = null != arguments[r] ? arguments[r] : {}; r % 2 ? ownKeys(Object(t), !0).forEach(function (r) { _defineProperty(e, r, t[r]); }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(t)) : ownKeys(Object(t)).forEach(function (r) { Object.defineProperty(e, r, Object.getOwnPropertyDescriptor(t, r)); }); } return e; }
function _defineProperty(e, r, t) { return (r = _toPropertyKey(r)) in e ? Object.defineProperty(e, r, { value: t, enumerable: !0, configurable: !0, writable: !0 }) : e[r] = t, e; }
function _toPropertyKey(t) { var i = _toPrimitive(t, "string"); return "symbol" == _typeof(i) ? i : i + ""; }
function _toPrimitive(t, r) { if ("object" != _typeof(t) || !t) return t; var e = t[Symbol.toPrimitive]; if (void 0 !== e) { var i = e.call(t, r || "default"); if ("object" != _typeof(i)) return i; throw new TypeError("@@toPrimitive must return a primitive value."); } return ("string" === r ? String : Number)(t); }
var DEFAULT_OPTIONS = {
  ignoreCase: true
};

/**
 * Returns the JSXAttribute itself or undefined, indicating the prop is not
 * present on the JSXOpeningElement.
 *
 * @param props
 * @param prop
 * @param options
 */
function getProp() {
  var props = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : [];
  var prop = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : '';
  var options = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : DEFAULT_OPTIONS;
  function getName(name) {
    return options.ignoreCase ? name.toUpperCase() : name;
  }
  var propToFind = getName(prop);
  function isPropToFind(property) {
    return property.type === 'Property' && property.key.type === 'Identifier' && propToFind === getName(property.key.name);
  }
  var foundAttribute = props.find(function (attribute) {
    // If the props contain a spread prop, try to find the property in the object expression.
    if (attribute.type === 'JSXSpreadAttribute') {
      return attribute.argument.type === 'ObjectExpression' && propToFind !== getName('key') &&
      // https://github.com/reactjs/rfcs/pull/107
      attribute.argument.properties.some(isPropToFind);
    }
    return propToFind === getName((0, _propName["default"])(attribute));
  });
  if (foundAttribute && foundAttribute.type === 'JSXSpreadAttribute') {
    return propertyToJSXAttribute(foundAttribute.argument.properties.find(isPropToFind));
  }
  return foundAttribute;
}
function propertyToJSXAttribute(node) {
  var key = node.key,
    value = node.value;
  return _objectSpread({
    type: 'JSXAttribute',
    name: _objectSpread({
      type: 'JSXIdentifier',
      name: key.name
    }, getBaseProps(key)),
    value: value.type === 'Literal' ? adjustRangeOfNode(value) : _objectSpread({
      type: 'JSXExpressionContainer',
      expression: adjustExpressionRange(value)
    }, getBaseProps(value))
  }, getBaseProps(node));
}
function adjustRangeOfNode(node) {
  var _ref = node.range || [node.start, node.end],
    _ref2 = _slicedToArray(_ref, 2),
    start = _ref2[0],
    end = _ref2[1];
  return _objectSpread(_objectSpread({}, node), {}, {
    end: undefined,
    range: [start, end],
    start: undefined
  });
}
function adjustExpressionRange(_ref3) {
  var expressions = _ref3.expressions,
    quasis = _ref3.quasis,
    expression = _objectWithoutProperties(_ref3, _excluded);
  return _objectSpread(_objectSpread(_objectSpread({}, adjustRangeOfNode(expression)), expressions ? {
    expressions: expressions.map(adjustRangeOfNode)
  } : {}), quasis ? {
    quasis: quasis.map(adjustRangeOfNode)
  } : {});
}
function getBaseProps(_ref4) {
  var loc = _ref4.loc,
    node = _objectWithoutProperties(_ref4, _excluded2);
  var _adjustRangeOfNode = adjustRangeOfNode(node),
    range = _adjustRangeOfNode.range;
  return {
    loc: getBaseLocation(loc),
    range: range
  };
}
function getBaseLocation(_ref5) {
  var start = _ref5.start,
    end = _ref5.end,
    source = _ref5.source,
    filename = _ref5.filename;
  return _objectSpread(_objectSpread({
    start: start,
    end: end
  }, source === undefined ? {} : {
    source: source
  }), filename === undefined ? {} : {
    filename: filename
  });
}