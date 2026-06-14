# Mythos Visual Design Brief

## Thesis

Mythos should feel like a private writing desk where the story is already alive — not a SaaS dashboard, not a chat app, and not a generic AI prompt box.

The interface exists to make creation entertaining. The Writer should see authored proof within the first minute: Mythos understands the premise, exposes a sharper pressure point, offers meaningful directions, and visibly changes the story when the Writer chooses.

---

## Non-Negotiables

1. **Creation is the entertainment.** The UI must make choosing, redirecting, and editing feel like the product, not setup before the product.
2. **Authored proof comes first.** The first minute must show the Writer that their premise has become more specific because of their input.
3. **The manuscript is the center.** The story artifact — concept, opening scene, chapter, or bible — owns the screen.
4. **AI lives in the margin.** Suggestions, forks, questions, and continuity notes support the artifact instead of replacing it with chat.
5. **Choices visibly become canon.** When the Writer chooses or edits, the interface should show where that decision landed and what it now affects.

---

## First-Minute Flow

The first prototype should prove this loop, even with mocked content:

1. **Premise:** the Writer enters the story idea, image, character, or contradiction they cannot stop thinking about.
2. **Mirror:** Mythos reflects the premise back as a vivid, specific paragraph.
3. **Pressure point:** Mythos names the emotional or moral contradiction that can power the story.
4. **Fork:** Mythos offers three sharply different directions, each with a one-line tradeoff.
5. **Mutation:** the Writer chooses one direction and the concept visibly changes.
6. **Opening-scene pull:** Mythos previews the first scene in a way that raises a question the Writer personally wants answered.

This is not onboarding. The Writer learns Mythos by watching their choices matter.

---

## Layout Pattern

Use one durable pattern for the desktop app:

- **Left rail:** story map, assets, chapters, export.
- **Center canvas:** the current story artifact in a quiet editorial layout.
- **Right margin:** forks, questions, contradictions, callbacks, and continuity warnings.

Default state: center canvas first, margins quiet. Mythos should interrupt only when a decision is meaningful or a contradiction matters.

---

## Visual Direction

The visual language should be warm, literary, private, and restrained.

Use:

- book-like line lengths;
- editorial typography for prose and concepts;
- quiet panels and low-contrast dividers;
- warm paper/ink tones;
- restrained accent color for active choices and canon markers.

Avoid:

- chatbot chrome;
- neon AI gradients;
- dashboard-card clutter;
- fantasy-game ornament;
- generic minimalist writing-app emptiness.

Exact tokens, component variants, and motion specs should come from the prototype after the first-minute loop is working.

---

## Prototype Target

Build one static route that demonstrates:

```text
premise capture → authored proof → fork choice → visible mutation → opening-scene preview
```

Success means a reviewer can understand the product without explanation: Mythos is a story-making experience where the Writer’s choices visibly shape the work.

Do not build a full design system yet. Define only the tokens and components needed to prove this route.
