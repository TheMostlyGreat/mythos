import { collectPropertyValues } from '../../typescript/ast-helpers.js';
export const getPageExtensions = (program) => Array.from(collectPropertyValues(program, 'pageExtensions'));
