import { frontmatterMatcher, scriptBodies } from '../../compilers/compilers.js';
const propsDeclMatcher = /(?:^|[\s;])(?:interface|type)\s+Props\b/;
const compiler = (text, path) => {
    const scripts = [];
    const frontmatter = text.match(frontmatterMatcher);
    if (frontmatter?.[1]) {
        let fm = frontmatter[1];
        if (propsDeclMatcher.test(fm) && text.includes('Astro.props'))
            fm += '\ntype __knip_astro_props = Props;';
        scripts.push(fm);
    }
    const scriptContent = scriptBodies(text, path);
    if (scriptContent)
        scripts.push(scriptContent);
    return scripts.join('\n');
};
export default compiler;
