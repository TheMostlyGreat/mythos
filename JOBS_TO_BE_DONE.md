# Jobs To Be Done

Inventory of outstanding work identified from code, comments, planning docs, and `.todos.md`.

---

## Critical

1. **Fix character generation** — `.todos.md:1` flags broken characters; unclear if questioner responses propagate into character assets
2. **Ensure questioner answers feed into concept** — `.todos.md:5`: "are the questions making their way back into the concept?"
3. **Add back critical perspectives** — `.todos.md:14`; currently generation is non-fatal (`story_builder.py:610` swallows exceptions and warns); unclear if output is fed into chapter writing
4. **Fix broad exception swallowing** — `ui_utils.py:51,77` and `story_asset_manager.py:129` catch bare `Exception` without logging; errors silently disappear
5. **Validate API keys on startup** — `llm_utils.py:169,348` check env vars but don't validate format; empty strings or malformed keys will surface late with confusing errors; `settings.py:537` has `validate_configuration()` commented out

---

## High

6. **Add scene-level story structure** — `.todos.md:3`: "Chapters and scenes should be filled out — a tree structure with scenes under chapters"; currently only chapter-level breakdown exists
7. **Break out research per item** — `.todos.md:5`: research asset is monolithic; needs per-item granularity
8. **Add intertextual references asset** — `.todos.md:4`: "intertextual references should be added" — not present in asset generation pipeline
9. **Decide on Settings breakout** — `.todos.md:6`: "Should there be a breakout of settings?" — unclear if world-settings asset needs subdivision
10. **Remove exception class duplication** — `settings.py:81-87` defines `ProviderError`/`ContentRefusalError` with `pass`; same classes redefined in `llm_utils.py:26-40`; `settings.py:80` acknowledges this — pick one canonical location
11. **Add character voice examples to Writing Style asset** — `PLANNING_ASSET_CRITIQUE.md:66`: missing character voice examples, dialogue samples, speech patterns
12. **Log JSON parse failures** — `story_builder.py:1145,1218` have bare `pass` in `except` blocks for JSON parsing fallback; failures are invisible

---

## Medium

13. **Optimize extended thinking budgets per use case** — `STATUS_OCTOBER_2025.md:111`: "Thinking budget optimization per use case" is explicitly listed as TODO; `settings.py:36` uses one default `DEFAULT_THINKING_BUDGET = 4000` for all calls
14. **Run full test suite + performance benchmarks** — `STATUS_OCTOBER_2025.md:109,110`: listed as explicit TODOs
15. **Document/justify `max_workers=3`** — `story_builder.py:1484,1721,1838` hardcode `ThreadPoolExecutor(max_workers=3)` with no rationale; should be configurable or derived from CPU count / API rate limits
16. **Improve external file change detection** — `__main__.py:282-284` only shows first 5 changed files; could silently hide significant edits; unclear how baseline updates during resume
17. **Define narrative voice as explicit asset** — `.todos.md:144` (inferred from planning docs); voice definition currently implicit

---

## Low / Future

18. **Historical token usage tracking** — `__main__.py:395,405,333` prints totals per run but no cumulative history; no per-asset or per-tier breakdown
19. **Tune timeout values with real data** — `settings.py:67,68` set `STANDARD_TIMEOUT=180` and `CONCEPT_TIMEOUT=300` without documented basis; revisit once performance benchmarks exist
20. **Write missing tests**
    - `StoryBuilder.smart_resume_story()` resume logic
    - `StoryManager.get_story_state()` state machine transitions
    - `StoryManager.has_asset_changes()` change detection
    - Concurrent asset generation with partial failures
    - Critical perspectives end-to-end workflow
    - EPUB generation with varying chapter counts
21. **Verify `ENABLE_INTERLEAVED_THINKING`** — `settings.py:37` enables it but usage in the codebase is unclear; confirm it's actually wired up in `llm_utils.py`
22. **Model selection rationale docs** — `settings.py:27-29` lists tier assignments but no guidance on when to change them or how they were chosen

---

## From `.todos.md` (verbatim, unresolved)

```
1. Fix characters
3. Chapters, and scenes should be filled out. I'm thinking a tree structure with the scenes under the chapters.
4. Intertextual references should be added
5. Research should be broken out per item
5. are the questions making their way back into the concept?
6. Should there be a breakout of settings?
14. Add back in critical perspectives
```
