# Glossary

Domain vocabulary for Mythos. Definitions describe the **concepts** the product works in, independent of any one implementation. (The Python CLI is a reference-only prototype; terms it introduced are marked _prototype_ where they may not carry forward unchanged.)

## Concept

**Definition:** The structured story brief generated first, from the writer's raw prompt — title, core idea, genre, themes, characters, setting, length. The seed for everything else.

**Do not confuse with:** Prompt — the unstructured writer input the concept is derived from.

## Asset

**Definition:** One building block of a story — concept, research, critical perspectives, settings, plot, themes, characters, timeline, writing style, intertextual references, chapter list, or a chapter. A living document the writer can read, edit, and collaborate on with the engine.

**Aliases:** Story element

## Story bible

**Definition:** The persistent, user-editable **canon** for a story — entities, world-rules, character voices, and established facts. The continuity engine reads it on every generation and writes to it on every edit; when an edit contradicts already-written chapters, the engine flags the conflict and offers a retroactive fix. The differentiator: not a one-time output of planning, but the source of truth the engine obeys throughout.

**Relates to:** Asset (assets are the bible's contents); Synopsis (the prototype's running-summary precursor to a true bible).

## Fork

**Definition:** A staged story decision. The engine surfaces a small set (3, up to 5) of genuinely divergent directions, each labeled with its one-line tradeoff; the writer picks. Does double duty — a low-effort authorial choice (ownership) and the mechanism that injects diversity against the model's homogenizing default.

**Do not confuse with:** Redirect — the plain-language override used when no forked option fits.

## Choose / Redirect / Edit

**Definition:** The core loop's three modes of writer control, in strict hierarchy. **Choose** at a fork (the spine). **Redirect** in plain language when no option fits (the steering wheel). **Edit** any asset, chapter, or the bible directly, becoming canon (the authority channel).

## Fork density

**Definition:** A writer-controlled dial for how often forks surface. Turned up → author mode (lean-forward, visible co-creation); near zero → reading mode (lean-back, near-continuous flow). The single mechanism that lets one engine serve both postures without a second product.

## Antislop pass

**Definition:** A craft pass that strips the recognizable tells of AI-generated prose — bans pattern families (the "it's not X, it's Y" frame, mechanical tricolons, the delve/tapestry/testament cluster), forces scene over summary, grounds stated emotion in the senses, and varies sentence rhythm.

## Details

**Definition:** The full generated text of an asset.

**Do not confuse with:** Summary — the compressed form used in downstream prompts.

## Summary

**Definition:** A compressed version of an asset's details (target ~300 words), used to keep downstream prompts small as the story grows.

**Do not confuse with:** Details — the full text the summary is derived from.

## Synopsis

**Definition:** _(prototype)_ The running, concatenated context for the whole story — the prompt, the concept details, and every asset's summary — rebuilt as assets are added and fed into later generation prompts. The prototype's shared-memory mechanism; superseded conceptually by the Story bible.

## Manuscript

**Definition:** The drafted prose chapters, written and held distinct from the planning assets.

## Opening scene

**Definition:** A standalone prose hook drafted in the story's writing style, generated early to break the blank page before full chapters exist.

## Iteration

**Definition:** _(prototype)_ A full refinement pass over the story — regenerates every planning asset at greater depth from the current context, then drafts the manuscript chapters. Bumps a version number.

**Aliases:** Version
