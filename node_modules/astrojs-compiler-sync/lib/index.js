import createCompilerSync from "./compiler-sync.cjs";

const workerPath = new URL("./astrojs-compiler-worker.js", import.meta.url);

const compilerSync = createCompilerSync(workerPath);

export function parse(...args) {
  return compilerSync("parse", ...args);
}
export function transform(...args) {
  return compilerSync("transform", ...args);
}
export function convertToTSX(...args) {
  return compilerSync("convertToTSX", ...args);
}
export function compile(...args) {
  return compilerSync("compile", ...args);
}
