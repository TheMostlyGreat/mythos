# Mythos — Jobs To Be Done

A forward-looking description of this project through the lens of every job it helps users accomplish.

---

## Who this is for

Mythos is a **creative tool, not a content platform** — it optimizes for the person _making_ a story, not an audience browsing a catalog of others' stories. Two personas, defined in `.safeword-project/personas.md`:

- **The Author (primary).** A person with a story in them but without a novelist's craft, time, or discipline for the blank page. They want to make the _meaningful_ decisions and have the drudgery removed; the payoff is an output they feel deep ownership over. Everything optimizes for them first. The Author also _reads_ their finished work in a lean-back mode (see _Fork density is a user-controlled dial_, below), so "Reader" is a mode of the Author, not a separate persona.
- **The Integrator (secondary).** A developer who invokes Mythos's generation engine programmatically through the MCP server — a game-master generating lore, an app embedding story creation — wanting the engine without the conversational UI.

A **Reader** who consumes _other_ authors' finished stories is explicitly **deferred**: that persona appears only if Mythos earns its way into being a platform. Until then, the only reader is the Author enjoying their own work.

---

## Design Principles

These principles govern _how_ the jobs below are delivered. They exist because the research on creative-tool attachment and AI fiction quality points somewhere counterintuitive.

### Mechanically effortless, expressively yours

The core tension in this product: "effortless" and "deep emotional attachment" pull in opposite directions. Attachment to a created thing comes from being its **causal, visible co-creator** — not its commissioner (the IKEA effect; psychological-ownership research shows automating the _expressive_ act destroys ownership and agency). A one-click "type a sentence, get a novel" product would simultaneously produce homogenized AI slop _and_ kill the user's attachment, because they did nothing they can point to and call their own.

So **"effortless" means mechanically effortless, never expressively effortless.** Strip out the drudgery — blank-page paralysis, continuity bookkeeping, formatting, "what comes next" mechanics. Keep, and actively stage, the expressive decisions, because those decisions _are_ the entertainment and _are_ the source of attachment. The unit of the product is **the meaningful decision, made delightful** — not the prompt, not the chat.

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

### Fork density is a user-controlled dial

The cadence above is the _default_. But fork density is a **dial the user controls**, and that single mechanism is how one engine serves both a lean-forward author and a lean-back reader — without a second product, a second mode, or a second persona.

- **Forks up → author mode (lean-forward).** Decisions surface at every tier; the user is the visible co-creator making the ~8–15 meaningful choices that earn ownership.
- **Forks near zero → reading mode (lean-back).** The engine writes through the bible in near-continuous flow and the user mostly _receives_ the story — the "beach novel" posture, same engine, divergence turned down.

Crucially, dialing density down never costs agency: the expressive decisions remain **available on demand** (the user can always request a fork), so lean-back mode _defers_ authorship rather than removing it. This is the concrete resolution of "Reader is a mode of the Author" — reading is authoring with the dial at zero.

---

## Creation — Ideation & Concept

### Turn a raw idea into a developed story concept

When a user has a rough premise ("a detective who can see memories"), they need help expanding it into a complete creative brief. Mythos conducts a conversational interview to clarify intent, stakes, tone, and genre — then synthesizes a full story concept that serves as the creative foundation for everything that follows.

### Review and shape the concept before committing to generation

After a concept is drafted, the user needs to see it, react to it, and refine it — in conversation — before the expensive downstream generation begins. They can ask for variations, redirect the tone, or edit the concept document directly like a doc. Only then does generation proceed.

### Build a complete world before writing a single chapter

Before prose, users need a fully realized world. Mythos generates interconnected planning assets — concept, research, critical perspectives, settings, plot, themes, characters, timeline, writing style — each stored as a living document the user can read, edit, and collaborate on with the AI.

### Understand the world deeply, not just broadly

Generic world-building isn't enough. Mythos identifies areas within the research and settings that need deeper investigation, then generates focused deep-dive documents for each — ensuring authentic specificity without padding.

### Explore the story through multiple critical lenses

Mythos generates literary analysis from feminist, Marxist, postcolonial, and other critical theory perspectives — for writers who want intellectual depth and thematic intentionality baked into the story, not added in revision.

### Use genre-appropriate craft guidance

Genre conventions, tropes, and structural expectations vary widely. Mythos applies genre-specific writing templates (Fantasy, Crime, Horror, Romance, Sci-Fi, Literary Fiction, Mystery/Thriller, Historical Fiction, etc.) that inform how each genre's craft is handled during generation.

### Track literary references and intertextual influences

Sophisticated writers manage deliberate allusions, influences, and literary references. Mythos captures these as a dedicated asset — giving writers a structured way to track the story's literary dialogue.

---

## Creation — Drafting & Writing

### Know exactly what happens in every chapter before writing it

Mythos generates a structured chapter outline for the entire story, then a detailed per-chapter planning document — covering scene breakdown, POV, character arcs, thematic elements, and pacing notes. Writers have a complete roadmap before prose begins.

### Start with a polished opening scene before committing to chapters

The opening scene establishes voice and tone for everything that follows. Mythos generates a dedicated opening scene — first a planning pass, then a full narrative scene — which becomes the anchor for the rest of the manuscript.

### Build the manuscript incrementally, chapter by chapter

Users need to see a chapter, react to it, and decide whether to continue or redirect — not commit to generating the entire manuscript blindly. Mythos generates one chapter at a time, surfacing the result for review before proceeding.

### Get a full draft manuscript written

Mythos writes complete narrative chapters — full prose, full length — using the planning assets as context. The model maintains continuity, voice, and thematic consistency across the full manuscript.

### Edit any output directly, like a document

At any point in the process, the user should be able to open any generated asset or chapter and edit it directly — not just regenerate it. Edits are respected and preserved. The AI treats user edits as authoritative when continuing generation.

### Steer the story in conversation at any stage

The creation process is a conversation, not a form. At any step — concept, assets, chapters — the user should be able to say "make the protagonist younger," "shift the tone darker," or "I want the setting to be near-future Tokyo" and have the system update accordingly.

---

## Creation — Quality & Craft

These jobs exist because the default output of an aligned LLM is recognizable "slop" — homogenized, relentlessly positive, low-tension, cliché-dense. Hitting literary quality is an explicit job, not a byproduct.

### Make it sound like literature, not a chatbot

Mythos runs a craft layer over generation: an antislop revision pass that bans _pattern families_ (the "it's not X, it's Y" antithesis frame, mechanical tricolons, the puffery cluster — delve/tapestry/testament), forced **scene over summary** (readers feel scenes, not summaries), and **sensory grounding of stated emotion** ("her coffee went cold against her trembling fingers," never "she was sad"). Sentence rhythm is deliberately varied. The goal is prose a reader is engrossed by, with none of the recognizable AI tells.

### Be surprised by my own story

At every fork, the divergent options are genuinely different directions, not rephrasings of one beat (Verbalized Sampling). Surprise is both the entertainment and the diversity mechanism — the user discovers possibilities they wouldn't have thought of, while the system escapes its homogenizing default.

### Feel the tension

Mythos plans an explicit **affect and tension arc** for the story rather than defaulting to the AI's homogeneously positive register. Turning points, suspense, and high-arousal beats are planned deliberately — the single biggest measured lever on perceived story quality.

### Make it sound like _me_ (later)

Optionally, the user can have Mythos adapt prose voice to **their own writing** — uploading their prose so the output reads as theirs. This is the strongest quality lever in the research (fine-tuning on an author's own work) _and_ the strongest attachment lever, while sidestepping the legal and ethical problems of imitating other authors.

---

## Creation — Continuity & Control

### Keep the whole book consistent with itself (the story bible as canon)

This is the differentiator. The story bible isn't just an _output_ of the planning phase — it's the **persistent continuity engine** the writing phase reads from on every generation. Entities, world-rules, character voices, and established facts are injected as fixed canon so an 80k-word book doesn't drift, contradict itself, or lose voice over its length (the failure mode that intrinsically afflicts long LLM generation). When the user edits the bible, the canon updates and all downstream generation respects the change. When an edit contradicts already-written chapters, Mythos flags the conflict and offers a one-click retroactive fix ("chapter 2 still uses the old name — update?"). The bible is the user-editable source of truth the engine obeys, not a document it merely consulted once.

### Pause and resume without losing progress

Story generation takes time across multiple sessions. Mythos saves state at every phase and resumes from any point of incompleteness. It detects what's done and picks up exactly where work stopped.

### Generate story length and scope appropriate to the idea

Not every idea is a novel. Mythos infers whether a concept warrants a short story, novella, or novel — and generates only the assets and chapters appropriate to that scope, with user override options.

### Research per topic, not as a monolithic blob

Research findings are most useful when organized by topic. Mythos breaks research into per-topic documents, enabling targeted use of specific findings during chapter writing.

### Recover gracefully when a model fails

When an AI model is unavailable or fails, Mythos retries with the next best alternative and notifies the user — rather than surfacing a hard error that stops the pipeline.

---

## Reading — The Final Product

### Read the story as it's born (creation and reading are one surface)

The reader and the creator are the same surface, alternating. Rather than "generate the whole book, then read it," the loop is: a chapter is written → the user reads it in the immersive reader → it ends on an open question that becomes the next fork. The reading _is_ the reward that pulls the user back into creating, the cliffhanger is the honest pull to return (Zeigarnik effect — not manufactured exit-guilt), and the user's reaction to each chapter is the steering signal for the next. The user witnesses every chapter being born, which is both more entertaining (serialization psychology) and higher-attachment (they were there for all of it).

### Read the completed story as a polished, immersive experience

The entertainment value of Mythos is equally in the creation process and in reading the finished story. The reading experience should feel like a real book — clean typography, chapter navigation, immersive layout — not a text file dump.

### Export the story as a publishable eBook

Once complete, Mythos packages the manuscript into a properly formatted EPUB — with table of contents, chapter navigation, and styling — ready to open in Kindle, Apple Books, or Kobo.

### Share the story with others

A finished story should be easy to share. Mythos provides shareable links, export formats, and access controls so users can share their stories with readers.

---

## Platform — Access & Distribution

### Use Mythos anywhere, on any device

Mythos works wherever the user is. The primary surface is a mobile-first web app accessible in any browser — no install required. A local desktop app (Electron or equivalent) is available for users who want offline access or local storage. Native mobile is a later target.

### Use Mythos as an MCP server

Developers and power users can integrate Mythos's story generation capabilities directly into their own tools and workflows via an MCP server interface — enabling story creation to be invoked from Claude, other AI assistants, or custom tooling.

### Use Mythos across multiple accounts and teams (multi-tenant)

Mythos is built multi-tenant from the ground up. Each user or organization has isolated data, stories, and settings. Billing, access control, and data isolation operate per-tenant. Teams can collaborate on stories with appropriate permissions.

---

## Platform — Technical Foundation

### Run on TypeScript end to end

The entire stack — server, client, shared types — is TypeScript. This enables end-to-end type safety across the API, data models, and UI, and makes the codebase accessible to the broadest contributor base.

### Control API costs without sacrificing quality where it matters

Not every task needs the most expensive model. Mythos routes calls to the right tier: fast/cheap for quick analysis, medium for planning and asset creation, expensive for narrative writing. Prompt caching reduces costs by up to 90% on repeated system prompts.

### Prevent wasted work from API failures

Retry logic with exponential backoff separates transient errors (rate limits, timeouts) from permanent failures (content refusals). Users never lose progress to a recoverable API hiccup.

### Enable reasoning-heavy generation

Extended thinking support — with configurable token budgets — allows the AI to reason deeply on complex narrative problems before producing output.
