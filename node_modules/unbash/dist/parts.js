import { Lexer } from "./lexer.js";
import { parse } from "./parser.js";
/**
 * Compute the structural parts of a word by re-scanning the source.
 * This is the "cold path" — only called when consumers actually need parts.
 *
 * Returns undefined for simple words (no quotes, expansions, or special structure).
 */
export function computeWordParts(source, word) {
    const lexer = new Lexer(source);
    const parts = lexer.buildWordParts(word.pos);
    if (!parts)
        return undefined;
    resolveCollected(lexer);
    return parts;
}
/**
 * Compute parts for an unquoted heredoc body.
 * Heredoc bodies use different scanning rules than shell words: newlines are
 * literal and single/double quotes have no special meaning.
 */
export function computeHereDocBodyParts(source, word) {
    const lexer = new Lexer(source);
    const parts = lexer.buildHereDocParts(word.pos, word.end);
    if (!parts)
        return undefined;
    resolveCollected(lexer);
    return parts;
}
function resolveCollected(lexer) {
    for (const e of lexer.getCollectedExpansions()) {
        if (e.inner !== undefined) {
            e.script = parse(e.inner);
            e.inner = undefined;
        }
    }
}
