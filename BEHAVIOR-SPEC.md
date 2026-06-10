# Mythos — Behavior Specification (JTBD + BDD)

This document reverse-engineers Mythos's product behavior from the current
codebase into the project's own intake format: **Personas → Jobs To Be Done →
Acceptance Criteria → BDD scenarios**, with each scenario carrying its full
lineage so persona → JTBD → AC → scenario stays traceable. The conventions
follow `.claude/skills/bdd/DISCOVERY.md` and `.claude/skills/bdd/SCENARIOS.md`.

**Source of truth:** behavior described here is derived from
`code/mythos/story_manager.py`, `story.py`, `story_llm.py`,
`story_assets/base.py`, and `__main__.py` — what the code _does today_, not the
README's aspirational feature list. Where the code's intent and its current
implementation diverge (known bugs), the scenario documents the **intended**
behavior and a footnote flags the defect.

**One deliberate format deviation:** the saved scenario format in
`SCENARIOS.md` ends each scenario with `RED / GREEN / REFACTOR` checkboxes.
Those drive forward TDD; this is documentation of already-built behavior, so
checking them would claim a TDD trail that doesn't exist and leaving them
unchecked would imply unbuilt work. They're omitted on purpose. The
load-bearing BDD practices — Rules, declarative Given/When/Then, lineage
naming, and AODI quality (Atomic, Observable, Deterministic, Independent) — are
all kept.

Slug for all jobs: `mythos`.

---

## Personas

`.safeword-project/personas.md` is currently empty (template only). The code
serves exactly one real user.

### Writer (WR)

**Role:** A fiction author using Mythos from the command line to move from a
loose idea to a structured story and first-draft manuscript.

**Context:** Works in a terminal (`python -m mythos`), interacts through a text
menu, and supplies a single free-text prompt describing their idea, influences,
and audience. Wants to combat writer's block and a blank page. Comfortable
re-running and iterating; expects work to persist to disk between sessions.

---

## Glossary

Domain vocabulary used throughout this spec. Mirrors the concepts in the code;
candidates for promotion into `.safeword-project/glossary.md`.

### Concept

**Definition:** The structured story brief generated first, from the writer's
raw prompt and `concept_template.md` — title, core idea, genre, themes,
characters, setting, length. Stored as the `concept` asset and the seed for
everything else.

**Do not confuse with:** the writer's raw **prompt**, which is the unstructured
input the concept is derived from.

### Asset (Story Asset)

**Definition:** One building block of a story — `concept`, `research`, `plot`,
`characters`, `themes`, `setting`, `timeline`, `writing_style`, `chapter_list`,
or a `chapter`. Each asset holds `details` and a `summary`, and persists itself
to disk. Implemented by `StoryAsset` (`story_assets/base.py`).

**Aliases:** Story element.

### Details vs Summary

**Definition:** Two representations every asset carries. **Details** is the full
generated text. **Summary** is an LLM-compressed version (target ~300 words)
used to keep downstream prompts small as the story grows. Setting details
auto-regenerates the summary.

### Synopsis

**Definition:** The running, concatenated context for the whole story —
the prompt, the concept details, and every asset's _summary_. Rebuilt and
written to `synopsis.md` every time an asset is added, then fed into subsequent
generation prompts. This is the story's shared memory.

### Planning text vs Narrative text

**Definition:** Two generation modes. **Planning text** drafts structural assets
(concept, plot, etc.) via OpenAI `gpt-4o-mini`. **Narrative text** drafts prose
(chapters, opening scene) via Anthropic `claude-3-5-sonnet`. A third mode,
**JSON generation**, converts the chapter list into structured chapter data
with a validate-and-retry pass.

### Iteration / Version

**Definition:** A full refinement pass over the story. `iterate()` bumps the
version number, regenerates every planning asset at greater depth from the
current synopsis, then drafts the manuscript chapters.

### Manuscript

**Definition:** The drafted prose chapters, written as `chapter` assets under
the story's `manuscript/` directory. Distinct from the planning assets.

### Opening scene

**Definition:** A standalone ~500-word prose hook drafted in the story's writing
style, saved to `opening_scene.md`. Generated during initial creation to break
the blank page before full chapters exist.

---

## Jobs To Be Done

### mythos.WR1 — Turn a raw idea into a structured concept

**Persona:** Writer (WR)

> When I have a loose story idea but only a blank page, I want Mythos to turn my
> free-text prompt into a structured, titled concept, so I can see my idea take
> a concrete shape I can build on.

### mythos.WR2 — Generate a full planning scaffold from the concept

**Persona:** Writer (WR)

> When I have a concept but don't know how to develop it into a whole story, I
> want Mythos to draft all the supporting planning assets for me, so I can
> develop a multifaceted story without authoring each piece from scratch.

### mythos.WR3 — Get an opening scene to beat the blank page

**Persona:** Writer (WR)

> When I'm stuck staring at a blank page, I want Mythos to draft a compelling
> opening scene in my story's writing style, so I can break through writer's
> block and feel momentum before the full draft exists.

### mythos.WR4 — Deepen and refine the whole story on demand

**Persona:** Writer (WR)

> When my first-pass planning feels too thin, I want to run an iteration that
> regenerates every asset at greater depth from the story so far, so I can
> progressively enrich the story without rewriting each part by hand.

### mythos.WR5 — Draft the manuscript chapter by chapter

**Persona:** Writer (WR)

> When my chapter list is ready, I want Mythos to draft each chapter in order
> while staying consistent with the story so far, so I can produce a full
> first-draft manuscript rather than just an outline.

### mythos.WR6 — Save and resume a story across sessions

**Persona:** Writer (WR)

> When I step away from a project, I want my story and all its assets persisted
> to disk and reloadable later, so I can resume work in a new session without
> losing progress.

### mythos.WR7 — See what's done and what's left

**Persona:** Writer (WR)

> When I come back to a story, I want to see which parts exist and which are
> still missing, so I can decide what to work on next.

---

## Acceptance Criteria

Capability-level guarantees under each job. Scenarios below prove their
specifics.

### mythos.WR1 — Turn a raw idea into a structured concept

#### mythos.WR1.AC1 — A free-text prompt produces a concept that follows the concept template

#### mythos.WR1.AC2 — A title is extracted from the concept and becomes the story's identity and folder

#### mythos.WR1.AC3 — The concept is persisted and available as the seed for later generation

### mythos.WR2 — Generate a full planning scaffold from the concept

#### mythos.WR2.AC1 — All planning assets are generated, in a fixed order, from the concept

#### mythos.WR2.AC2 — Each generated asset is persisted and folded into the running synopsis

#### mythos.WR2.AC3 — Generation refuses to proceed when no concept exists yet

### mythos.WR3 — Get an opening scene to beat the blank page

#### mythos.WR3.AC1 — An opening scene is drafted in the story's writing style and saved to disk

#### mythos.WR3.AC2 — The opening scene is refused when no writing style exists to anchor it

### mythos.WR4 — Deepen and refine the whole story on demand

#### mythos.WR4.AC1 — An iteration regenerates every planning asset at greater depth from the synopsis

#### mythos.WR4.AC2 — Each iteration advances the story's version number

#### mythos.WR4.AC3 — An iteration finishes by drafting the manuscript chapters

### mythos.WR5 — Draft the manuscript chapter by chapter

#### mythos.WR5.AC1 — The chapter list is converted into valid structured (JSON) chapter data

#### mythos.WR5.AC2 — Each chapter is drafted as prose, in order, with the story so far as context

#### mythos.WR5.AC3 — Chapter drafting is refused when no chapter list exists

#### mythos.WR5.AC4 — Unrecoverable malformed chapter data stops drafting instead of producing garbage

### mythos.WR6 — Save and resume a story across sessions

#### mythos.WR6.AC1 — Every asset persists its details and summary to the story's folder

#### mythos.WR6.AC2 — The writer can list previously created stories and reopen one

#### mythos.WR6.AC3 — Reopening a story restores its previously generated assets

### mythos.WR7 — See what's done and what's left

#### mythos.WR7.AC1 — Status reports which core parts of the story are complete vs incomplete

---

## BDD Scenarios

Scenarios grouped under business **Rules**. Titles carry the lineage
`mythos.WR<n>.AC<m>.<snake_case_name>`. Each is written to be Atomic,
Observable, Deterministic, and Independent — LLM calls are treated as a
mockable boundary (a deterministic stub stands in for the model), so "the
generator returns X" is a controllable Given, not a live network dependency.

---

### Rule: A raw prompt becomes a structured, titled, persisted concept

Covers WR1.AC1, WR1.AC2, WR1.AC3.

#### Scenario: mythos.WR1.AC1.prompt_produces_concept_from_template

Given a writer has supplied a free-text story prompt
And the concept template is available
When the writer generates the concept
Then the planning generator is called with both the prompt and the template
And the returned concept is stored as the story's `concept` asset

#### Scenario: mythos.WR1.AC2.title_extracted_and_drives_folder_name

Given a generated concept whose text contains a `Title: ` line
When the concept is created
Then the story's title is set to that line's value
And the story's folder path is derived from the sanitized main title
(special characters removed, spaces replaced with underscores)

#### Scenario: mythos.WR1.AC2.untitled_concept_is_reported_not_silently_accepted

Given a generated concept whose text contains no `Title: ` line
When the concept is created
Then title extraction fails loudly rather than setting an empty or wrong title

> Rationale: today the code does `concept.split('Title: ')[1]`, which raises
> `IndexError` on a concept with no title line. The desired behavior is a clear,
> attributable failure — this scenario pins that intent. (Known defect:
> `story_manager.py:51`.)

#### Scenario: mythos.WR1.AC3.concept_is_persisted_as_generation_seed

Given a concept has been generated
When concept creation completes
Then the concept's details are written to the story folder
And the concept is available as `story.concept` for later asset generation

---

### Rule: The planning scaffold is generated in full, in order, from the concept

Covers WR2.AC1, WR2.AC2.

#### Scenario: mythos.WR2.AC1.initial_pass_generates_all_assets_in_fixed_order

Given a story with a concept set
When the writer runs the initial pass
Then an asset is generated for each planning type in the order
research, plot, characters, themes, setting, timeline, writing_style,
chapter_list
And each asset is generated from the concept details

#### Scenario: mythos.WR2.AC2.each_asset_is_added_and_folded_into_synopsis

Given the initial pass is generating assets
When an asset is added to the story
Then the asset is stored under its type in the story's asset map
And the synopsis is rebuilt to include that asset's summary
And the updated synopsis is written to `synopsis.md`

---

### Rule: Generation refuses to run without its prerequisites

Covers WR2.AC3, WR3.AC2, WR5.AC3.

#### Scenario: mythos.WR2.AC3.asset_generation_aborts_without_a_concept

Given a story that has no concept set
When the writer attempts to generate a planning asset
Then no asset is generated
And the writer is told that no concept is set

#### Scenario: mythos.WR3.AC2.opening_scene_refused_without_writing_style

Given a story that has no `writing_style` asset
When the writer requests an opening scene
Then drafting is refused with an explicit error naming the missing writing style
And no `opening_scene.md` is written

#### Scenario: mythos.WR5.AC3.chapter_drafting_refused_without_chapter_list

Given a story that has no `chapter_list` asset
When the writer attempts to draft chapters
Then drafting is refused with an explicit error naming the missing chapter list
And no chapters are produced

---

### Rule: The opening scene is drafted in the story's style and saved

Covers WR3.AC1.

#### Scenario: mythos.WR3.AC1.opening_scene_uses_writing_style_and_is_saved

Given a story with a `writing_style` asset and a synopsis
When the writer requests an opening scene
Then the narrative generator is called with the synopsis and the writing style
And the result is written to `opening_scene.md` in the story folder

---

### Rule: An iteration deepens every asset and advances the version

Covers WR4.AC1, WR4.AC2, WR4.AC3.

#### Scenario: mythos.WR4.AC2.iteration_increments_the_version_number

Given a story at version N
When the writer runs an iteration
Then the story's version number becomes N+1

#### Scenario: mythos.WR4.AC1.iteration_regenerates_each_asset_from_synopsis_and_template

Given a story with an existing set of assets and a synopsis
When the writer runs an iteration
Then for each planning asset type the asset is regenerated
And regeneration uses the asset's template plus the current synopsis
And the regenerated content is stored as that asset's details

#### Scenario: mythos.WR4.AC1.missing_asset_is_created_during_iteration

Given a story whose asset map is missing one planning type
When the writer runs an iteration
Then a new asset of that type is created rather than the iteration failing

#### Scenario: mythos.WR4.AC3.iteration_drafts_chapters_after_regenerating_assets

Given an iteration has regenerated all planning assets
When the iteration continues
Then chapter drafting runs as the final step of the iteration

---

### Rule: The manuscript is drafted from structured chapter data, in order, with continuity

Covers WR5.AC1, WR5.AC2, WR5.AC4.

#### Scenario: mythos.WR5.AC1.chapter_list_is_converted_to_valid_json

Given a story with a `chapter_list` asset
When chapter drafting begins
Then the chapter list details are converted to JSON in the chapter-list format
And the JSON is validated before use

#### Scenario: mythos.WR5.AC2.chapters_are_drafted_in_order_with_story_so_far

Given valid structured chapter data with multiple chapters
When chapters are drafted
Then each chapter is drafted in sequence as a `chapter` asset under `manuscript/`
And each chapter's prompt includes the synopsis and the story-so-far
accumulated from prior chapters

#### Scenario: mythos.WR5.AC4.unrecoverable_malformed_chapter_json_stops_drafting

Given chapter-list-to-JSON conversion that yields invalid JSON even after retry
When chapter drafting attempts to parse it
Then drafting stops without creating partial or garbage chapters
And the failure is surfaced to the writer

> Rationale: `generate_json` retries once on invalid JSON; `draft_chapters`
> additionally guards with a `JSONDecodeError` catch and a "no chapters found"
> error. This scenario pins the contract that bad data halts cleanly.

---

### Rule: Stories and their assets persist and reload across sessions

Covers WR6.AC1, WR6.AC2, WR6.AC3.

#### Scenario: mythos.WR6.AC1.asset_persists_details_and_summary_to_disk

Given an asset whose details are set
When the details are saved
Then a details markdown file is written in the story folder
And a summary markdown file is written
And the asset state is serialized for later reload

#### Scenario: mythos.WR6.AC2.writer_lists_and_selects_an_existing_story

Given one or more previously created story folders exist
When the writer chooses to work on an existing story
Then the existing stories are listed for selection
And selecting a valid number opens that story

#### Scenario: mythos.WR6.AC2.empty_store_reports_no_stories

Given no previously created story folders exist
When the writer chooses to work on an existing story
Then the writer is told there are no existing stories
And the writer is returned to a usable state rather than crashing

#### Scenario: mythos.WR6.AC3.reopening_a_story_restores_its_assets

Given a previously saved story with concept, plot, and setting on disk
When the writer reopens that story
Then the story's previously generated assets are loaded back into the session

> Rationale: pins the intended reload contract. (Known defects in current code:
> `__main__.open_story` reads `story.BASE_PATH`, which `Story` does not define,
> and `Story.load` requires an absolute path while it is called with a bare
> folder name — so reload currently fails. These scenarios define the target
> behavior the fixes should satisfy.)

---

### Rule: Status reports completion of the core story parts

Covers WR7.AC1.

#### Scenario: mythos.WR7.AC1.status_reports_complete_and_incomplete_parts

Given a story with some parts generated and others not
When the writer checks status
Then each core part (concept, plot outline, characters, setting) is reported as
complete or incomplete according to whether it exists

---

## Coverage map

| JTBD       | ACs     | Scenarios |
| ---------- | ------- | --------- |
| mythos.WR1 | AC1–AC3 | 4         |
| mythos.WR2 | AC1–AC3 | 3         |
| mythos.WR3 | AC1–AC2 | 2         |
| mythos.WR4 | AC1–AC3 | 4         |
| mythos.WR5 | AC1–AC4 | 4         |
| mythos.WR6 | AC1–AC3 | 4         |
| mythos.WR7 | AC1     | 1         |

Every AC is referenced by at least one scenario; every scenario traces to an AC,
a JTBD, and the Writer persona. No orphans, no uncovered ACs.

## Known defects surfaced during extraction

These are documented as footnotes above; collected here for action. The
scenarios encode the _intended_ behavior each fix should make pass.

1. **Untitled concept crashes** — `story_manager.py:51` assumes a `Title: ` line
   (`mythos.WR1.AC2`).
2. **Reload is broken** — `open_story` references the non-existent
   `story.BASE_PATH`, and `Story.load` requires an absolute path but is called
   with a bare folder name (`mythos.WR6.AC2`, `mythos.WR6.AC3`).
3. **CWD-fragile paths** — templates open as `templates/...` and
   `STORY_DIR = "../stories"`, so the app only runs from inside `code/` (affects
   WR1, WR2, WR4 in practice).
4. **Dead asset subclasses** — `Chapter`/`Character` call
   `super().__init__(summary_length=...)` but the base requires `path` and
   `asset_type`; they would crash if used.
5. **Literal-brace summary prompt** — the summary prompt in `base.py:97` is not
   an f-string, so `{self.summary_length}` ships verbatim to the model.

**Next:** want me to also seed `.safeword-project/personas.md` and `glossary.md`
from the Personas/Glossary sections here, or open tickets for the five defects?
