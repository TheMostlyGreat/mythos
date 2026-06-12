export function createZxVisitor(ctx) {
    return {
        TaggedTemplateExpression(node) {
            if (!ctx.sourceText.startsWith('#!/usr/bin/env zx'))
                return;
            if (node.tag.type === 'Identifier' && node.tag.name === '$') {
                for (const q of node.quasi.quasis) {
                    if (q.value.raw)
                        ctx.addScript(q.value.raw);
                }
            }
        },
    };
}
