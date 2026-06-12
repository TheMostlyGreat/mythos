import { collectPropertyValues } from '../../typescript/ast-helpers.js';
export const getInputFromAST = (program) => {
    return collectPropertyValues(program, 'input');
};
