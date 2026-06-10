# Mythos Creative Process Improvement Plan

**Status**: Draft
**Created**: 2025-10-08
**Focus**: Enhancing the writing/creative workflow, not technical reliability

## Executive Summary

The Mythos creative process successfully produces high-quality, genre-appropriate fiction at unprecedented speed. However, it currently operates as a **linear generation pipeline** rather than a **collaborative creative tool**. This plan proposes restructuring the workflow to emphasize iterative refinement, voice development, and creative discovery—transforming Mythos from "automated ghostwriter" to "creative co-pilot."

**Current Process**: `Concept → Assets → Manuscript → Done`
**Proposed Process**: `Concept ⇄ Assets ⇄ Draft ⇄ Refine → Done`

---

## Current Process Analysis

### What We Actually Do Now

1. **User provides concept** (single sentence to paragraph)
2. **AI expands to full concept** (8,000+ character document)
3. **AI generates 28 planning assets** (characters, plot, themes, research, chapters)
4. **AI writes manuscript** (9 chapters of polished prose)
5. **User reviews final output**

### Strengths of Current Process

✅ **Speed**: 10-100x faster than traditional writing
✅ **Research synthesis**: Minutes instead of weeks
✅ **Structural coherence**: Planning prevents plot holes
✅ **Genre competence**: Reliably follows genre conventions
✅ **Quality**: Produces genuinely compelling prose (see Chapter 1 of "The Smoke and the Sacred")

### Weaknesses of Current Process

❌ **No iteration between phases**: Can't refine concept after seeing detailed assets
❌ **Generic voice**: Competent but lacks authorial distinctiveness
❌ **Rigid planning**: 28 documents before any prose—prevents creative discovery during drafting
❌ **No reader feedback simulation**: Straight to polished prose without beta reading
❌ **Unclear research utilization**: Did AI actually use the diesel mechanics research doc?
❌ **Linear workflow**: Assumes perfect planning is possible

---

## The Fundamental Creative Question

### Is This "Writing" or "Content Generation"?

**Traditional writing**:

- Writer makes every sentence-level choice
- Discovery happens through the act of writing
- Struggle with expression is part of the creative process
- Writer owns every word

**Mythos generation**:

- User makes high-level creative decisions (genre, premise, themes)
- AI executes sentence-level choices
- User evaluates and refines output
- User directs, AI writes

**Conclusion**: This is **"Directed Generative Writing"**

- Human is creative director
- AI is execution team
- Similar to film: director doesn't paint every frame but is the creative author
- **Writing is decision-making**, and the user makes the decisions that matter most

**Implication**: Optimize for **creative direction tools** not just automation:

- Better feedback mechanisms
- Easier pivoting and refinement
- Vision articulation tools
- Quality control checks

---

## Priority 1: Iterative Workflow (Critical)

### 1.1 Add Concept Review Checkpoint

**Current flow**:

```
User prompt → AI generates concept → Assets → Manuscript
```

**Proposed flow**:

```
User prompt → AI generates concept → USER REVIEWS →
├─ Approve → Proceed to assets
├─ Regenerate → New concept variation
└─ Edit → User tweaks concept directly
```

**Why this matters**:

- Concept determines everything downstream
- User may want "Margarethe as protagonist" after seeing full concept
- Cheaper to fix concept than regenerate 28 assets + 9 chapters

**Implementation**:

```python
# In story_builder.py
def build_story_interactive(self, user_prompt: str) -> Story:
    """Build story with review checkpoints."""

    # Generate initial concept
    concept = self._generate_concept(user_prompt)

    while True:
        # Show concept to user
        print("\n" + "="*60)
        print("STORY CONCEPT")
        print("="*60)
        print(concept['concept_markdown'][:1000] + "...")

        action = input("\n[a]pprove, [r]egenerate, [e]dit, [d]etails: ").lower()

        if action == 'a':
            break
        elif action == 'r':
            print("Regenerating with variation...")
            concept = self._generate_concept(user_prompt, variation=True)
        elif action == 'e':
            # Open in editor or accept inline changes
            concept = self._edit_concept(concept)
        elif action == 'd':
            print(concept['concept_markdown'])  # Show full text

    # Proceed to assets
    story = Story(title=concept['title'], ...)
    return self._build_assets(story)
```

**User experience**:

```
STORY CONCEPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Title: The Smoke and the Sacred

Protagonist: Lukas Brenner (38), mechanic-exorcist
Deuteragonist: Margarethe Kessler (34), chief engineer
Themes: Faith through labor, price of progress
Setting: Alternate 1930s Berlin...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[a]pprove, [r]egenerate, [e]dit, [d]etails:
```

**Estimated effort**: 4-6 hours
**Impact**: High - prevents wasted generation on unwanted concepts

---

### 1.2 Implement "First Chapter Test"

**Current flow**:

```
Assets generated → AI writes all 9 chapters → User sees result
```

**Proposed flow**:

```
Assets generated → AI writes Chapter 1 ONLY → USER REVIEWS →
├─ Approve voice/tone → Generate remaining chapters
├─ Adjust style → Regenerate Ch1 with tweaks → Review again
└─ Revise assets → Update character/theme docs → Regenerate Ch1
```

**Why this matters**:

- Voice and tone only become clear in actual prose
- Cheaper to fix after 1 chapter than after 9
- User can catch "this feels too light" or "not enough technical detail" early

**Implementation**:

```python
# In story_builder.py
def build_story_with_chapter_review(self, user_prompt: str) -> Story:
    """Build story with chapter 1 review checkpoint."""

    # ... concept and assets generation

    # Generate chapter 1 first
    print("\n🔖 Generating Chapter 1 as test...")
    chapter_1 = self._generate_chapter(story, 'chapter_1')

    while True:
        # Show preview
        preview = chapter_1[:800]
        print("\n" + "="*60)
        print("CHAPTER 1 PREVIEW")
        print("="*60)
        print(preview + "\n...")

        action = input("\n[a]pprove, [r]egenerate (adjust style), [f]ull chapter, [t]weak: ").lower()

        if action == 'a':
            # Save chapter 1 and proceed with rest
            self._save_chapter(story, 'chapter_1', chapter_1)
            break
        elif action == 'r':
            # Get style adjustment
            adjustment = input("What to adjust? (more/less: formal, technical, atmospheric, etc.): ")
            chapter_1 = self._generate_chapter(story, 'chapter_1', style_adjustment=adjustment)
        elif action == 'f':
            print("\n" + chapter_1)  # Show full chapter
        elif action == 't':
            # Tweak generation parameters
            temp = float(input("Temperature (current 1.0): "))
            tone = input("Tone adjustment: ")
            chapter_1 = self._generate_chapter(story, 'chapter_1', temperature=temp, tone=tone)

    # Generate remaining chapters with approved style
    self._write_remaining_chapters(story, style_from_chapter_1=chapter_1)
```

**User experience**:

```
CHAPTER 1 PREVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The Schaublin lathe hadn't been fed power in six days,
but it spun anyway.

Lukas Brenner stood in the doorway of the Müller Textile
Works, watching the drive belt slap against dead pulleys...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Voice: ✓ Hardboiled, technical
Tone: ✓ Noir atmosphere
Pacing: ✓ Grounded opening

[a]pprove, [r]egenerate, [f]ull chapter, [t]weak:
```

**Estimated effort**: 5-7 hours
**Impact**: High - catches voice/tone issues before expensive full generation

---

### 1.3 Enable Mid-Manuscript Pivoting

**Current flow**:

```
All 9 chapters generated → User discovers chapter 3 momentum dies →
No recourse except regenerate everything
```

**Proposed flow**:

```
Chapters 1-3 generated → USER REVIEWS →
├─ Approve pacing → Continue with chapters 4-9 as planned
├─ Pivot plot → Regenerate chapter outlines 4-9 based on what's working
└─ Character shift → Adjust POV balance or character arcs for remaining chapters
```

**Why this matters**:

- Creative discovery happens during writing, not just planning
- "Margarethe is more compelling than Lukas" may only become clear by chapter 3
- Expensive to regenerate all chapters; cheaper to adjust remaining ones

**Implementation**:

```python
# In story_builder.py
def build_story_adaptive(self, user_prompt: str, review_points: list[int] = [3, 6]) -> Story:
    """Build story with mid-manuscript review points."""

    # ... concept and assets generation

    for checkpoint in review_points + [len(story.manuscript_metadata)]:
        # Generate chapters up to checkpoint
        self._write_chapters_batch(story, up_to=checkpoint)

        if checkpoint < len(story.manuscript_metadata):
            # Mid-manuscript review
            print(f"\n📊 Chapters 1-{checkpoint} complete")
            print("Review recent chapters before proceeding...")

            action = input("\n[c]ontinue as planned, [p]ivot remaining chapters, [s]kip to end: ").lower()

            if action == 'p':
                # Analyze what's working
                print("What's working so far?")
                strengths = input("  Strengths: ")
                issues = input("  Issues to address: ")

                # Regenerate remaining chapter outlines
                remaining_chapters = list(story.manuscript_metadata.keys())[checkpoint:]
                self._revise_chapter_outlines(
                    story,
                    chapters=remaining_chapters,
                    based_on_written=list(story.manuscript_metadata.keys())[:checkpoint],
                    strengths=strengths,
                    issues=issues
                )

                print(f"✓ Revised outlines for chapters {checkpoint+1}-{len(story.manuscript_metadata)}")
```

**User experience**:

```
📊 Chapters 1-3 complete (review checkpoint)

Chapter 1: ✓ Strong hook, Josef's voice compelling
Chapter 2: ✓ Margarethe introduction, tension builds
Chapter 3: ⚠ Pacing slows, too much exposition

What's working?
  Strengths: Josef mystery, Lukas/Margarethe dynamic
  Issues: Need to accelerate Machine Witch reveal, cut factory tour scene

✓ Revised outlines for chapters 4-9
  - Chapter 4: Josef encounter moved earlier
  - Chapters 5-6: Machine Witch active threat (not shadowy)
  - Chapter 7-9: Compressed to maintain momentum

Continue with revised plan? [y/n]:
```

**Estimated effort**: 8-10 hours
**Impact**: High - enables creative discovery during drafting, not just planning

---

## Priority 2: Voice Development

### 2.1 Voice Calibration with Examples

**Current approach**:

- Writing style guide says "hardboiled prose," "short sentences," "noir atmosphere"
- AI synthesizes generic interpretation of these abstract labels

**Problem**:

- No examples of _specific_ preferred style
- Results in competent but generic voice
- Doesn't capture authorial distinctiveness

**Proposed approach**:

```
User provides style examples → AI analyzes patterns →
Generates test paragraph → User rates similarity →
AI adjusts → Lock in voice parameters
```

**Implementation**:

```python
# In story_builder.py or new voice_calibration module
def calibrate_voice(self, examples: list[str], target_genre: str) -> dict:
    """Calibrate narrative voice based on examples."""

    # Analyze provided examples
    analysis = self._analyze_writing_samples(examples)

    # Extract patterns
    voice_params = {
        "avg_sentence_length": analysis['sentence_stats']['mean'],
        "vocab_complexity": analysis['lexical_density'],
        "metaphor_frequency": analysis['figurative_language']['rate'],
        "dialogue_ratio": analysis['dialogue_percentage'],
        "tense_preference": analysis['tense'],
        "pov_style": analysis['pov'],
        "paragraph_rhythm": analysis['paragraph_patterns'],
        # ... more metrics
    }

    # Generate test paragraph in target style
    test_prompt = f"Write opening paragraph for {target_genre} story in this style"
    test_para = self._generate_with_voice(test_prompt, voice_params)

    # User feedback loop
    while True:
        print("\nTEST PARAGRAPH:")
        print(test_para)
        print("\nVOICE PARAMETERS:")
        for key, val in voice_params.items():
            print(f"  {key}: {val}")

        rating = input("\nSimilarity to examples (1-5): ")
        if int(rating) >= 4:
            break

        adjustment = input("What to adjust? (sentence_length/complexity/metaphors/etc.): ")
        direction = input("More or less?: ")

        # Adjust parameters
        voice_params = self._adjust_voice_param(voice_params, adjustment, direction)
        test_para = self._generate_with_voice(test_prompt, voice_params)

    return voice_params
```

**User experience**:

```
VOICE CALIBRATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provide 1-3 paragraphs in your preferred style:
(Paste example, press Enter twice when done)

> The Schaublin lathe hadn't been fed power in six days,
> but it spun anyway. Lukas Brenner stood in the doorway...

Analyzing style...
  ✓ Sentence length: 12-18 words (varied)
  ✓ Vocabulary: Technical + accessible
  ✓ Metaphors: Sparse, grounded
  ✓ Tone: Hardboiled, matter-of-fact

Generating test paragraph...

TEST PARAGRAPH:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The diesel engine coughed black smoke, then died.
Margarethe knelt beside it, fingers already reaching for
the compression tester. Third failure this week, always
at 3,000 RPM, always cylinder four.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Similarity to your examples (1-5): 4

✓ Voice calibrated
Proceed with full manuscript in this style? [y/n]:
```

**Estimated effort**: 10-12 hours
**Impact**: Medium-High - creates distinctive voice, but requires user to provide good examples

---

### 2.2 Comp Title Analysis

**Current approach**:

- User says "dieselpunk noir"
- AI interprets abstractly

**Proposed approach**:

- User provides 2-3 comp titles: "Like China Miéville's _Perdido Street Station_ + Raymond Chandler"
- AI analyzes those specific works
- Incorporates structural and stylistic insights

**Implementation**:

```python
# In story_builder.py
def analyze_comp_titles(self, titles: list[str], user_concept: str) -> dict:
    """Analyze comparison titles to inform story generation."""

    insights = {}

    for title in titles:
        # Fetch summary/analysis of the work (via web search or knowledge base)
        analysis = self._fetch_work_analysis(title)

        insights[title] = {
            "narrative_structure": analysis['plot_structure'],
            "voice_characteristics": analysis['prose_style'],
            "thematic_elements": analysis['themes'],
            "pacing_rhythm": analysis['pacing'],
            "character_archetypes": analysis['character_types'],
        }

    # Synthesize how to apply to user's concept
    synthesis = call_llm(
        prompt=f"""
        User wants to write: {user_concept}

        Comparison titles provided:
        {json.dumps(insights, indent=2)}

        How should we incorporate elements from these works?
        What should we emphasize? What should we differentiate?
        """,
        tier="medium"
    )

    return {
        "comp_insights": insights,
        "synthesis": synthesis,
        "recommendations": self._extract_recommendations(synthesis)
    }
```

**User experience**:

```
COMPARISON TITLE ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your comp titles:
1. China Miéville - Perdido Street Station
2. Raymond Chandler - The Big Sleep

Analyzing...

Miéville: Perdido Street Station
  ✓ Industrial Gothic atmosphere
  ✓ Non-human entities with agency
  ✓ City as character
  ✓ Baroque, dense prose
  → Apply: Berlin as living entity, demons as non-human intelligence

Chandler: The Big Sleep
  ✓ Hardboiled first-person perspective
  ✓ Cynical but moral protagonist
  ✓ Mystery structure
  ✓ Lean, sharp dialogue
  → Apply: Lukas's voice, investigation framework

SYNTHESIS:
Your story should combine Miéville's rich world-building and
occult mechanics with Chandler's lean prose and noir pacing.

Key differentiators:
  - Working-class protagonist (vs Chandler's PI, Miéville's academic)
  - Practical mysticism (vs high-concept weird)
  - 1930s historical grounding (vs Chandler's present, Miéville's fantasy)

Proceed with this synthesis? [y/n]:
```

**Estimated effort**: 8-10 hours
**Impact**: Medium - creates more distinctive stories, requires external work analysis

---

## Priority 3: Quality & Reader Feedback

### 3.1 AI Beta Reader

**Current approach**:

- Generate polished prose
- User reviews (if they have time/expertise)
- No intermediate reader feedback

**Proposed approach**:

- After manuscript generation, run "beta reader AI"
- Simulates naive reader asking questions
- Flags confusion, pacing issues, character inconsistencies

**Implementation**:

```python
# In new beta_reader module
def beta_read_chapter(chapter_text: str, story_context: dict) -> dict:
    """Simulate beta reader feedback on chapter."""

    feedback = call_llm(
        prompt=f"""
        You are a beta reader for this story. Read this chapter and provide feedback.

        Story context: {story_context['concept_summary']}
        Characters: {story_context['main_characters']}

        Chapter text:
        {chapter_text}

        Provide feedback on:
        1. Confusion points: What was unclear or confusing?
        2. Pacing: Did you feel engaged or did it drag?
        3. Character voice: Were characters distinct and believable?
        4. Emotional beats: Did intended moments land?
        5. Questions raised: What do you want to know more about?
        6. Overall impression: Rate 1-5 stars and explain

        Be honest and specific. Point to exact lines when possible.
        """,
        tier="medium"
    )

    return {
        "feedback": feedback,
        "issues": self._extract_issues(feedback),
        "rating": self._extract_rating(feedback)
    }

def beta_read_full_manuscript(story: Story) -> dict:
    """Beta read entire manuscript with holistic feedback."""

    chapter_feedback = []
    for chapter_key in story.manuscript_metadata.keys():
        chapter_text = self._load_chapter(story, chapter_key)
        feedback = beta_read_chapter(chapter_text, story.get_context())
        chapter_feedback.append((chapter_key, feedback))

    # Holistic feedback
    overall = call_llm(
        prompt=f"""
        You've read all {len(chapter_feedback)} chapters. Provide overall feedback:

        1. Story arc: Does it build effectively?
        2. Character development: Do characters grow/change believably?
        3. Pacing across chapters: Are there slow sections?
        4. Thematic coherence: Are themes woven throughout?
        5. Ending satisfaction: Does conclusion satisfy setup?

        Individual chapter ratings: {[f['rating'] for _, f in chapter_feedback]}
        """,
        tier="medium"
    )

    return {
        "chapter_feedback": chapter_feedback,
        "overall_feedback": overall,
        "recommended_revisions": self._generate_revision_suggestions(chapter_feedback, overall)
    }
```

**User experience**:

```
BETA READER FEEDBACK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Chapter 1: The Voice in the Lathe (★★★★☆ 4/5)

Strengths:
  ✓ Compelling opening hook
  ✓ Strong atmospheric detail
  ✓ Josef revelation is genuinely unsettling

Issues:
  ⚠ Hand trembling mentioned 4 times - feels repetitive (lines 63, 76, 99, 132)
  ⚠ Funke's "too-observant eyes" mentioned twice in quick succession
  ? How did Lukas become a mechanic-exorcist? (backstory unclear)
  ? Why is Margarethe coming to him specifically?

Pacing: Strong throughout, minor drag in workshop scene (lines 90-140)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OVERALL MANUSCRIPT (Chapters 1-9): ★★★★☆ 4/5

Arc: Strong setup → investigation → revelation → climax flows well
Characters: Lukas compelling, Margarethe could use more agency in Ch 4-6
Pacing: Ch 1-3 strong, Ch 5-6 slow (factory tour drags), Ch 7-9 strong
Themes: "Faith through labor" well-executed, "price of progress" could be sharper

Recommended revisions:
  1. Trim workshop exposition in Ch 1 (cut 10-15%)
  2. Give Margarethe more active role in Ch 4-6
  3. Compress or cut factory tour scene in Ch 5
  4. Strengthen Machine Witch motivation in final confrontation

Generate revision suggestions? [y/n]:
```

**Estimated effort**: 12-15 hours
**Impact**: High - catches issues before user reads full manuscript, provides actionable feedback

---

### 3.2 Tension & Impact Analysis

**Current approach**:

- Quality validation checks chapter length, character name consistency
- No assessment of narrative effectiveness

**Proposed approach**:

- Analyze each chapter for intended emotional beats
- Flag when prose doesn't deliver intended impact
- Provide pacing heat map

**Implementation**:

```python
# In quality validation module
def analyze_narrative_tension(chapter_text: str, intended_beats: list[dict]) -> dict:
    """Analyze if prose delivers intended emotional beats."""

    analysis = call_llm(
        prompt=f"""
        This chapter intends to deliver these emotional beats:
        {json.dumps(intended_beats, indent=2)}

        Chapter text:
        {chapter_text}

        For each intended beat:
        1. Did the prose deliver it effectively? (1-5 rating)
        2. If not, why not? (too subtle, wrong tone, timing off, etc.)
        3. Specific line where beat occurs (or should occur)

        Also analyze:
        - Pacing rhythm (action vs. reflection ratio)
        - Tension curve (does it build or stay flat?)
        - Scene transitions (smooth or jarring?)
        """,
        tier="medium"
    )

    return {
        "beat_effectiveness": self._extract_beat_ratings(analysis),
        "pacing_issues": self._extract_pacing_issues(analysis),
        "recommendations": self._extract_recommendations(analysis)
    }

def generate_pacing_heatmap(story: Story) -> str:
    """Visual representation of story pacing."""

    chapters = []
    for chapter_key in story.manuscript_metadata.keys():
        chapter_text = self._load_chapter(story, chapter_key)

        # Analyze pacing
        action_ratio = self._calculate_action_ratio(chapter_text)
        dialogue_ratio = self._calculate_dialogue_ratio(chapter_text)
        tension_level = self._calculate_tension_level(chapter_text)

        chapters.append({
            "chapter": chapter_key,
            "action": action_ratio,
            "dialogue": dialogue_ratio,
            "tension": tension_level
        })

    # Generate visual heatmap
    heatmap = self._render_heatmap(chapters)
    return heatmap
```

**User experience**:

```
NARRATIVE TENSION ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Chapter 1: The Voice in the Lathe

Intended Beat: Horror (Josef's voice) → Line 49
  Effectiveness: ★★★★★ 5/5
  ✓ Delivered with visceral detail and emotional weight
  ✓ German dialogue adds authenticity

Intended Beat: Protagonist determination → Line 143
  Effectiveness: ★★★☆☆ 3/5
  ⚠ Undercut by calling his resolution "a lie" immediately after
  → Recommendation: Either commit to determination or show internal conflict more gradually

Pacing Heat Map:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ch 1: ████████░░ Action: High  | Tension: ▲ Rising
Ch 2: ████░░░░░░ Action: Med   | Tension: ─ Steady
Ch 3: ██████░░░░ Action: Med   | Tension: ▲ Rising
Ch 4: ███░░░░░░░ Action: Low   | Tension: ▼ Falling ⚠
Ch 5: ██░░░░░░░░ Action: Low   | Tension: ─ Steady  ⚠
Ch 6: ████████░░ Action: High  | Tension: ▲▲ Sharp rise
Ch 7: █████████░ Action: High  | Tension: ▲ Rising
Ch 8: ██████████ Action: V.High| Tension: ▲▲▲ Climax
Ch 9: █████░░░░░ Action: Med   | Tension: ▼ Resolution

Issues detected:
  ⚠ Chapters 4-5 show pacing slump (low action, flat tension)
  → Recommendation: Compress Ch 4-5 or add action beat in Ch 4

Overall tension curve: Strong setup, mid-story slump, strong climax
```

**Estimated effort**: 10-12 hours
**Impact**: Medium-High - helps identify structural issues beyond surface polish

---

## Priority 4: Research & Context Utilization

### 4.1 Research Relevance Filtering

**Current approach**:

- System generates research on: diesel mechanics, exorcism rituals, Weimar culture
- Unclear if AI actually references these during narrative generation
- May be generating unused documents

**Proposed approach**:

```
Concept generated → AI proposes research topics →
USER APPROVES subset → Generate only approved research →
Explicitly inject research into narrative generation prompts
```

**Implementation**:

```python
# In story_builder.py
def propose_research_topics(self, story_concept: dict) -> list[dict]:
    """Propose research topics based on concept."""

    proposal = call_llm(
        prompt=f"""
        Story concept: {story_concept}

        What research would improve this story's authenticity?
        Propose 5-8 specific research topics, each with:
        - Topic name
        - Why it matters for this story
        - What it will inform (setting, character actions, technical details, etc.)
        - Estimated importance (critical, helpful, nice-to-have)
        """,
        tier="medium"
    )

    topics = self._parse_research_proposal(proposal)
    return topics

def build_story_with_research_selection(self, user_prompt: str) -> Story:
    """Let user choose which research to generate."""

    concept = self._generate_concept(user_prompt)
    story = Story(title=concept['title'], ...)

    # Propose research
    topics = self.propose_research_topics(concept)

    print("\nPROPOSED RESEARCH TOPICS:")
    for i, topic in enumerate(topics):
        print(f"{i+1}. [{topic['importance']}] {topic['name']}")
        print(f"   Why: {topic['rationale']}")

    # User selection
    selected = input("\nSelect topics (e.g., '1,3,5' or 'all'): ")

    if selected.lower() == 'all':
        selected_topics = topics
    else:
        indices = [int(x.strip())-1 for x in selected.split(',')]
        selected_topics = [topics[i] for i in indices]

    # Generate only selected research
    for topic in selected_topics:
        research_doc = self._generate_research(topic)
        story.add_research_asset(topic['name'], research_doc)

    return story
```

**User experience**:

```
PROPOSED RESEARCH TOPICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. [CRITICAL] 1930s Diesel Engine Mechanics & Industrial Machinery
   Why: Lukas's exorcism rituals must be technically authentic
   Informs: Ritual descriptions, workshop details, possessed machine behavior

2. [CRITICAL] Catholic & Orthodox Exorcism Rituals
   Why: Core to Lukas's character and story mechanics
   Informs: Ritual structure, blessed objects, theological framework

3. [HELPFUL] Weimar Berlin Working-Class Daily Life & Culture
   Why: Setting authenticity, character behavior
   Informs: Dialogue, locations, social dynamics

4. [HELPFUL] German Language & Berlin Dialect
   Why: Authentic dialogue and character voice
   Informs: Character speech patterns, period slang

5. [NICE-TO-HAVE] 1930s Berlin Geography & Districts
   Why: Accurate location details
   Informs: Scene transitions, neighborhood descriptions

Select topics (1,3,5 or 'all'): 1,2,3

✓ Generating research for 3 topics...
  ✓ Diesel mechanics (2,400 words)
  ✓ Exorcism rituals (1,800 words)
  ✓ Weimar culture (2,100 words)

Proceed to asset generation? [y/n]:
```

**Estimated effort**: 6-8 hours
**Impact**: Medium - reduces unnecessary generation, clarifies research value

---

### 4.2 Explicit Research Injection in Narrative Prompts

**Current approach**:

- Research documents generated
- Stored in assets
- Unclear if narrative AI references them

**Proposed approach**:

- When generating each chapter, explicitly inject relevant research excerpts
- Ensure technical details come from research, not just AI knowledge

**Implementation**:

```python
# In story_builder.py
def _generate_chapter_with_research(self, story: Story, chapter_key: str) -> str:
    """Generate chapter with explicit research references."""

    chapter_meta = story.manuscript_metadata[chapter_key]

    # Identify relevant research
    relevant_research = self._identify_relevant_research(chapter_meta, story.research_assets)

    # Build enhanced prompt
    research_context = "\n\n".join([
        f"## Research: {topic}\n{content[:1000]}..."  # Include excerpt
        for topic, content in relevant_research.items()
    ])

    chapter_prompt = f"""
    {story.get_concept_summary()}

    RESEARCH CONTEXT (use for authenticity):
    {research_context}

    CHAPTER TO WRITE:
    {chapter_meta}

    Write this chapter using technical details from the research context.
    Ensure machinery descriptions, ritual mechanics, and period details are accurate.
    """

    return generate_narrative_text(prompt=chapter_prompt)

def _identify_relevant_research(self, chapter_meta: dict, research_assets: dict) -> dict:
    """Identify which research is relevant to this chapter."""

    # Use AI to match research to chapter needs
    analysis = call_llm(
        prompt=f"""
        Chapter description: {chapter_meta}

        Available research: {list(research_assets.keys())}

        Which research topics are most relevant to this chapter?
        Return list of topic names.
        """,
        tier="fast"
    )

    relevant_topics = self._parse_topic_list(analysis)
    return {topic: research_assets[topic] for topic in relevant_topics if topic in research_assets}
```

**User experience** (mostly transparent to user, but logged):

```
📖 Writing Chapter 1: The Voice in the Lathe

Injecting research context:
  ✓ Diesel Engine Mechanics (for lathe technical details)
  ✓ Exorcism Rituals (for blessed oil, spark plug ritual)

🤔 AI is processing...
✅ Chapter 1 saved (12,847 characters)
   - Used 8 technical terms from diesel mechanics research
   - Referenced 3 ritual elements from exorcism research
```

**Estimated effort**: 4-6 hours
**Impact**: Medium - ensures research actually informs narrative, improves authenticity

---

## Priority 5: Advanced Creative Tools

### 5.1 Character Discovery Mode

**Current approach**:

- Characters fully specified before any prose written
- Produces consistent characters but may miss emergent personality

**Proposed approach**:

- Generate basic character framework
- Run "interview" mode where character responds in voice
- User interacts, character personality emerges
- Lock in discovered voice for manuscript

**Implementation**:

```python
# In new character_discovery module
def discover_character_voice(character_name: str, character_basics: dict) -> dict:
    """Discover character voice through interaction."""

    print(f"\nCHARACTER DISCOVERY: {character_name}")
    print("━" * 60)
    print("Ask questions to discover this character's voice.")
    print("Type 'done' when satisfied.\n")

    conversation_history = []

    while True:
        question = input(f"You: ")
        if question.lower() == 'done':
            break

        # Character responds
        response = call_llm(
            prompt=f"""
            You are {character_name}:
            {json.dumps(character_basics, indent=2)}

            Conversation so far:
            {json.dumps(conversation_history, indent=2)}

            User asks: "{question}"

            Respond in character. Be authentic, revealing personality through:
            - Word choice and speech patterns
            - Attitude and emotional tone
            - What you choose to reveal or hide
            - How you relate to the question

            Stay consistent with previous responses.
            """,
            tier="medium",
            temperature=0.9  # Higher for personality variety
        )

        print(f"{character_name}: {response}\n")

        conversation_history.append({
            "question": question,
            "response": response
        })

    # Analyze discovered voice
    voice_profile = call_llm(
        prompt=f"""
        This character has had the following conversation:
        {json.dumps(conversation_history, indent=2)}

        Extract their voice characteristics:
        - Speech patterns (formal/casual, verbose/terse, etc.)
        - Personality traits revealed
        - Emotional range
        - Distinctive phrases or habits
        - Internal conflicts or contradictions

        Create a voice profile for narrative generation.
        """,
        tier="medium"
    )

    return {
        "conversation": conversation_history,
        "voice_profile": voice_profile,
        "character_name": character_name
    }
```

**User experience**:

```
CHARACTER DISCOVERY: Lukas Brenner
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Ask questions to discover this character's voice.
Type 'done' when satisfied.

You: What do you think when you look at a possessed machine?

Lukas: I think about tolerances. A bearing should have maybe
two-thousandths clearance. When it starts talking to me, that's
wrong. Not supernatural wrong—wrong like a bent shaft or a
cracked cylinder. Something's off spec, needs fixing.

You: Do you miss your brother?

Lukas: [pause] I miss having someone to drink coffee with at
three in the morning who understood why you'd stay up for a
lathe that needed you. Josef got that. Most people think machines
are just tools. We knew better.

You: Are you afraid of the demons?

Lukas: Afraid? No. Respectful, maybe. I'm afraid of bad welds
and stripped threads—things that fail under load when you need
them. Demons are just another thing that needs the right tool
and the right technique. Mostly I'm tired.

You: done

✓ Voice profile captured:
  - Speech: Terse, technical metaphors, deflects emotion
  - Patterns: Frames everything through mechanical lens
  - Reveals: Grief through mechanical details
  - Distinctive: "Wrong like..." comparisons

Use this voice for narrative? [y/n]:
```

**Estimated effort**: 12-15 hours
**Impact**: Medium - creates more authentic character voices, but time-intensive

---

### 5.2 Iterative Refinement Mode

**Current approach**:

- Generate prose once
- User manually edits if needed

**Proposed approach**:

- Generate rough draft
- AI self-critiques
- Generate revision
- User compares versions
- AI synthesizes best elements

**Implementation**:

```python
# In story_builder.py
def generate_chapter_with_refinement(self, story: Story, chapter_key: str, iterations: int = 2) -> str:
    """Generate chapter with iterative refinement."""

    chapter_meta = story.manuscript_metadata[chapter_key]
    versions = []

    # Generate initial draft
    print(f"📖 Generating initial draft for {chapter_key}...")
    draft_1 = generate_narrative_text(
        prompt=self._build_chapter_prompt(story, chapter_key),
        temperature=0.9  # Higher for variety
    )
    versions.append(("Initial draft", draft_1))

    for i in range(iterations):
        print(f"🔄 Refinement pass {i+1}/{iterations}...")

        # Self-critique
        critique = call_llm(
            prompt=f"""
            Critique this chapter draft:

            {versions[-1][1]}

            Analyze:
            1. What's working well? (specific strengths)
            2. What's not working? (specific weaknesses)
            3. How could prose be improved? (concrete suggestions)
            4. Are emotional beats landing?
            5. Is pacing appropriate?

            Be specific and actionable.
            """,
            tier="medium"
        )

        # Generate revision based on critique
        revision = generate_narrative_text(
            prompt=f"""
            Original chapter:
            {versions[-1][1]}

            Critique:
            {critique}

            Write a revised version addressing the critique.
            Keep what's working, improve what's not.
            """,
            temperature=0.8
        )

        versions.append((f"Revision {i+1}", revision))

    # Let user choose best version or synthesize
    print("\nGENERATED VERSIONS:")
    for i, (name, _) in enumerate(versions):
        print(f"{i+1}. {name}")

    choice = input("\nSelect version (or 's' to synthesize best elements): ")

    if choice.lower() == 's':
        # Synthesize best elements
        synthesis = generate_narrative_text(
            prompt=f"""
            Multiple versions of this chapter exist:

            {chr(10).join([f"VERSION {i+1}:\n{text}\n" for i, (_, text) in enumerate(versions)])}

            Create final version taking the best elements from each:
            - Strongest prose from any version
            - Most effective emotional beats
            - Best pacing and structure
            - Clearest characterization
            """,
            tier="big"
        )
        return synthesis
    else:
        return versions[int(choice)-1][1]
```

**User experience**:

```
📖 Generating Chapter 1: The Voice in the Lathe

Initial draft complete (12,450 chars)

🔄 Refinement pass 1/2...
Self-critique:
  ✓ Opening hook strong
  ✓ Technical details authentic
  ⚠ Josef revelation too abrupt (needs more build-up)
  ⚠ Workshop scene drags (trim 15%)

Revision 1 complete (11,200 chars)

🔄 Refinement pass 2/2...
Self-critique:
  ✓ Improved pacing in workshop
  ✓ Josef build-up more effective
  ⚠ Lost some atmospheric detail in trimming
  → Suggestion: Restore fog/smog imagery

Revision 2 complete (11,600 chars)

GENERATED VERSIONS:
1. Initial draft
2. Revision 1 (faster pacing)
3. Revision 2 (balanced)

Select version (or 's' to synthesize): s

Synthesizing best elements...
✅ Final version (11,450 chars)
   - Opening from initial draft (strongest hook)
   - Workshop pacing from Revision 1
   - Atmospheric details from Revision 2
   - Josef revelation from Revision 2
```

**Estimated effort**: 15-18 hours
**Impact**: High - significantly improves prose quality, but 2-3x generation time

---

## Implementation Roadmap

### Phase 1: Iterative Workflow (Weeks 1-2)

**Goal**: Transform from linear to iterative process

1. Concept review checkpoint (P1.1) - **6 hours**
2. First chapter test (P1.2) - **7 hours**
3. Mid-manuscript pivoting (P1.3) - **10 hours**

**Total**: ~23 hours
**Impact**: Enables creative discovery, prevents wasted generation

### Phase 2: Voice & Quality (Weeks 3-4)

**Goal**: Develop distinctive voice and catch issues early

4. Voice calibration (P2.1) - **12 hours**
5. AI beta reader (P3.1) - **15 hours**
6. Research relevance filtering (P4.1) - **8 hours**

**Total**: ~35 hours
**Impact**: More distinctive stories, better quality assurance

### Phase 3: Advanced Tools (Month 2+)

**Goal**: Enable power-user workflows

7. Comp title analysis (P2.2) - **10 hours**
8. Tension & impact analysis (P3.2) - **12 hours**
9. Character discovery mode (P5.1) - **15 hours**
10. Iterative refinement mode (P5.2) - **18 hours**

**Total**: ~55 hours
**Impact**: Professional-grade creative control

---

## Success Metrics

### Creative Quality Metrics

- **Voice distinctiveness**: Beta readers can identify "this is Mythos-generated" → want them to NOT identify it
- **Measure**: Blind test comparing Mythos output to human-written similar genre fiction

### User Satisfaction Metrics

- **Creative control**: Users feel like directors, not just consumers
- **Measure**: Survey "How much did you influence the final story?" (target: 8+/10)

### Iteration Metrics

- **Concept-to-satisfaction time**: Including review/revision cycles
- **Target**: <2 hours for full satisfaction (vs. <1 hour current but often unsatisfying)
- **Measure**: Track from initial concept to "I'm happy with this" declaration

### Voice Quality Metrics

- **Authorial voice capture**: How well does output match user's style examples?
- **Target**: 4+/5 similarity rating from users
- **Measure**: User ratings during voice calibration

---

## Risk Assessment

### High-Risk Items

- **Iterative refinement (P5.2)**: Very complex, 2-3x cost, uncertain quality gains
  - _Mitigation_: Start with single-pass refinement, measure improvement before multi-pass

- **Character discovery (P5.1)**: Time-intensive, may not scale to multiple characters
  - _Mitigation_: Limit to protagonist only initially, expand if valuable

### Medium-Risk Items

- **Voice calibration (P2.1)**: Requires users to provide good examples
  - _Mitigation_: Provide fallback to comp title analysis if user has no examples

- **Mid-manuscript pivoting (P1.3)**: Complex UX, could confuse users
  - _Mitigation_: Make pivoting optional, default to "continue as planned"

### Low-Risk Items

- **Concept review (P1.1)**: Simple checkpoint, clear value
- **First chapter test (P1.2)**: Natural workflow enhancement
- **Research filtering (P4.1)**: Pure efficiency gain, no downside

---

## Cost-Benefit Analysis

### Highest ROI (Implement First)

- **P1.1 Concept review**: 6 hours → prevents wasted 28-asset generation on wrong concept
- **P1.2 First chapter test**: 7 hours → catches voice issues before 9-chapter generation
- **P4.1 Research filtering**: 8 hours → reduces unnecessary generation, speeds workflow

### High ROI (Implement Second)

- **P1.3 Mid-manuscript pivoting**: 10 hours → enables creative discovery worth the complexity
- **P3.1 AI beta reader**: 15 hours → automated QA catches issues user might miss

### Medium ROI (Consider Later)

- **P2.1 Voice calibration**: 12 hours → creates distinctive voice but requires user examples
- **P3.2 Tension analysis**: 12 hours → nice-to-have insight, not critical

### Lower ROI (Advanced Users Only)

- **P5.1 Character discovery**: 15 hours → time-intensive for incremental improvement
- **P5.2 Iterative refinement**: 18 hours → 2-3x cost for quality gains of uncertain magnitude

---

## Comparison to Traditional Creative Workflows

### How Professional Writers Actually Work

**Discovery writers ("Pantsers")**:

1. Start with vague concept
2. Write to discover story
3. Characters surprise them
4. Heavy revision after draft
5. **Strength**: Organic, authentic discoveries

**Outline writers ("Plotters")**:

1. Detailed outline before drafting
2. Write to execute plan
3. Characters pre-defined
4. Light revision after draft
5. **Strength**: Coherent structure, fewer plot holes

**Mythos current approach**: Extreme plotter

- All planning upfront
- Zero discovery during writing
- **Result**: Coherent but potentially lifeless

**Mythos with improvements**: Adaptive plotter

- Planning upfront BUT
- Review checkpoints enable discovery
- Pivoting allows organic evolution
- **Result**: Structure + spontaneity

---

## The Vision: Mythos as Creative Co-Pilot

### Current Reality

```
User: "Write me a dieselpunk story"
Mythos: [generates 28 assets + 9 chapters]
Mythos: "Here you go!"
User: "Uh, this isn't quite what I wanted..."
Mythos: "Then regenerate from scratch"
```

### Improved Reality

```
User: "Write me a dieselpunk story about..."
Mythos: "Here's the concept I developed. Thoughts?"
User: "Love it, but make Margarethe the protagonist"
Mythos: "Updated. Here's Chapter 1 in the voice you requested"
User: "Perfect tone, but Josef needs more presence"
Mythos: "Adjusted chapters 2-9 to feature Josef more prominently"
User: "Chapter 5 drags. Any ideas?"
Mythos: "Beta reader flagged pacing issue. Suggest compressing factory tour. Want me to revise?"
User: "Yes, do it"
Mythos: "Revised. Here's the final manuscript."
User: "This is exactly what I envisioned!"
```

### Key Difference

- **Current**: User is passive recipient
- **Improved**: User is active director with responsive creative partner

---

## Next Steps

### Immediate (This Week)

1. Review this plan with stakeholders
2. Prioritize Phase 1 features for implementation
3. Design UX mockups for concept review and chapter test workflows

### Short-Term (Month 1)

1. Implement Phase 1: Iterative workflow (23 hours)
2. Test with 3-5 different story concepts
3. Gather user feedback on new workflow
4. Refine based on feedback

### Medium-Term (Month 2-3)

1. Implement Phase 2: Voice & quality (35 hours)
2. Beta test voice calibration with users who have style examples
3. Validate beta reader feedback against human beta reader feedback
4. Measure quality improvements

### Long-Term (Month 4+)

1. Evaluate demand for Phase 3 advanced features
2. Implement selectively based on user requests
3. Consider parallel with technical improvements from PROCESS_IMPROVEMENTS.md
4. Explore integration with external writing tools (Scrivener, etc.)

---

## Conclusion

The Mythos creative process is already producing high-quality fiction, but it's optimized for **speed over collaboration**. By adding iterative checkpoints, voice development tools, and quality feedback loops, we can transform it from an **automated ghostwriter** into a **creative co-pilot**.

**The key insight**: The best writing emerges from dialogue between planning and execution, between intention and discovery. Mythos currently does planning → execution with no dialogue in between. These improvements add that crucial conversation.

**Expected outcome**:

- Stories with more distinctive voices
- Higher user satisfaction (felt creative control)
- Better quality output (caught issues early)
- Slightly longer time-to-completion (~2 hours vs. 1 hour)
- But MUCH higher "time-to-satisfaction" (2 hours vs. days of manual editing)

**Recommended priority**:

1. **Phase 1 first** (iterative workflow) - this is the foundation
2. **Evaluate impact** - does iteration actually improve satisfaction?
3. **Phase 2 next** (voice & quality) - if Phase 1 proves valuable
4. **Phase 3 selectively** - only features users explicitly request

**Total estimated effort for Phases 1-2**: ~58 hours (~1.5 weeks focused development)

**Philosophy shift**: From "AI that writes for you" to "AI that writes _with_ you"
