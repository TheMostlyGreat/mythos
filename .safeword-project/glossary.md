# Glossary

## Concept

**Definition:** The structured story brief generated first, from the writer's raw prompt and `concept_template.md` — title, core idea, genre, themes, characters, setting, length. Stored as the `concept` asset and the seed for everything else.

**Used in:** spec WR1; `story_manager.generate_concept`.

**Do not confuse with:** Prompt — the unstructured writer input the concept is derived from.

## Asset

**Definition:** One building block of a story — `concept`, `research`, `plot`, `characters`, `themes`, `setting`, `timeline`, `writing_style`, `chapter_list`, or a `chapter`. Each asset holds `details` and a `summary` and persists itself to disk. Implemented by `StoryAsset` (`story_assets/base.py`).

**Used in:** all specs; the core unit the StoryManager generates and refines.

**Aliases:** Story Element

## Details

**Definition:** The full generated text of an asset. Setting details auto-regenerates the asset's summary.

**Do not confuse with:** Summary — the compressed form used in downstream prompts.

## Summary

**Definition:** An LLM-compressed version of an asset's details (target ~300 words), used to keep downstream prompts small as the story grows.

**Do not confuse with:** Details — the full text the summary is derived from.

## Synopsis

**Definition:** The running, concatenated context for the whole story — the prompt, the concept details, and every asset's summary. Rebuilt and written to `synopsis.md` each time an asset is added, then fed into subsequent generation prompts. The story's shared memory.

**Used in:** WR2, WR4, WR5; `story.build_synopsis`.

## Planning text

**Definition:** Generation mode that drafts structural assets (concept, plot, etc.) via OpenAI `gpt-4o-mini`.

**Do not confuse with:** Narrative text — used for prose.

## Narrative text

**Definition:** Generation mode that drafts prose (chapters, opening scene) via Anthropic `claude-3-5-sonnet`.

**Do not confuse with:** Planning text — used for structural assets.

## Iteration

**Definition:** A full refinement pass over the story — bumps the version number, regenerates every planning asset at greater depth from the current synopsis, then drafts the manuscript chapters.

**Used in:** WR4; `story_manager.iterate`.

**Aliases:** Version

## Manuscript

**Definition:** The drafted prose chapters, written as `chapter` assets under the story's `manuscript/` directory. Distinct from the planning assets.

**Used in:** WR5; `story_manager.draft_chapters`.

## Opening scene

**Definition:** A standalone ~500-word prose hook drafted in the story's writing style and saved to `opening_scene.md`. Generated during initial creation to break the blank page before full chapters exist.

**Used in:** WR3; `story_manager.draft_opening_scene`.
