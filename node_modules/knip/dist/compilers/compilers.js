export const fencedCodeBlockMatcher = /```[\s\S]*?```/g;
export const inlineCodeMatcher = /`[^`]+`/g;
export const scriptExtractor = /<script\b((?:[^>"']|"[^"]*"|'[^']*')*)>([\s\S]*?)<\/script>/gi;
export const blockCommentMatcher = /\/\*[\s\S]*?\*\//g;
export const lineCommentMatcher = /^[ \t]*\/\/.*$/gm;
export const importMatcher = /import(?:\s*\(\s*['"][^'"]+['"][^)]*\)|(?!\s*\()[^'"]+['"][^'"]+['"])/g;
export const importsWithinScripts = (text) => {
    const scripts = [];
    for (const [, , scriptBody] of text.matchAll(scriptExtractor)) {
        const body = scriptBody.replace(blockCommentMatcher, '').replace(lineCommentMatcher, '');
        for (const importMatch of body.matchAll(importMatcher))
            scripts.push(importMatch);
    }
    return scripts.join(';\n');
};
export const scriptBodies = (text) => {
    const scripts = [];
    for (const [, , body] of text.matchAll(scriptExtractor)) {
        if (body)
            scripts.push(body);
    }
    return scripts.join(';\n');
};
export const frontmatterMatcher = /^---\r?\n([\s\S]*?)\r?\n---/;
export const importsWithinFrontmatter = (text, keys = []) => {
    const frontmatter = text.match(frontmatterMatcher)?.[1];
    if (!frontmatter)
        return '';
    const imports = keys.flatMap(key => {
        const valueMatcher = new RegExp(`${key}:\\s*["']([^"']+)["']`, 'i');
        const match = frontmatter.match(valueMatcher);
        return match?.[1] ? [`import ${key} from "${match[1]}";`] : [];
    });
    return imports.join('\n');
};
