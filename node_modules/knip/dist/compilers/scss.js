import { basename, dirname } from '../util/path.js';
const condition = (hasDependency) => hasDependency('sass') || hasDependency('sass-embedded') || hasDependency('node-sass');
const importMatcher = /@(?:use|import|forward)\s+['"](pkg:)?([^'"]+)['"]/g;
const isAlias = (s) => (s.charCodeAt(0) === 64 && s.charCodeAt(1) === 47) || s.charCodeAt(0) === 126 || s.charCodeAt(0) === 35;
const candidates = (specifier) => {
    const spec = specifier.startsWith('.') || isAlias(specifier) ? specifier : `./${specifier}`;
    const name = basename(spec);
    const dir = dirname(spec);
    const hasExt = name.endsWith('.scss') || name.endsWith('.sass');
    const bases = hasExt ? [name] : [`${name}.scss`, `${name}.sass`];
    const out = [];
    for (const base of bases) {
        out.push(`${dir}/${base}`);
        if (!name.startsWith('_'))
            out.push(`${dir}/_${base}`);
    }
    return out;
};
const compiler = text => {
    const out = [];
    let i = 0;
    for (const match of text.matchAll(importMatcher)) {
        const spec = match[2];
        if (!spec || spec.startsWith('sass:'))
            continue;
        const specs = match[1] ? [spec] : candidates(spec);
        for (const s of specs)
            out.push(`import _$${i++} from '${s}';`);
    }
    return out.join('\n');
};
export default { condition, compiler };
