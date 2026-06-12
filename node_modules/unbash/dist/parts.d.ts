import type { Word, WordPart } from "./types.ts";
/**
 * Compute the structural parts of a word by re-scanning the source.
 * This is the "cold path" — only called when consumers actually need parts.
 *
 * Returns undefined for simple words (no quotes, expansions, or special structure).
 */
export declare function computeWordParts(source: string, word: Word): WordPart[] | undefined;
/**
 * Compute parts for an unquoted heredoc body.
 * Heredoc bodies use different scanning rules than shell words: newlines are
 * literal and single/double quotes have no special meaning.
 */
export declare function computeHereDocBodyParts(source: string, word: Word): WordPart[] | undefined;
