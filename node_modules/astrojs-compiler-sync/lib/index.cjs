"use strict";

const createCompilerSync = require("./compiler-sync.cjs");

const compilerSync = createCompilerSync(
  require.resolve("./astrojs-compiler-worker.js"),
);

module.exports = {
  parse,
  transform,
  convertToTSX,
  compile,
};

function parse(...args) {
  return compilerSync("parse", ...args);
}

function transform(...args) {
  return compilerSync("transform", ...args);
}

function convertToTSX(...args) {
  return compilerSync("convertToTSX", ...args);
}

function compile(...args) {
  return compilerSync("compile", ...args);
}
