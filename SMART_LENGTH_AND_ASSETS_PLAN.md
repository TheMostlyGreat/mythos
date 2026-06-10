# Smart Length and Asset Selection Implementation Plan

**Branch**: `feature/smart-length-and-assets`
**Goal**: Infer appropriate story length from concept complexity and generate only necessary planning assets
**Audience**: LLM implementing these changes

## Key Design Decisions

1. **LLM Tier**: Use `tier="medium"` for all inference operations (length, chapters, assets) - consistent with other planning tasks like concept/character generation
2. **Chapter Cap**: NO maximum chapter limit - epics can have 40+ chapters if structure requires it
3. **Length Detection**: Always run inference, let LLM use any existing length specifications in concept as guidance (Option B)
4. **Concept Data**: Read from `story.assets.get(AssetTypeNames.CONCEPT.value).details` after concept generation (using proper enum access)
5. **Chapter Count Passing**: Store in `story.metadata['target_chapters']`, inject into CHAPTER_LIST prompt via modified `_assemble_planning_prompt()`
6. **Story Model**: Pydantic BaseModel (not dataclass), add `metadata: Dict[str, Any] = Field(default_factory=dict)`
7. **Asset Generation Order**: Matches existing `_generate_related_assets()` order to maintain deep dive triggers
8. **User Overrides**: Three optional parameters: `force_length`, `force_chapters`, `force_assets`
9. **Asset Key Naming**: Standardized to `'settings'` (not 'deep_settings') and `'chapter_list'` (not 'chapter_plans') - matches actual AssetTypeNames
10. **Resume Behavior**: When resuming via `smart_resume_story()`, always use stored `metadata['asset_plan']` if present (preserves generation intent, efficient, predictable). Only run fresh inference for legacy stories missing asset_plan.
11. **Chapter Count Hint Flexibility**: Target chapter count is guidance, not constraint. Trust LLM to adjust based on full context. Log deviations for debugging but don't warn users.
12. **Override Trust**: User overrides (`force_length`, `force_chapters`, `force_assets`) are absolute - no validation or warnings. Principle: explicit parameters = explicit intent. Skips all inference for overridden values (efficient, no friction).
13. **Skipped Asset Regeneration**: If users need a skipped asset later, they can manually create markdown file in appropriate directory (FileChangeTracker detects it). Formal `regenerate_asset()` API not needed for v1 (edge case, avoid bloat).
14. **AssetTypes vs AssetTypeNames**: These are DIFFERENT types used for different purposes:
    - `AssetTypeNames` = Enum (e.g., `AssetTypeNames.CONCEPT`)
      - Use `.name` to get enum name string: `AssetTypeNames.CONCEPT.name` → `"CONCEPT"`
      - Use `.value` to get asset key string: `AssetTypeNames.CONCEPT.value` → `"concept"` (for dict access)
    - `AssetTypes` = Class with dynamically generated attributes (e.g., `AssetTypes.CONCEPT`)
      - Each attribute is an `AssetType` dataclass with: `title`, `directory`, `template_path`, `summary_length`
      - Access these for metadata: `AssetTypes.CONCEPT.template_path`, `AssetTypes.RESEARCH.directory`
    - **Conversion**: `getattr(AssetTypes, asset_type_enum.name)` converts AssetTypeNames enum → AssetType dataclass
    - **Usage patterns**:
      - Dictionary access: `story.assets.get(AssetTypeNames.CONCEPT.value)` (uses string key "concept")
      - Metadata access: `AssetTypes.CONCEPT.template_path` (uses dataclass attribute)
      - Type comparison: `asset_type == AssetTypes.CHAPTER_LIST` (comparing AssetType instances)

---

## Changes Required

### 1. Update Concept Template (templates/concept_template.md)

**Current**:

```markdown
- Length: The length of the story in pages. Unless otherwise specified,
  the story should be between 20 and 50 pages.
```

**New**:

```markdown
- Length: Based on concept complexity and user preferences, recommend story length:
  - Novella: 40-80 pages (~12,000-25,000 words) - single protagonist arc, focused plot, 3-5 chapters
  - Novel: 200-400 pages (~60,000-120,000 words) - multiple character arcs, complex plot, 8-15 chapters
  - Epic: 400+ pages (120,000+ words) - expansive world, many subplots, 15+ chapters
```

**Implementation**: Edit line 18 in `templates/concept_template.md`

---

### 2. Create Length Inference Function (mythos/utils/story_analysis.py - NEW FILE)

```python
"""Story analysis utilities for inferring length, complexity, and asset needs."""

from mythos.utils.llm_utils import call_llm
from mythos.utils.logger import get_logger
from typing import Dict, List, Tuple
import json

logger = get_logger(__name__)

def infer_story_length(concept_text: str) -> Tuple[str, int, str]:
    """
    Infer appropriate story length from concept complexity.

    Returns:
        Tuple of (length_category, target_pages, reasoning)
        - length_category: "novella" | "novel" | "epic"
        - target_pages: int (40-80 for novella, 200-400 for novel, 400+ for epic)
        - reasoning: str explaining the decision
    """

    analysis = call_llm(
        prompt=f"""Analyze this story concept and recommend appropriate length:

{concept_text}

Complexity factors to consider:
- Number of character arcs (1 = novella, 2-4 = novel, 5+ = epic)
- Plot complexity (single thread = novella, multiple converging = novel, sprawling = epic)
- World-building depth (minimal = novella, detailed = novel, extensive = epic)
- Subplot count (0-1 = novella, 2-4 = novel, 5+ = epic)
- Thematic depth (focused = novella, layered = novel, philosophical = epic)

If the concept already specifies a length, use that as guidance. Otherwise, infer from complexity.

Recommend:
1. Length category: novella/novel/epic
2. Target page count (specific number within category range)
3. Brief reasoning (2-3 sentences)

Return as JSON:
{{
  "category": "novel",
  "pages": 280,
  "reasoning": "Multiple character arcs, complex world-building, several subplots, and thematic depth justify novel length."
}}""",
        tier="medium",
        json_output=True,
        json_schema={
            "type": "object",
            "properties": {
                "category": {"type": "string", "enum": ["novella", "novel", "epic"]},
                "pages": {"type": "integer", "minimum": 40},
                "reasoning": {"type": "string"}
            },
            "required": ["category", "pages", "reasoning"],
            "additionalProperties": False
        }
    )

    # Parse response with error handling
    try:
        if isinstance(analysis, str):
            analysis = json.loads(analysis)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Failed to parse length inference JSON: {e}")
        analysis = {}

    # Validate and use defaults on failure
    category = analysis.get('category', 'novel')
    pages = analysis.get('pages', 250)
    reasoning = analysis.get('reasoning', 'Failed to infer length, using novel default')

    # Clamp to valid ranges
    if category == 'novella' and not (40 <= pages <= 80):
        logger.warning(f"Novella pages {pages} out of range, clamping to 40-80")
        pages = max(40, min(80, pages))
    elif category == 'novel' and not (200 <= pages <= 400):
        logger.warning(f"Novel pages {pages} out of range, clamping to 200-400")
        pages = max(200, min(400, pages))
    elif category == 'epic' and pages < 400:
        logger.warning(f"Epic pages {pages} too low, setting to 400")
        pages = 400

    return (category, pages, reasoning)

def determine_chapter_count(concept_text: str, target_pages: int) -> Tuple[int, str]:
    """
    Determine optimal chapter count based on story structure needs, not page math.

    Returns:
        Tuple of (chapter_count, reasoning)
    """

    analysis = call_llm(
        prompt=f"""Determine optimal chapter count for this story:

{concept_text}

Target length: {target_pages} pages

Consider STRUCTURE needs, not page math:
- Story acts/beats (3-act = ~8-12 chapters, 5-act = ~15-20 chapters)
- POV characters (single = fewer chapters, multiple = more chapters)
- Plot complexity (linear = fewer, episodic = more)
- Pacing needs (intense = shorter chapters/more breaks, contemplative = longer chapters/fewer)

Recommend:
1. Chapter count (specific number, no artificial cap)
2. Reasoning based on structure (not "X pages ÷ Y per chapter")

Return as JSON:
{{
  "chapters": 12,
  "reasoning": "Three-act structure with multiple POV characters benefits from 12 chapters, allowing 4 chapters per act for proper narrative development."
}}""",
        tier="medium",
        json_output=True,
        json_schema={
            "type": "object",
            "properties": {
                "chapters": {"type": "integer", "minimum": 3},
                "reasoning": {"type": "string"}
            },
            "required": ["chapters", "reasoning"],
            "additionalProperties": False
        }
    )

    # Parse response with error handling
    try:
        if isinstance(analysis, str):
            analysis = json.loads(analysis)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Failed to parse chapter count JSON: {e}")
        analysis = {}

    # Validate with defaults
    chapters = analysis.get('chapters', 9)
    reasoning = analysis.get('reasoning', 'Failed to determine chapter count, using 9')

    # Clamp to minimum only
    if chapters < 3:
        logger.warning(f"Chapter count {chapters} below minimum, setting to 3")
        chapters = 3

    return (chapters, reasoning)

def select_needed_assets(concept_text: str) -> Dict[str, bool]:
    """
    Determine which planning assets are needed based on concept analysis.

    Args:
        concept_text (str): The story concept markdown text.

    Always generated:
    - concept (already exists)
    - characters
    - plot
    - chapter_list

    Conditionally generated based on 7+/10 necessity score:
    - research (specialized knowledge needed?)
    - settings (complex world-building?)
    - themes (literary depth vs pure entertainment?)
    - timeline (complex chronology?)
    - writing_style (unusual voice/style needs?)

    Returns:
        Dict mapping asset type to boolean (generate or skip)
    """

    analysis = call_llm(
        prompt=f"""Analyze which planning assets this story needs:

{concept_text}

ALWAYS NEEDED (already decided):
✓ concept
✓ characters
✓ plot
✓ chapter_list

EVALUATE NECESSITY (score 0-10, generate if 7+):

1. research: Specialized knowledge required?
   - Historical periods, technical domains, cultural practices
   - Score 7+ if story requires fact-checking or authenticity research

2. settings: Complex world-building?
   - Alternate history, invented worlds, detailed locations, technology systems
   - Score 7+ if setting is more than backdrop

3. themes: Literary/philosophical depth?
   - Thematic analysis, symbol systems, critical perspectives
   - Score 7+ if story has artistic ambitions beyond entertainment

4. timeline: Complex chronology?
   - Multi-timeline, extensive flashbacks, long timespan, non-linear
   - Score 7+ if temporal structure needs dedicated planning (simple linear = skip, plot.md covers it)

5. writing_style: Unusual voice/style?
   - Period-specific language, distinct narrative voice, experimental form
   - Score 7+ if style is challenging or highly specific

Return necessity scores and decisions as JSON:
{{
  "research": {{"score": 8, "reasoning": "Historical period requires factual accuracy", "generate": true}},
  "settings": {{"score": 7, "reasoning": "Complex world-building central to plot", "generate": true}},
  "themes": {{"score": 6, "reasoning": "Entertainment-focused, skip heavy thematic analysis", "generate": false}},
  "timeline": {{"score": 3, "reasoning": "Linear chronology, plot.md sufficient", "generate": false}},
  "writing_style": {{"score": 7, "reasoning": "Distinct narrative voice requires guidance", "generate": true}}
}}""",
        tier="medium",
        json_output=True,
        json_schema={
            "type": "object",
            "properties": {
                "research": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 0, "maximum": 10},
                        "reasoning": {"type": "string"},
                        "generate": {"type": "boolean"}
                    },
                    "required": ["score", "reasoning", "generate"]
                },
                "settings": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 0, "maximum": 10},
                        "reasoning": {"type": "string"},
                        "generate": {"type": "boolean"}
                    },
                    "required": ["score", "reasoning", "generate"]
                },
                "themes": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 0, "maximum": 10},
                        "reasoning": {"type": "string"},
                        "generate": {"type": "boolean"}
                    },
                    "required": ["score", "reasoning", "generate"]
                },
                "timeline": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 0, "maximum": 10},
                        "reasoning": {"type": "string"},
                        "generate": {"type": "boolean"}
                    },
                    "required": ["score", "reasoning", "generate"]
                },
                "writing_style": {
                    "type": "object",
                    "properties": {
                        "score": {"type": "integer", "minimum": 0, "maximum": 10},
                        "reasoning": {"type": "string"},
                        "generate": {"type": "boolean"}
                    },
                    "required": ["score", "reasoning", "generate"]
                }
            },
            "required": ["research", "settings", "themes", "timeline", "writing_style"],
            "additionalProperties": False
        }
    )

    # Parse response with error handling
    try:
        if isinstance(analysis, str):
            analysis = json.loads(analysis)
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"Failed to parse asset selection JSON: {e}")
        analysis = {}

    # Build asset decisions with safe defaults
    asset_decisions = {
        'concept': True,
        'characters': True,
        'plot': True,
        'chapter_list': True,
        'research': analysis.get('research', {}).get('generate', True),
        'settings': analysis.get('settings', {}).get('generate', True),
        'themes': analysis.get('themes', {}).get('generate', True),
        'timeline': analysis.get('timeline', {}).get('generate', False),
        'writing_style': analysis.get('writing_style', {}).get('generate', True)
    }

    # Log decisions for transparency
    print("\n📊 Asset Generation Plan:")
    for asset, decision in asset_decisions.items():
        status = "✓ Generate" if decision else "✗ Skip"
        if asset in analysis:
            reasoning = analysis[asset]['reasoning']
            print(f"  {status} {asset}: {reasoning}")
        else:
            print(f"  {status} {asset} (always generated)")

    return asset_decisions
```

**Implementation**: Create new file `mythos/utils/story_analysis.py`

---

### 3. Update StoryBuilder to Use Inference (mythos/services/story_builder.py)

**Add import at top of file** (around line 4-6, after existing config imports):

```python
from mythos.utils.story_analysis import infer_story_length, determine_chapter_count, select_needed_assets
# Note: List is already imported at line 19
# Note: AssetTypeNames is already imported at line 5 from config.settings
```

**Modify `build_story()` method** (around line 106):

**Current signature**:

```python
def build_story(self, user_prompt: str, iterations: int = 1, stop_after_assets: bool = False, non_interactive: bool = False) -> Story:
    # Generate concept
    concept = self._generate_concept(user_prompt)

    # Generate all assets
    self._build_assets(story)

    # Generate all chapters
    self._generate_chapter_list(story)
```

**New signature with Optional type hints**:

```python
def build_story(
    self,
    user_prompt: str,
    iterations: int = 1,
    stop_after_assets: bool = False,
    non_interactive: bool = False,
    force_length: Optional[int] = None,
    force_chapters: Optional[int] = None,
    force_assets: Optional[List[str]] = None
) -> Story:
    """
    Constructs a complete story from a user prompt using iterative refinement.

    Args:
        user_prompt (str): The initial prompt provided by the user.
        iterations (int): Number of iterations to refine the story.
        stop_after_assets (bool): If True, stops after generating story assets without creating chapters.
        non_interactive (bool): If True, skips user confirmations and runs full pipeline automatically.
        force_length (Optional[int]): Override inferred length with specific page count. Skips length inference.
        force_chapters (Optional[int]): Override inferred chapter count. Skips chapter count inference.
        force_assets (Optional[List[str]]): Specify which optional assets to generate. Core assets always generated.

    Returns:
        Story: The story object (complete or with assets only, depending on stop_after_assets).

    Raises:
        StoryBuildException: If the story building process fails.
    """
    # ... existing code to create story and generate concept asset ...
    # (Lines 125-135 of existing build_story)

    # *** INSERT THE FOLLOWING IMMEDIATELY AFTER LINE 135 ***
    # *** (after self._create_asset_with_metadata(story, concept_asset)) ***
    # *** BEFORE LINE 137 (the confirmation dialog) ***

    # Get concept text once for all inference operations (efficiency)
    # Note: AssetTypeNames already imported at top of file from config.settings
    concept_text = story.assets.get(AssetTypeNames.CONCEPT.value).details

    # STEP 1: Infer story length if not forced by user
    if force_length:
        print(f"\n📏 Using user-specified length: {force_length} pages")
        target_pages = force_length
        # Infer category from page count
        if target_pages < 80:
            length_category = "novella"
        elif target_pages < 400:
            length_category = "novel"
        else:
            length_category = "epic"
        reasoning = f"User specified {force_length} pages"
    else:
        print("\n📏 Inferring story length from concept complexity...")
        length_category, target_pages, reasoning = infer_story_length(concept_text)
        print(f"   Recommended: {length_category.upper()} ({target_pages} pages)")
        print(f"   Reasoning: {reasoning}")

    # Store in story metadata
    story.metadata['target_length'] = target_pages
    story.metadata['length_category'] = length_category

    # STEP 2: Determine chapter count from structure or use override
    if force_chapters:
        print(f"\n📖 Using user-specified chapter count: {force_chapters}")
        chapter_count = force_chapters
        chapter_reasoning = f"User specified {force_chapters} chapters"
    else:
        print("\n📖 Determining chapter structure...")
        chapter_count, chapter_reasoning = determine_chapter_count(
            concept_text,
            story.metadata.get('target_length', 40)
        )
    print(f"   Chapters: {chapter_count}")
    print(f"   Structure reasoning: {chapter_reasoning}")
    story.metadata['target_chapters'] = chapter_count

    # STEP 3: Select needed assets or use override
    if force_assets:
        print(f"\n📚 Using user-specified assets: {', '.join(force_assets)}")
        asset_plan = {
            'concept': True,
            'characters': True,
            'plot': True,
            'chapter_list': True,
            'research': 'research' in force_assets,
            'settings': 'settings' in force_assets,
            'themes': 'themes' in force_assets,
            'timeline': 'timeline' in force_assets,
            'writing_style': 'writing_style' in force_assets or 'style' in force_assets
        }
        story.metadata['asset_plan'] = asset_plan
    else:
        print("\n📚 Analyzing which planning assets are needed...")
        asset_plan = select_needed_assets(concept_text)
        story.metadata['asset_plan'] = asset_plan

    # STEP 4: Generate only selected assets
    # *** REPLACE line 147 call to self._generate_related_assets(story) with: ***
    self._build_selected_assets(story, asset_plan)

    # Rest of build_story continues as normal with existing flow...
    # (Lines 149-202 of existing build_story - chapter outlines, manuscript, EPUB)
```

**Add new method** `_build_selected_assets()`:

```python
def _build_selected_assets(self, story: Story, asset_plan: Dict[str, bool]) -> None:
    """Generate only the assets marked as needed in asset_plan."""

    print("\n🏗️  Generating selected planning assets...")

    # Note: AssetTypeNames already imported at top of file from config.settings
    # Map of asset types to generate (using existing _create_single_asset pattern)

    asset_type_mapping = {
        'characters': AssetTypeNames.CHARACTERS,
        'plot': AssetTypeNames.PLOT,
        'research': AssetTypeNames.RESEARCH,
        'settings': AssetTypeNames.SETTINGS,  # Settings handles both baseline and deep
        'themes': AssetTypeNames.THEMES,
        'timeline': AssetTypeNames.TIMELINE,
        'writing_style': AssetTypeNames.WRITING_STYLE,
        'chapter_list': AssetTypeNames.CHAPTER_LIST
    }

    # Always generate core assets (in order: research, settings, plot, themes, characters, timeline, chapter_list, style)
    # This matches the existing _generate_related_assets() order
    core_assets = ['research', 'settings', 'plot', 'themes', 'characters', 'timeline', 'chapter_list', 'writing_style']

    for asset_key in core_assets:
        # Check if this asset should be generated
        should_generate = asset_plan.get(asset_key, False)

        # Override: always generate characters, plot, chapter_list
        if asset_key in ['characters', 'plot', 'chapter_list']:
            should_generate = True

        if should_generate:
            asset_type = asset_type_mapping[asset_key]
            print(f"  ✓ Generating {asset_key}...")
            asset = self._create_single_asset(story, asset_type)
            self._create_asset_with_metadata(story, asset)
            self.story_manager.update_story(story)

            # Trigger deep dives if applicable (matching existing pattern)
            if asset_key == 'research':
                try:
                    self.generate_deep_dive_research(story)
                    self.generate_critical_perspectives(story)
                except Exception as e:
                    self.logger.warning(f"Deep dive research failed: {e}")

            if asset_key == 'settings':
                try:
                    self.generate_deep_dive_settings(story)
                except Exception as e:
                    self.logger.warning(f"Deep dive settings failed: {e}")

    # Log what was skipped
    skipped = [k for k, v in asset_plan.items() if not v and k not in ['concept', 'characters', 'plot', 'chapter_list']]
    if skipped:
        print(f"\n  ✗ Skipped (not needed): {', '.join(skipped)}")
```

**Modify `_assemble_planning_prompt()` to include chapter count hint**:

```python
def _assemble_planning_prompt(self, story: Story, asset_type: AssetTypes, current_asset: Optional[StoryAsset] = None) -> str:
    """
    Assembles a prompt for the writer service to generate a planning asset.
    """
    self.logger.debug(f"Assembling prompt for asset type: '{asset_type.title}'")

    template_text = Path(asset_type.template_path).read_text()
    current_asset_section = f"## Current version of the asset:\n{current_asset.details}\n" if current_asset else ""

    # Special handling for CHAPTER_LIST: include target chapter count if available
    chapter_hint = ""
    if asset_type == AssetTypes.CHAPTER_LIST and 'target_chapters' in story.metadata:
        target_count = story.metadata['target_chapters']
        chapter_hint = f"## Target Chapter Count:\nAim for approximately {target_count} chapters based on story structure analysis.\n\n"
        self.logger.debug(f"Suggesting {target_count} chapters (LLM can adjust based on full context)")

    prompt = (
        f"## User Prompt:\n{story.user_prompt}\n"
        f"## Story Synopsis:\n{self.story_manager.get_synopsis(story)}\n"
        f"{chapter_hint}"
        f"## Template for '{asset_type.title}':\n{template_text}\n"
        f"{current_asset_section}"
        f"## Prompt:\nPlease create or refine a '{asset_type.title}' for this story using the template.\n"
        "Focus on clarity, brevity, and specificity.\n"
    )

    self.logger.debug("Planning prompt assembled.")
    return prompt
```

**Note on chapter generation flow**:

- Chapter count is determined before asset generation
- Stored in `story.metadata['target_chapters']`
- When generating CHAPTER_LIST asset, `_assemble_planning_prompt()` checks metadata and includes the target count as a hint
- LLM uses this hint but can adjust based on full context (it's guidance, not constraint)
- System trusts LLM expertise - no validation or user warnings if actual count differs from suggestion
- Debug logging shows deviations for development visibility only
- After CHAPTER_LIST is generated, existing `generate_chapter_assets()` creates individual chapter outline files
- No changes needed to downstream chapter outline/manuscript generation

**Implementation**: Modify `mythos/services/story_builder.py` as specified above

---

### 4. Update Story Model (mythos/story/story.py)

**Add metadata field** (Story is a Pydantic BaseModel, not a dataclass):

```python
from typing import Dict, Any

class Story(BaseModel):
    # ... existing fields ...

    metadata: Dict[str, Any] = Field(default_factory=dict)
    # New metadata keys:
    # - 'target_length': int (pages)
    # - 'length_category': str ("novella" | "novel" | "epic")
    # - 'target_chapters': int
    # - 'asset_plan': Dict[str, bool]
```

**Implementation**: Add metadata field to Story model in `mythos/story/story.py`

---

### 5. Update User-Facing Messages (mythos/services/story_builder.py)

**Insert after all 3 inference steps complete, before the existing confirmation dialog**:

```python
# *** INSERT IMMEDIATELY AFTER: story.metadata['asset_plan'] = asset_plan ***
# *** (This is the last line of STEP 3 shown in Section 3 above) ***
# *** BEFORE: Original line 137 confirmation dialog in story_builder.py ***

# Display story plan summary
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 STORY PLAN

Length: {length_category.upper()} (~{target_pages} pages)
Chapters: {chapter_count}
Assets: {sum(asset_plan.values())}/{len(asset_plan)} will be generated

{reasoning}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
```

**During generation**:

```python
# Show progress, no cost warnings (per decision: Option B)
# Progress indicators already exist, just ensure they show for long generations
```

**Implementation**: Update print statements in `story_builder.py::build_story()`

---

### 6. Backward Compatibility (Per Decision: Option A)

**No changes to existing stories**: Leave stories generated with 40-page assumption unchanged.

**Implementation**: No action required - new logic only affects new story generation

---

## Testing Plan

### Test Case 1: Simple Concept (Should infer Novella)

```python
concept = "Two rival food truck owners fall in love during a city food festival"

# Expected:
# - Length: Novella (40-50 pages)
# - Chapters: 5-6
# - Assets: Skip research, settings, timeline, themes (just characters + plot + chapter_list + writing_style)
```

### Test Case 2: Complex Concept (Should infer Novel)

```python
concept = "A dieselpunk occult adventure about a mechanic-exorcist who uses blessed engine oil and holy spark plugs to banish demons possessing industrial machinery in a soot-choked 1930s alternate Berlin"

# Expected:
# - Length: Novel (250-300 pages)
# - Chapters: 9-12
# - Assets: Generate research + settings + themes + writing_style (skip timeline for linear story)
```

### Test Case 3: Epic Concept (Should infer Epic)

```python
concept = "A thousand-year space opera following five generations of a family across three galaxies as they navigate the collapse of the Terran Empire, the rise of the AI Conclave, and first contact with extra-dimensional beings"

# Expected:
# - Length: Epic (500+ pages)
# - Chapters: 20-30+
# - Assets: Generate all (research + settings + themes + timeline + writing_style)
```

**Implementation**: Create test file `tests/test_story_inference.py` with these cases

---

## Files to Modify/Create

**Modify**:

1. `templates/concept_template.md` (line 18 - update length guidance)
2. `mythos/services/story_builder.py` (add inference logic, new `_build_selected_assets()` method, modify `build_story()`, modify `_assemble_planning_prompt()`)
3. `mythos/story/story.py` (add `metadata` field to Pydantic model)

**Create**:

1. `mythos/utils/story_analysis.py` (new utility module with 3 functions)
2. `tests/test_story_inference.py` (test cases)

**Total changes**: 5 files (2 new, 3 modified)

**Specific modifications to `story_builder.py`**:

- Add 3 new parameters to `build_story()`: `force_length`, `force_chapters`, `force_assets`
- Insert inference logic at line 135 of existing build_story() (after concept generation, before confirmation dialog)
- Retrieve concept_text once at start of inference block for efficiency (reuse in all 3 steps)
- Create new method `_build_selected_assets()` replacing `_generate_related_assets()` call
- Modify `_assemble_planning_prompt()` to include chapter count hint for CHAPTER_LIST

---

## Implementation Order

1. ✅ Create branch (done)
2. Create `mythos/utils/story_analysis.py` with all three functions (includes error handling)
3. Update `templates/concept_template.md`
4. Update `mythos/story/story.py` (add metadata field)
5. Update `mythos/services/story_builder.py` (integrate inference with concept_text optimization)
6. Create `tests/test_story_inference.py`
7. Test with simple/complex/epic concepts
8. Commit and push to branch

**Note**: `smart_resume_story()` automatically handles stored asset plans per Design Decision #10 - no code changes needed (it already checks `metadata` dict).

---

## Success Criteria

- [ ] Concept template updated with length guidance (no hardcoded 20-50 default)
- [ ] `infer_story_length()` correctly categorizes simple → novella, complex → novel, epic → epic
- [ ] `determine_chapter_count()` uses story structure, not page math, with NO artificial cap
- [ ] Inference operations use `tier="medium"` (consistent with other planning tasks)
- [ ] `select_needed_assets()` skips unnecessary assets (timeline for linear stories, research for contemporary fiction)
- [ ] StoryBuilder shows inference reasoning to user (transparent decisions)
- [ ] User overrides skip inference entirely (no validation, no warnings, efficient)
- [ ] Chapter count hint is guidance only - LLM can adjust, no user warnings on deviation
- [ ] Error handling wraps all json.loads() calls with graceful defaults
- [ ] Story metadata stores: `target_length`, `length_category`, `target_chapters`, `asset_plan`
- [ ] Resumed stories use stored asset_plan (efficient, predictable)
- [ ] Test cases pass (novella, novel, epic inference works correctly)
- [ ] Existing stories unaffected (backward compatible)
- [ ] No bloat (clean, focused implementation)
- [ ] User overrides work (`force_length`, `force_chapters`, `force_assets`)
