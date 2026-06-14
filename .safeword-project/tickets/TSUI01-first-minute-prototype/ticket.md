# Feature: First-minute authored-proof prototype

**Type:** Feature

**Scope:** Build a static web prototype that demonstrates Mythos's first-minute experience: premise capture, authored proof, three meaningful forks, visible mutation, and an opening-scene preview. The prototype is visual/static only and exists to validate product direction before live generation.

**Out of Scope:** Real LLM calls, persistence, authentication, billing, export, desktop shell selection, responsive production hardening, and full design-system extraction.

**Done When:**

- [x] The home page demonstrates premise capture → authored proof → fork choice → visible mutation → opening-scene preview.
- [x] The page uses the manuscript-with-living-margin layout from the visual design brief.
- [x] The Writer can understand the product without explanatory docs.
- [x] Automated tests verify the core prototype content renders.
- [x] Build, lint, typecheck, and tests pass.

**User Story:**

As a Writer with only a rough premise,
I want Mythos to reflect my idea, expose a sharper pressure point, and show meaningful story directions immediately,
So that I can feel my choices shaping the story before committing more time.

**Technical Constraints:**

- No new packages unless the prototype cannot be tested with existing dependencies.
- Static/mocked content only.
- Keep implementation local to the scaffolded web app.
