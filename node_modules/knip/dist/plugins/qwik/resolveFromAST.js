import { findCallArg, getPropertyValues } from '../../typescript/ast-helpers.js';
export const getSrcDir = (program) => {
    const arg = findCallArg(program, 'qwikVite');
    if (arg) {
        const values = getPropertyValues(arg, 'srcDir');
        if (values.size > 0)
            return Array.from(values)[0];
    }
    return 'src';
};
export const getRoutesDirs = (program, srcDir) => {
    const arg = findCallArg(program, 'qwikCity');
    if (arg) {
        const values = Array.from(getPropertyValues(arg, 'routesDir')).filter(Boolean);
        if (values.length > 0)
            return values;
    }
    return [`${srcDir}/routes`];
};
