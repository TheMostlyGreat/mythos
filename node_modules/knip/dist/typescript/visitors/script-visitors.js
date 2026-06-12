export function createBunShellVisitor(ctx) {
    return {
        TaggedTemplateExpression(node) {
            const tag = node.tag;
            if (tag.type === 'Identifier' && tag.name === '$') {
                for (const q of node.quasi.quasis) {
                    if (q.value.raw)
                        ctx.addScript(q.value.raw);
                }
            }
        },
    };
}
