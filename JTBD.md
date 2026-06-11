# Mythos — Jobs To Be Done

A forward-looking description of this project through the lens of every job it helps users accomplish.

> This document is the **canonical, forward-looking description** of Mythos — the jobs it helps the **Writer** accomplish, stated independently of any implementation. Stack, delivery, and the current rebuild live in `CLAUDE.md`, not here.

Each job is stated in canonical job-story form — **[Persona] — When [situation], I want to [motivation], so I can [outcome]** — followed by the design rationale. The one persona, **Writer**, is defined in `.safeword-project/personas.md`. A few jobs labeled _Integrator (deferred)_ describe a role we don't build for today.

---

## Who this is for

Mythos is a **creative tool, not a content platform** — it optimizes for the person _making_ a story, not an audience browsing others' stories. Personas are defined in [`.safeword-project/personas.md`](.safeword-project/personas.md): the one real user is the **Writer**, with an **Integrator** (programmatic/MCP access) and a **Reader** (consuming _other_ writers' stories) as deferred roles we don't build for yet. Per _The story finds its own cadence_ below, "Reader" is a mode of the Writer — reading is authoring with forks turned down — not a separate persona.

---

## Design Principles

These principles govern _how_ the jobs below are delivered. They exist because the research on creative-tool attachment and AI fiction quality points somewhere counterintuitive.

### Mechanically effortless, expressively yours

"Effortless" and "deep emotional attachment" pull in opposite directions. Attachment comes from being a thing's **causal, visible co-creator**, not its commissioner — the IKEA effect, and psychological-ownership research showing that automating the _expressive_ act destroys ownership and agency. A one-click "type a sentence, get a novel" product would produce homogenized AI slop _and_ kill attachment at once, because the user did nothing they can point to as their own.

So **"effortless" means mechanically effortless, never expressively effortless.** Strip the drudgery — blank-page paralysis, continuity bookkeeping, formatting, "what comes next" mechanics. Keep and actively stage the expressive decisions, because those decisions _are_ the entertainment and _are_ the source of attachment. The unit of the product is **the meaningful decision, made delightful** — not the prompt, not the chat.

### The core loop: choose → redirect → edit

Three modes of user control, in a strict hierarchy:

1. **Choose** (the spine — cheap, frequent enough to feel authored). At a story fork, the engine surfaces a small set of genuinely divergent directions, each labeled with its tradeoff. The user picks. This single gesture does double duty: it's a low-effort, legible, causal authorial choice (ownership), and it's how we inject diversity against the AI's homogenizing default (Verbalized Sampling — ask the model for a _distribution_ of options, ~1.6–2.1× diversity, no quality loss).
2. **Redirect** (the steering wheel). When no option fits, the user says it in plain language — "make the ending land as regret" — and the engine regenerates against that, honoring the standing choice. Conversation is the override channel, not the primary surface.
3. **Edit** (the authority channel). The user opens any asset, chapter, or the story bible and edits it directly, like a doc. Their edit becomes **canon** — ground truth the engine obeys in all downstream generation.

Everything writes _through_ the story bible, which is read on every generation and written to on every edit.

### Fork spec: how decisions are staged

Grounded in choice-architecture research (Chernev 2015 choice-overload moderators; Cowan's ~4-chunk working-memory limit; Fendt 2012 on agency saturation; Sid Meier's "interesting decisions"):

- **3 options per fork** (4 only when sharply differentiated and each previewed in one line; 5 is the hard ceiling). Story forks are high on every choice-overload moderator — no objectively right branch, hard to evaluate in the abstract — so small sets win. The lever that defeats overload is **evaluability**: a crisp one-line tradeoff label on each option matters more than the exact count.
- **Tiered cadence, not a fixed clock.** Most of the book is **flow** (pure, bible-consistent prose). Punctuated by **~per-chapter forks** (medium stakes, light divergence on a central spine) and **3–5 act forks** across the whole book (high stakes, real divergence). A novel involves roughly **8–15 total decisions**, not 40.
- **Spend on acknowledgment, not branch width.** Felt agency saturates: a few well-acknowledged forks (the engine calls back to the choice, the bible visibly reflects it, a "your story diverged here" marker) feel _more_ authored than a dense thicket of cosmetic ones — and cost far less to build.
- **The user can always request a fork** ("let me steer here") on top of the ones the engine surfaces.

> **Open build risk:** tiered cadence requires the engine to _detect_ where a genuine "interesting decision" lives in the plot, rather than hardcoding "fork at chapter 3." That detection is the non-trivial part; the user-requested fork is the fallback.

### The story finds its own cadence

The cadence above is a _default_, not a fixed clock — and crucially **not a setting the user manages.** Asking the Writer to pick a "mode" or work a density slider is a thing to learn and a thing to get wrong; one engine serves both a lean-forward author and a lean-back reader without ever surfacing that choice as a control.

Instead, **the control and the sensor are the same gesture.** Every fork carries a frictionless "let the story carry on," and every stretch of flow can be interrupted with "let me steer here." When the Writer deliberates over a fork and picks, that's a lean-forward signal; when they wave forks through or reach for "just continue," that's lean-back. The engine reads that behavior and slowly modulates how often it surfaces forks against the default curve — pushing when the Writer is engaged, breathing when they're receiving. No mood-reading, no menu; the Writer's own choices _are_ the dial.

Two rules keep this from going wrong, both straight from the research on self-adjusting interfaces: adaptation moves **slowly and predictably** (no thrash from one stray click), and every adaptation is **elective** — a fork is always skippable and a fork is always summonable, so the Writer can override the engine's read at any moment without losing agency. "Reader is a mode of the Writer" resolves here: lean-back and lean-forward aren't modes anyone selects — they're emergent positions on a curve the story discovers from how the Writer plays it.

### Sophistication is a property of the output, not the Writer

Literary sophistication — thematic depth, intertextual echo, a real tension arc, prose that doesn't read as slop — is an attribute of the **story Mythos produces**, never a trait the Writer has to bring. The Writer is a layperson with no formal craft; they hire Mythos precisely to supply the sophistication they couldn't engineer themselves. So every craft job is voiced as the Writer's plain desire ("I want my story to actually mean something"), and the machinery that delivers it (critical lenses, allusion-tracking, affect planning) lives in the rationale, never in the want. The Writer directs; Mythos is the crew. The gap between what the Writer can do alone and the quality of the output isn't a contradiction — it's the whole value proposition.

---

## Creation — Ideation & Concept

### Turn a raw idea into a developed story concept

**Writer** — When I have only a rough premise ("a detective who can see memories") and don't know how to grow it into something I could actually write, I want Mythos to interview me about intent, stakes, tone, and genre and synthesize a complete creative brief, so I can start from a solid foundation instead of a blank page.

Mythos conducts a conversational interview to clarify intent, stakes, tone, and genre — then synthesizes a full story concept that serves as the creative foundation for everything that follows.

### Review and shape the concept before committing to generation

**Writer** — When a concept has been drafted but I'm not yet sure it's right, I want to react to it, ask for variations, and edit the concept document directly in conversation before any expensive generation runs, so I can commit to a direction I actually believe in.

The user can ask for variations, redirect the tone, or edit the concept document directly like a doc. Only then does generation proceed.

### Build a complete world before writing a single chapter

**Writer** — When my concept is set but the world behind it is still thin, I want Mythos to generate interconnected planning assets — concept, research, critical perspectives, settings, plot, themes, characters, timeline, writing style — as living documents I can read and edit, so I can write on top of a fully realized world.

Each asset is stored as a living document the user can read, edit, and collaborate on with the AI.

### Understand the world deeply, not just broadly

**Writer** — When my world is broad but generic, I want Mythos to identify the areas in the research and settings that need depth and generate focused deep-dives on each, so I can have authentic specificity without padding.

Generic world-building isn't enough; Mythos targets the spots that need deeper investigation rather than padding everything uniformly.

### Give the story something real to say

**Writer** — When I want my story to actually mean something — to land with weight rather than just happen — I want Mythos to build that depth in from the start, so I can have a story that says something without knowing how to engineer that myself.

The machinery: Mythos reads the story through established critical lenses (feminist, Marxist, postcolonial, and others) to surface theme and subtext, then bakes that depth into generation. The craft runs underneath; the Writer never has to name a theory — they just get a story with something to say.

### Use genre-appropriate craft guidance

**Writer** — When my story sits in a genre with its own conventions, tropes, and structural expectations, I want Mythos to apply genre-specific craft guidance during generation, so I can have the genre's craft handled well rather than generically.

Mythos applies genre-specific writing templates (Fantasy, Crime, Horror, Romance, Sci-Fi, Literary Fiction, Mystery/Thriller, Historical Fiction, etc.) that inform how each genre's craft is handled.

### Echo the books and influences I love

**Writer** — When my idea is inspired by stories I love — "like Le Guin meets a heist movie" — I want Mythos to treat those touchstones as something it writes toward, so I can have my story echo what inspired it without studying how allusion works.

The machinery: the influences the Writer names are captured as a dedicated asset and fed into generation as a living touchstone. The Writer says what they love; Mythos manages the literary dialogue — allusion, homage, intertextual echo — underneath.

---

## Creation — Drafting & Writing

### Know exactly what happens in every chapter before writing it

**Writer** — When I'm about to draft but have no roadmap, I want Mythos to generate a full chapter outline and a detailed per-chapter plan (scene breakdown, POV, character arcs, thematic elements, pacing), so I can write each chapter knowing exactly what it needs to do.

Writers have a complete roadmap before prose begins.

### Start with a polished opening scene before committing to chapters

**Writer** — When I haven't locked the voice and tone yet, I want Mythos to generate a dedicated opening scene — a planning pass, then full prose — first, so I can anchor the rest of the manuscript to an opening I'm happy with.

The opening scene establishes voice and tone for everything that follows and becomes the anchor for the rest of the manuscript.

### Build the manuscript incrementally, chapter by chapter

**Writer** — When I don't want to commit to a whole manuscript sight-unseen, I want Mythos to generate one chapter at a time and surface each for my reaction, so I can continue or redirect before more is written.

Users see a chapter, react to it, and decide whether to continue or redirect — not commit to generating the entire manuscript blindly.

### See and steer the story scene by scene

**Writer** — When a whole chapter is too big a unit to react to, I want to see my story as scenes inside each chapter — each one its own beat I can read, edit, or redirect on its own — so I can shape the story at the grain where it actually turns, not in 4,000-word blocks.

The machinery: the manuscript is a tree — story → chapters → scenes — where each scene is a first-class node carrying its own POV, setting, characters present, purpose, and tension level, plus its own prose. That structure is what lets the engine place forks where a story genuinely turns (scene boundaries, not an arbitrary chapter clock), regenerate one scene without disturbing the rest, and track continuity at the grain where it actually breaks.

### Get a full draft manuscript written

**Writer** — When my planning is done and I want to see the book exist, I want Mythos to write complete, full-length narrative chapters from the planning assets while holding continuity, voice, and theme, so I can have a real draft rather than fragments.

The model maintains continuity, voice, and thematic consistency across the full manuscript.

### Edit any output directly, like a document

**Writer** — When generated text is close but not exactly what I want, I want to open any asset or chapter and edit it directly — not just regenerate — and have Mythos treat my edit as authoritative in all downstream generation, so I can keep ultimate authorship.

Edits are respected and preserved; the AI treats user edits as authoritative when continuing generation.

### Steer the story in conversation at any stage

**Writer** — When something needs to change mid-process, I want to say it in plain language at any step — "make the protagonist younger," "shift the tone darker," "set it in near-future Tokyo" — and have the system update accordingly, so I can direct the story instead of filling out forms.

The creation process is a conversation, not a form — at concept, assets, or chapters.

---

## Creation — Quality & Craft

These jobs exist because the default output of an aligned LLM is recognizable "slop" — homogenized, relentlessly positive, low-tension, cliché-dense. Hitting literary quality is an explicit job, not a byproduct.

### Make it sound like literature, not a chatbot

**Writer** — When generated prose carries the recognizable tells of AI slop, I want Mythos to run a craft pass that bans _pattern families_, forces scene over summary, and grounds stated emotion in the senses, so I can read prose a reader is engrossed by rather than prose that announces its origin.

The antislop pass bans pattern families (the "it's not X, it's Y" antithesis frame, mechanical tricolons, the puffery cluster — delve/tapestry/testament), forces **scene over summary** (readers feel scenes, not summaries), grounds stated emotion ("her coffee went cold against her trembling fingers," never "she was sad"), and deliberately varies sentence rhythm.

### Be surprised by my own story

**Writer** — When I reach a fork, I want the divergent options to be genuinely different directions rather than rephrasings of one beat, so I can discover possibilities I wouldn't have thought of.

Surprise is both the entertainment and the diversity mechanism (Verbalized Sampling) — the user discovers possibilities they wouldn't have thought of while the system escapes its homogenizing default.

### Feel the tension

**Writer** — When a story drifts into the AI's flat, uniformly positive register, I want Mythos to plan an explicit affect-and-tension arc with deliberate turning points, suspense, and high-arousal beats, so I can feel real stakes as I read.

A planned tension arc is the single biggest measured lever on perceived story quality.

### Make it sound like _me_ (later)

**Writer** — When I have my own writing and want the book to read as mine, I want Mythos to adapt its prose voice to my uploaded work, so I can have output that reads as mine without imitating other authors.

This is the strongest quality lever in the research (fine-tuning on an author's own work) _and_ the strongest attachment lever, while sidestepping the legal and ethical problems of imitating other authors.

---

## Creation — Continuity & Control

### Keep the whole book consistent with itself (the story bible as canon)

**Writer** — When a long book risks drifting, contradicting itself, or losing voice over 80k words, I want Mythos to treat the story bible as persistent canon it reads on every generation — and to flag conflicts and offer a one-click retroactive fix when I edit it — so I can trust the whole book to stay consistent with itself.

This is the differentiator. The story bible isn't just an _output_ of the planning phase — it's the **persistent continuity engine** the writing phase reads from on every generation. Entities, world-rules, character voices, and established facts are injected as fixed canon. When the user edits the bible, the canon updates and all downstream generation respects the change; when an edit contradicts already-written chapters, Mythos flags it and offers a one-click retroactive fix ("chapter 2 still uses the old name — update?"). The bible is the user-editable source of truth the engine obeys, not a document it merely consulted once.

### Pause and resume without losing progress

**Writer** — When I have to stop partway and come back later, I want Mythos to save state at every phase and resume from the exact point of incompleteness, so I can work across many sessions without losing progress.

Mythos detects what's done and picks up exactly where work stopped.

### Generate story length and scope appropriate to the idea

**Writer** — When my idea isn't necessarily novel-sized, I want Mythos to infer whether it's a short story, novella, or novel and scope the assets and chapters to match (with my override), so I can get a length that fits the idea.

Not every idea is a novel; Mythos generates only the assets and chapters appropriate to the inferred scope, with user override.

### Research per topic, not as a monolithic blob

**Writer** — When I need research while writing, I want it organized into per-topic documents rather than one blob, so I can pull the specific findings a given scene needs.

Research findings are most useful organized by topic, enabling targeted use of specific findings during chapter writing.

### Recover gracefully when a model fails

**Writer** — When an AI model is unavailable or fails mid-pipeline, I want Mythos to retry with the next best alternative and notify me, so I can keep going instead of hitting a hard error that stops everything.

Rather than surfacing a hard error that stops the pipeline, Mythos retries with the next best model and tells the user.

---

## Reading — The Final Product

### Read the story as it's born (creation and reading are one surface)

**Writer** — When a new chapter is written, I want to read it immediately in an immersive reader that ends on the open question becoming my next fork, so I can witness the story being born and let my reaction steer what comes next.

The reader and the creator are the same surface, alternating: a chapter is written → the user reads it in the immersive reader → it ends on an open question that becomes the next fork. The reading _is_ the reward that pulls the user back into creating, the cliffhanger is the honest pull to return (Zeigarnik effect — not manufactured exit-guilt), and the user's reaction to each chapter is the steering signal for the next. Witnessing every chapter being born is both more entertaining (serialization psychology) and higher-attachment.

### Read the completed story as a polished, immersive experience

**Writer** — When my story is finished, I want to read it in a real book-like reader — clean typography, chapter navigation, immersive layout — rather than a text-file dump, so I can enjoy it as a finished work.

The entertainment value of Mythos is equally in the creation process and in reading the finished story; the reading experience should feel like a real book.

### Export the story as a publishable eBook

**Writer** — When I want my story off the platform, I want Mythos to package the manuscript into a properly formatted EPUB with table of contents and chapter navigation, so I can open it in Kindle, Apple Books, or Kobo.

Once complete, Mythos packages the manuscript into a styled, navigable EPUB ready for the major readers.

### Share the story with others

**Writer** — When I want someone else to read what I made, I want shareable links, export formats, and access controls, so I can share my story on my own terms.

Mythos provides shareable links, export formats, and access controls so users can share their stories with readers.

---

## Platform — Access & Distribution

### Use Mythos anywhere, on any device

**Writer** — When I want to work wherever I am, I want Mythos as a mobile-first web app with an optional desktop app for offline or local-storage use, so I can create and read without being tied to one machine.

The primary surface is a mobile-first web app accessible in any browser — no install required. A local desktop app (Electron or equivalent) serves users who want offline access or local storage. Native mobile is a later target.

### Use Mythos as an MCP server

**Integrator (deferred)** — When I'm building my own product or workflow, I want to invoke Mythos's generation capabilities (a story, chapter, character, or bible) programmatically over an MCP server, so I can embed story creation in Claude, another assistant, or custom tooling.

Developers and power users — a game-master generating lore, an app embedding story generation — get programmatic access to the engine without the conversational creation UI.

### Use Mythos across multiple accounts and teams (multi-tenant)

**Integrator (deferred)** — When my organization or team uses Mythos, I want isolated per-tenant data, billing, and access control with collaboration where wanted, so I can trust that our stories and data stay separate and secure.

Mythos is built multi-tenant from the ground up. Each user or organization has isolated data, stories, and settings; billing, access control, and data isolation operate per-tenant; teams can collaborate on stories with appropriate permissions.
