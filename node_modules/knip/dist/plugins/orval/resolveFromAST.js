import { collectPropertyValues } from '../../typescript/ast-helpers.js';
const PATH_KEY = 'path';
const TRANSFORMER_KEY = 'transformer';
export const getInputsFromAST = (program) => {
    const values = new Set();
    for (const v of collectPropertyValues(program, PATH_KEY))
        values.add(v);
    for (const v of collectPropertyValues(program, TRANSFORMER_KEY))
        values.add(v);
    return values;
};
