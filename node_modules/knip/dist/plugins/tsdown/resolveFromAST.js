import { collectPropertyValues } from '../../typescript/ast-helpers.js';
export const getEntryFromAST = (program) => {
    return collectPropertyValues(program, 'entry');
};
