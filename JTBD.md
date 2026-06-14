# Mythos — Jobs To Be Done

A forward-looking description of this project through the lens of every job it helps users accomplish.

> **Companion doc:** [`BEHAVIOR-SPEC.md`](BEHAVIOR-SPEC.md) is the mirror of this file — what Mythos _does today_ (as-built jobs, acceptance criteria, and BDD scenarios reverse-engineered from the code). This document is the **destination**; that one is the **current location**.

Each job is stated in canonical job-story form — **[Persona] — When [situation], I want to [motivation], so I can [outcome]** — followed by the design rationale. The one persona, **Writer**, is defined in `.safeword-project/personas.md`. Jobs labeled _Maintainer_ describe the system itself, not personas we build for today.

---

## Who this is for

Mythos is a **creative tool, not a content platform** — it optimizes for the person _making_ a story, not an audience browsing others' stories. There is **one persona**, defined in `.safeword-project/personas.md`:

- **Writer.** A fiction author moving from a loose idea toward a structured story and first-draft manuscript. Wants to make the _meaningful_ decisions and have the drudgery — blank-page paralysis, continuity bookkeeping, formatting — removed; the payoff is an output they feel deep ownership over. Everything optimizes for them. The Writer also _reads_ their finished work in a lean-back mode (see _Fork density is a user-controlled dial_), so "Reader" is a mode of the Writer, not a separate persona.

**Deferred — not a second persona.** A **Reader** who consumes _other_ writers' stories becomes real only if Mythos earns its way into a content platform. Until then the only user is the Writer. For v1, the Writer uses Mythos as a desktop app; later surfaces may include web, mobile, and chat access through MCP.

---

## Design Principles

These principles govern _how_ the jobs below are delivered. They exist because the research on creative-tool attachment and AI fiction quality points somewhere counterintuitive.

### Mechanically effortless, expressively yours

"Effortless" and "deep emotional attachment" pull in opposite directions. Attachment comes from being a thing's **causal, visible co-creator**, not its commissioner — the IKEA effect, and psychological-ownership research showing that automating the _expressive_ act destroys ownership and agency. A one-click "type a sentence, get a novel" product would produce homogenized AI slop _and_ kill attachment at once, because the user did nothing they can point to as their own.

So **"effortless" means mechanically effortless, never expressively effortless.** Strip the drudgery — blank-page paralysis, continuity bookkeeping, formatting, "what comes next" mechanics. Keep and actively stage the expressive decisions, because those decisions _are_ the entertainment and _are_ the source of attachment. The unit of the product is **the meaningful decision, made delightful** — not the prompt, not the chat.

### Creation is the entertainment

Mythos must hook the Writer before it asks for patience. Within the first minute, the Writer should see **authored proof**: a vivid reflection of their premise, a small set of sharply different directions, and one visible choice that immediately changes what Mythos shows next. The first minute is not onboarding or explanation; it is the smallest complete taste of co-creation.

From there, Mythos should draw the Writer into their own rabbit hole by progressively increasing personal specificity. Each step should reveal something that feels latent in the Writer's premise — a hidden wound, forbidden desire, moral contradiction, image, voice, or consequence — then ask for one meaningful choice that makes the story more theirs. By the end of the opening scene, the Writer should not merely approve a generated sample; they should recognize a story they helped uncover and want to know what happens next.

This is not a tutorial. Help is contextual and secondary. The Writer learns Mythos by watching their choices matter.

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

Crucially, dialing density down never costs agency: the expressive decisions remain **available on demand** (the user can always request a fork), so lean-back mode _defers_ authorship rather than removing it. This is the concrete resolution of "Reader is a mode of the Writer" — reading is authoring with the dial at zero.

---

## Creation — Ideation & Concept

### Turn a raw idea into a developed story concept

**Writer** — When I have only a rough premise ("a detective who can see memories") and don't know how to grow it into something I could actually write, I want Mythos to interview me about intent, stakes, tone, and genre and synthesize a complete creative brief, so I can start from a solid foundation instead of a blank page.

Mythos conducts a conversational interview to clarify intent, stakes, tone, and genre — then synthesizes a full story concept that serves as the creative foundation for everything that follows.

### Choose the right story direction before expansion

**Writer** — When Mythos turns my rough premise into a story concept, I want to compare alternatives, redirect the tone, and edit the concept until it feels like the story I actually want to make, so every later asset and chapter grows from a direction I believe in.

The concept is the first major authorship checkpoint. The Writer can ask for variations, steer the creative direction, or edit the concept directly before Mythos expands it into the broader story world.

### Build a complete world before writing a single chapter

**Writer** — When my concept is set but the world behind it is still thin, I want Mythos to generate interconnected planning assets — concept, research, critical perspectives, settings, plot, themes, characters, timeline, writing style — as living documents I can read and edit, so I can write on top of a fully realized world.

Each asset is stored as a living document the user can read, edit, and collaborate on with the AI.

### Understand the world deeply, not just broadly

**Writer** — When my world is broad but generic, I want Mythos to identify the areas in the research and settings that need depth and generate focused deep-dives on each, so I can have authentic specificity without padding.

Generic world-building isn't enough; Mythos targets the spots that need deeper investigation rather than padding everything uniformly.

### Explore the story through multiple critical lenses

**Writer** — When I want intellectual and thematic depth baked in from the start, I want Mythos to generate literary analysis through feminist, Marxist, postcolonial, and other critical-theory lenses, so I can write with thematic intention rather than adding it in revision.

For writers who want intellectual depth and thematic intentionality baked into the story, not bolted on later.

### Use genre-appropriate craft guidance

**Writer** — When my story sits in a genre with its own conventions, tropes, and structural expectations, I want Mythos to apply genre-specific craft guidance during generation, so I can have the genre's craft handled well rather than generically.

Mythos applies genre-specific writing templates (Fantasy, Crime, Horror, Romance, Sci-Fi, Literary Fiction, Mystery/Thriller, Historical Fiction, etc.) that inform how each genre's craft is handled.

### Track literary references and intertextual influences

**Writer** — When I'm deliberately working with allusions, influences, and literary references, I want Mythos to capture them as a dedicated asset, so I can manage the story's literary dialogue intentionally.

Sophisticated writers manage deliberate allusions and influences; Mythos gives them a structured place to track the story's literary dialogue.

---

## Creation — Drafting & Writing

### Know exactly what happens in every chapter before writing it

**Writer** — When I'm about to draft but have no roadmap, I want Mythos to generate a full chapter outline and a detailed per-chapter plan (scene breakdown, POV, character arcs, thematic elements, pacing), so I can write each chapter knowing exactly what it needs to do.

Writers have a complete roadmap before prose begins.

### Start with a polished opening scene before committing to chapters

**Writer** — When I am still deciding whether this story is worth following, I want Mythos to turn my early choices into a gripping opening scene that reflects my taste and raises questions I personally want answered, so I am pulled into my own story before committing to the full manuscript.

The opening scene is the first retention milestone. It establishes voice and tone, but its deeper job is to prove that creation itself is entertaining: the Writer can see their choices echoed in the prose, feel the story becoming more specific, and leave the scene with a live curiosity gap.

### Build the manuscript incrementally, chapter by chapter

**Writer** — When I don't want to commit to a whole manuscript sight-unseen, I want Mythos to generate one chapter at a time and surface each for my reaction, so I can continue or redirect before more is written.

Users see a chapter, react to it, and decide whether to continue or redirect — not commit to generating the entire manuscript blindly.

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

### Handle model content limits without losing the Writer's work

**Writer** — When the story I ultimately want to write runs into model or provider content limits, I want Mythos to try an allowed fallback model where possible, or stop clearly if no configured model can generate it, so I understand what happened and can decide how to continue without losing work.

Content refusals are not transient failures and should not be retried blindly. Mythos must distinguish them from outages or rate limits, preserve story state, and route to a configured fallback model or provider when the requested content is allowed by Mythos and that provider can handle it. If no configured model can generate the requested content, Mythos should tell the Writer that clearly, avoid vague or moralizing language, and offer compliant alternatives such as changing the framing, reducing explicitness, generating adjacent planning material, switching to a permitted summary, or letting the Writer edit/export the existing story state without losing progress.

---

## Reading — The Final Product

### Read the story as it's born (creation and reading are one surface)

**Writer** — When a new chapter is written, I want to read it immediately in an immersive reader that ends on the open question becoming my next fork, so I can witness the story being born and let my reaction steer what comes next.

The reader and the creator are the same surface, alternating: a chapter is written → the user reads it in the immersive reader → it ends on an open question that becomes the next fork. The reading _is_ the reward that pulls the user back into creating, the cliffhanger is the honest pull to return (Zeigarnik effect — not manufactured exit-guilt), and the user's reaction to each chapter is the steering signal for the next. Witnessing every chapter being born is both more entertaining (serialization psychology) and higher-attachment.

### Read the completed story as a polished, immersive experience

**Writer** — When my story is finished, I want to read it in a real book-like reader — clean typography, chapter navigation, immersive layout — rather than a text-file dump, so I can enjoy it as a finished work.

The entertainment value of Mythos is equally in the creation process and in reading the finished story; the reading experience should feel like a real book.

### Export the story as a publishable eBook

**Writer** — When I want my story off the platform, I want Mythos to package the manuscript into a properly formatted EPUB and make it easy to send to my reading device, so I can open it in Kindle, Apple Books, Kobo, or another reader without fighting file-transfer mechanics.

Once complete, Mythos packages the manuscript into a styled, navigable EPUB with table of contents and chapter navigation, then helps deliver it to the Writer's preferred reader. Kindle support should include a low-friction path such as Send to Kindle instructions, email delivery, or a direct handoff if the platform supports it; the Writer should not need to understand EPUB/MOBI/AZW compatibility details to read their story.

### Share the story with others

**Writer** — When I want someone else to read what I made, I want shareable links, export formats, and access controls, so I can share my story on my own terms.

Mythos provides shareable links, export formats, and access controls so users can share their stories with readers.

---

## Platform — Access & Distribution

### Use Mythos as a focused desktop app first

**Writer** — When I am building a story, I want Mythos as a focused desktop app, so I can work in a durable, local-first creative environment without depending on a browser or mobile session.

The v1 surface is desktop-only. Browser, mobile, and cross-device access are later distribution surfaces for the same Writer experience, not v1 requirements.

### Use Mythos as an MCP server

**Writer** — When I'm working from ChatGPT, Claude, or another assistant, I want to access my Mythos stories and generation tools through MCP, so I can keep creating and steering my story without leaving the conversation I'm already in.

MCP is a Writer access surface, not a developer persona. It lets the same Writer bring Mythos into the assistant they already use: create a concept, inspect or edit the story bible, generate a chapter, request forks, or continue a draft from chat.

### Use Mythos across multiple accounts and teams (multi-tenant)

**Writer** — When my organization or team uses Mythos, I want isolated per-tenant data, billing, and access control with collaboration where wanted, so I can trust that our stories and data stay separate and secure.

Mythos is built multi-tenant from the ground up. Each user or organization has isolated data, stories, and settings; billing, access control, and data isolation operate per-tenant; teams can collaborate on stories with appropriate permissions.

### Meter token usage for billing

**Maintainer** — When Mythos generates work for a Writer, I want every model call metered by token usage and attributed to the right account, so Mythos can bill sustainably while preserving the Writer's creative flow.

Token accounting is an internal billing primitive, not a user-facing "cost visibility" feature. V1 pricing starts with token-based billing: a free tier capped around early exploration (likely a few opening scenes, not full chapter generation), then a subscription roughly comparable to Netflix with usage overages beyond the included token allowance. Pricing should target roughly a 50% gross margin against model costs while still routing to the best model for each job.

---

## Platform — Technical Foundation

These jobs are framed from the viewpoint of whoever **builds and operates** Mythos (a maintainer, or the running system acting on the Writer's behalf) — they are architectural requirements that serve the Writer's experience indirectly rather than jobs the Writer performs directly.

### Run on TypeScript end to end

**Maintainer** — When I'm building and extending Mythos, I want the entire stack — server, client, shared types — in TypeScript, so I can rely on end-to-end type safety across API, data models, and UI and keep the codebase accessible to the broadest contributor base.

End-to-end type safety across the API, data models, and UI; one language across the stack.

### Control API costs without sacrificing quality where it matters

**Maintainer** — When different generation tasks reward different model strengths, I want Mythos to route each call to the best model for that job and cache repeated system prompts, so I can keep costs down without weakening the writing where model choice matters.

Routing is based on fit, not just size: lightweight models can handle summaries and quick analysis, planning models can handle structure and asset creation, and stronger creative models can handle narrative writing or complex judgment calls. Prompt caching on Anthropic calls reduces costs by up to 90% on repeated system prompts.

### Prevent wasted work from API failures

**Maintainer** — When a transient API error hits mid-generation, I want retry logic with exponential backoff that separates transient errors (rate limits, timeouts) from permanent ones (content refusals), so I can ensure users never lose progress to a recoverable hiccup.

Transient errors retry; permanent failures surface; users never lose progress to a recoverable API hiccup.

### Calibrate reasoning depth for hard creative work

**Maintainer** — When a narrative problem requires deeper judgment, I want Mythos to choose the right reasoning mode and effort level for the task, so complex creative decisions get enough deliberation without wasting tokens on simple work.

Reasoning controls should be model-aware and current with provider APIs. Some models expose fixed thinking-token budgets; newer Anthropic models favor adaptive thinking with effort levels instead. Mythos should treat both as implementation details behind a durable routing policy: use deeper reasoning for plot logic, thematic tradeoffs, continuity repair, and difficult prose choices; keep routine summaries and formatting tasks shallow.
