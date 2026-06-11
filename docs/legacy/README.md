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
