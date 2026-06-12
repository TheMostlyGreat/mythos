# Legacy planning docs (Python prototype era)

These documents planned and critiqued the **Python prototype** under `mythos/`. They are kept as **reference to mine** during the greenfield TypeScript rebuild — working behavior, prompt designs, pipeline logic, and craft critiques — not as live plans.

The canonical, forward-looking source of truth is `JTBD.md` at the repo root; the rebuild's framing lives in `CLAUDE.md`. Treat everything here as historical: model names, status claims, and "next steps" reflect the prototype, not the current direction.

---

## Findings worth mining

Verified observations from reading the prototype, for whoever rebuilds the equivalent in TypeScript.

### Intake interview → concept (traced June 2026)

The raw-idea → concept path, end to end:

1. `StoryQuestioner.conduct_interview` (`mythos/services/story_questioner.py`) runs a **fast-tier** (`gpt-5-mini`) chat — one question per turn, governed entirely by `QUESTIONER_SYSTEM_PROMPT` (`mythos/config/settings.py`). Each turn the model returns `{response, ready_to_stop}` and decides when to stop; it stays in **setup phase only** (never asks about plot, endings, or twists, to preserve the user's discovery).
2. `_build_refined_prompt` does **not** synthesize — it concatenates the original idea with a bullet list of the user's raw answers and **discards the AI's questions**.
3. That blob becomes `story.user_prompt`. `_assemble_planning_prompt` wraps it with `concept_template.md` and calls `generate_story_concept` — a **medium-tier** (`claude-sonnet-4`) call returning the structured concept `{title, concept_markdown}`.

**So synthesis happens — but in `_generate_concept_asset`, one step later than the "refiner" name suggests, and the structure comes from the template, not the interview.** Two upgrades for the rebuild: (a) the concept model only ever sees answers, never the questions that framed them ("slow-burn" without "slow-burn, forbidden, or triangle?"), so context is lost; (b) the TS questioner should emit a structured brief (Q&A pairs or a synthesized brief), not a bullet dump. Maps to JTBD "Turn a raw idea into a developed story concept" — interview half solid, synthesis half thin.

### Asset & chapter generation pipeline (traced June 2026)

`build_story` (`mythos/services/story_builder.py`) runs five phases, each gated only by a yes/no `confirm_next_step`: concept → planning assets → chapter outline → chapter narratives → EPUB. The Writer's sole agency is "continue?".

- **Planning fan-out** (`_generate_related_assets`) is **sequential, fixed order**: research → settings → plot → themes → characters → timeline → chapter_list → writing_style. Each asset is generated from `{user_prompt + running synopsis + asset template}` (`_assemble_planning_prompt`), and each new summary folds into the **synopsis** before the next runs — so order is load-bearing. That synopsis is the prototype's continuity memory: **the proto-`story bible`** the vision promotes to canon.
- **Generator dispatch** (`_create_single_asset`): characters and chapter_list use structured-JSON generators, research uses the web-search call, the rest use plain planning text — all medium-tier.
- **Chapter narratives** (`write_chapters`) is also a **sequential** loop, accumulating `story_so_far` (concatenated chapter summaries) for continuity; each chapter is written from `{synopsis + chapter_details + writing_style + story_so_far}`.
- **Parallelism** (`ThreadPoolExecutor(max_workers=3)`) is used **only** for order-independent batches — critical perspectives, deep-dive research, deep-dive settings. The continuity-bound loops are deliberately sequential. (Resolves the old "document max_workers=3" todo: it's correct where it sits.)
- **Non-fatal branches:** deep-dives and critical perspectives are wrapped in `try/except` that warns and continues — failures are silent, and nothing wires their output into chapter writing (the "add back critical perspectives" todo).

For the rebuild: **keep** the synopsis→bible lineage, the asset list, and the sequential-for-continuity / parallel-for-independent split. **Break open** the silent auto-fan-out — the high-leverage assets (plot, themes, character cast) and act-level chapter turns are the natural fork sites, replacing "continue?" gates with authored choices. **Fix** the silent critical-perspective failures, and actually feed their output downstream.

### Persistence & resume (traced June 2026)

- **Persistence is dual** (`StoryManager.save_story`): a `{sanitized-title}.story` JSON file holds the `Story` plus asset/manuscript _metadata_; the asset and chapter _content_ lives in `.md` files on disk. The `.story` file is references and metadata, not prose.
- **State is inferred, not stored** (`get_story_state`): the phase is derived by inspecting which artifacts exist — required planning assets present? chapter outlines? manuscript chapters (count vs. outlines)? final draft/EPUB? — returning `empty` / `assets_incomplete` / `chapters_not_outlined` / `chapters_not_written` / `chapters_partial` / `finalization_needed` / `complete`. There is **no saved "current phase" flag**: the artifacts _are_ the state, so it can't desync from reality.
- **Resume dispatches on that state** (`smart_resume_story`): each state routes to the matching resume method (assets / outlines / chapters / finalize), gated by a `confirm_next_step`.

This **strongly validates** JTBD "Pause and resume without losing progress" — and the artifact-derived, self-healing design is worth keeping verbatim. Two forward notes for the fork world: (a) "the exact point of incompleteness" should also mean an **unanswered fork**, not just a missing artifact — phase-only resume would silently drop a pending decision; (b) resume granularity is chapter-level today and will need to drop to **scene-level** alongside the scene tree.
