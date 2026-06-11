@./.safeword/SAFEWORD.md

---

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mythos is an AI-powered story builder that transforms user concepts into complete narratives with rich world-building, character development, and narrative structure. It uses a multi-tier LLM system with OpenAI and Anthropic models.

> ## ⚠️ Project status: greenfield TypeScript rebuild
>
> Mythos is being **rebuilt from scratch in TypeScript** (end-to-end: server, client, shared types). The product vision driving that build is `JTBD.md`; the single persona is in `.safeword-project/personas.md`.
>
> **The Python code under `mythos/` and everything documented below is the reference-only prototype** — kept to mine for working behavior, prompts, and pipeline logic, not to extend. Build new work in TypeScript against `JTBD.md`; treat the Python stack notes below as historical reference.

## Essential Commands

### Development

```bash
# Run the application
python -m mythos

# Run tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/services/test_story_builder.py -v

# Run with verbose output
python -m pytest tests/ -vv
```

### Environment Setup

```bash
# Activate virtual environment (required)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set required API keys (no .env files - shell only)
export OPENAI_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
```

## Architecture Overview

### Core Philosophy

- **Simple over complex**: Prefer functions over class hierarchies
- **Single patterns**: One approach, used consistently
- **Explicit error handling**: Never silently ignore errors
- **User-focused UX**: Show major phases only, hide technical details

### Multi-Tier LLM System (October 2025)

Located in `mythos/config/settings.py`, uses **latest available models** (October 2025):

- **FAST**: `gpt-5-mini` (OpenAI) - GPT-5 Mini, ultra-fast & cost-effective
- **MEDIUM**: `claude-sonnet-4` (Anthropic) - Claude Sonnet 4, best balance (72.7% SWE-bench)
- **BIG**: `gpt-5` (OpenAI) - GPT-5 with 400K context, reasoning_effort & verbosity controls

**Additional Available Models**:

- `claude-opus-4` - Most powerful Anthropic model for complex reasoning
- `gpt-4o-2024-08-06` - Stable GPT-4o backup
- `claude-3-5-sonnet-20241022` - Stable Claude 3.5 backup

All LLM calls go through `mythos/utils/llm_utils.py::call_llm()` which implements:

- **Prompt caching** (Anthropic) - Up to 90% cost savings on system prompts/tools
- **Extended thinking** (Claude 4) - Native API support with configurable budgets (1K-128K tokens)
- **Interleaved thinking** (Claude 4) - Thinking between tool calls
- **GPT-5 parameters** - reasoning_effort (minimal/low/medium/high), verbosity (low/medium/high)
- **Structured outputs** (OpenAI) - `parallel_tool_calls: false` for compatibility
- **Error handling** - `ProviderError` (retry) vs `ContentRefusalError` (no retry)
- **Token tracking** via global `TokenCounter`
- **User feedback** via `print_thinking()` indicators

### Data Models & Storage

**Story Structure** (`mythos/story/story.py`):

- `Story`: Main story dataclass (Pydantic model)
  - `assets`: Dict of story assets (legacy, for backward compat)
  - `asset_metadata`: New metadata-only storage (content in .md files)
  - `manuscript`: Dict of chapter content (legacy)
  - `manuscript_metadata`: New metadata for chapters
  - `story_dir`: Path to story files (default: `stories/{uuid}`)

**Asset System** (`mythos/story_asset/`):

- `StoryAsset`: Individual story components (characters, plot, themes, etc.)
- `AssetMetadata`: Lightweight metadata refs (content stored in markdown files)
- `StoryAssetManager`: Creates/updates assets as markdown in story directories

**Story Management** (`mythos/story/story_manager.py`):

- Handles persistence, versioning, and state tracking
- Manages file-based storage in `stories/` directory
- Tracks external changes via `FileChangeTracker`
- Methods:
  - `load_story(title)`: Load existing story from disk
  - `save_story(story)`: Persist story to .story file
  - `get_story_state(story)`: Returns current completion state
  - `get_story_progress_summary(story)`: Human-readable progress

### Story Building Pipeline

**StoryBuilder** (`mythos/services/story_builder.py`):
The main orchestrator that transforms concepts into complete stories.

Key workflow:

1. **Concept refinement** → `StoryQuestioner.conduct_interview()`
2. **Asset generation** → Creates characters, settings, plot, themes, etc.
3. **Chapter planning** → Generates chapter list with summaries
4. **Manuscript writing** → Writes full chapter content
5. **EPUB export** → Creates distributable ebook

Smart resume capability via `smart_resume_story()`:

- Detects incomplete assets/chapters
- Resumes from exact point of interruption
- Uses `StoryManager.get_story_state()` for state detection

**Writer Services** (`mythos/services/writer.py`):
Specialized generation functions:

- `generate_story_concept()`: Expands user prompt into full concept
- `generate_planning_text()`: Creates story assets (plot, themes, etc.)
- `generate_character_list()`: Returns structured character data
- `generate_chapter_list()`: Creates chapter outline
- `generate_narrative_text()`: Writes chapter content

### User Experience Layer

**Progress Tracking** (`mythos/utils/progress_tracker.py`):

- `ProgressTracker`: Shows structured multi-step operations
- Global singleton pattern via `get_progress_tracker()`
- Methods:
  - `start_session(phase)`: Begin tracking phase
  - `start_step(name)`: Start individual step
  - `complete_step(name)`: Mark step complete with timing
  - `show_chapter_progress()`: Visual progress bar for chapters

**UI Utilities** (`mythos/utils/ui_utils.py`):

- `print_thinking(msg)`: Shows immediate feedback during 10-30s LLM delays
- `print_progress_step()`: Display step start
- `complete_progress_step()`: Display step completion
- `confirm_next_step()`: Interactive confirmation between major phases

**Main CLI** (`__main__.py`):
Entry point with interactive workflow:

- Welcome screen and concept input
- Story creation vs resume existing
- Progress display and confirmations
- Error handling and recovery

### Template System

Templates in `templates/` directory:

- `concept_template.md`: Story concept structure
- `character_template.md`: Character development guide
- `chapter_template.md`: Chapter writing structure
- Genre-specific craft templates (fantasy, crime, comedy, etc.)
- `critical_perspective_template_generator.md`: Meta-template for analysis

Templates are loaded via `mythos/config/settings.py` constants:

- `META_TEMPLATE_PATH`: Path to meta-templates
- `TEMPLATE_SUBDIR`: Subdirectory for genre templates

### File Change Detection

**FileChangeTracker** (`mythos/utils/file_change_tracker.py`):

- Detects external modifications to story asset files
- Creates baseline snapshots in `.mythos/changes.json`
- Allows users to edit markdown files directly
- System preserves and uses external changes

## Critical Implementation Rules

### API Usage (from .cursor/index.mdc)

**OpenAI**:

- ALWAYS use Responses API (`/v1/responses`) - never Chat Completions
- Use `text` parameter (not `response_format`)
- JSON schemas require `additionalProperties: false` for strict mode
- Access response via `output_text` attribute

**Anthropic**:

- Use Messages API (`/v1/messages`)
- Standard message format with `role` and `content`

**Parameters**:

- Named parameters only, never positional
- Pull API keys from shell environment (no .env files)

### Error Handling

Two error types in `llm_utils.py`:

- `ProviderError`: Retry these (rate limits, timeouts, API issues)
- `ContentRefusalError`: Don't retry (safety policy violations)
- Always log errors explicitly, never silently ignore

### UX Patterns

**Thinking Indicators**:

```python
print_thinking("Creating your story concept...")
# Before any LLM operation that takes 10+ seconds
```

**Progress Tracking**:

```python
tracker = start_story_progress(story.title)
tracker.start_step("Generating characters", "Creating main cast...")
# Do work
tracker.complete_step("Generating characters", f"Created {count} characters")
```

**Confirmations**:

```python
confirm_next_step(
    current_step="Story assets created",
    next_step="Generate chapter manuscripts",
    story_title=story.title
)
```

### Data Patterns

**Creating Assets**:

```python
asset = StoryAsset(
    asset_type="Characters",
    title="Main Characters",
    summary="Brief summary",
    details="Full content...",
    relative_file_path="assets/characters.md"
)
story_builder._create_asset_with_metadata(story, asset)
```

**Loading Stories**:

```python
story_manager = StoryManager()
story = story_manager.load_story("story-title")
state, description = story_manager.get_story_state(story)
```

## Testing Guidelines

Focus on real user workflows:

- Happy path: Story creation from concept to EPUB
- Error recovery: Resume from interruption points
- Backwards compatibility: Legacy asset loading
- Performance regression: Token usage tracking

Avoid:

- Complex mocking without user validation
- Testing architectural edge cases over user needs
- Unvalidated assumptions about performance

## Tech Stack Versions

- **Python**: 3.12.2
- **OpenAI**: 1.97.0+ (Chat Completions API `/v1/chat/completions`)
- **Anthropic**: 0.58.0+ (Messages API `/v1/messages` with prompt caching & extended thinking)
- **Pydantic**: 2.11.7+ (data models)
- **Pytest**: 8.4.1+ (testing)

### Configured AI Models (October 2025)

**OpenAI**:

- `gpt-5` (Released Aug 2025: 400K context, reasoning_effort, verbosity controls)
- `gpt-5-mini` (Cost-effective GPT-5 variant)
- `gpt-4o-2024-08-06` (Stable backup: structured outputs, 128K context)
- `gpt-4o-mini-2024-07-18` (Fast/cheap backup)

**Anthropic**:

- `claude-sonnet-4` (Released May 2025: 72.7% SWE-bench, best balance)
- `claude-opus-4` (Most powerful: complex reasoning, $15/$75 per million tokens)
- `claude-3-5-sonnet-20241022` (Stable backup)
- `claude-3-5-haiku-20241022` (Fast/cheap backup)

### October 2025 Features Implemented

✅ **GPT-5 Support** - reasoning_effort (minimal/low/medium/high), verbosity (low/medium/high)
✅ **Claude 4 Extended Thinking** - Native API with configurable budgets (1K-128K tokens)
✅ **Interleaved Thinking** - Thinking between tool calls (Claude 4)
✅ **Prompt Caching** (Anthropic) - 90% cost savings via `cache_control`
✅ **Structured Outputs** (OpenAI) - `parallel_tool_calls: false` for compatibility
✅ **Specific Versions** - Pinned model dates for consistency
✅ **Proper Error Handling** - Retry logic with exponential backoff

## Common Gotchas

1. **Dual Storage**: Assets exist in both legacy `story.assets` dict AND new `story.asset_metadata` - maintain both for backward compatibility
2. **No .env files**: API keys from shell environment only
3. **Responses API**: OpenAI uses `/v1/responses` NOT `/v1/chat/completions`
4. **Global tracker**: Use `get_progress_tracker()` singleton, don't instantiate directly
5. **Markdown storage**: Asset content lives in .md files, not in Story object
6. **Story directories**: Created at `stories/{sanitized-title}/` with auto-uniquing

## Story Directory Structure

```
stories/
└── story-title/
    ├── story-title.story          # Serialized Story object
    ├── assets/                    # Story planning assets
    │   ├── concept.md
    │   ├── characters.md
    │   ├── plot.md
    │   └── themes.md
    ├── manuscript/                # Chapter content
    │   ├── chapter-01.md
    │   └── chapter-02.md
    └── .mythos/                   # Internal tracking
        └── changes.json           # File change baseline
```

## Entry Points

- **CLI**: `python -m mythos` → `__main__.py::__main__()`
- **API**: `from mythos.services.story_builder import StoryBuilder`
- **LLM**: `from mythos.utils.llm_utils import call_llm`

## Quick Reference

**Create a story programmatically**:

```python
from mythos.services.story_builder import StoryBuilder

builder = StoryBuilder()
story = builder.build_story("A detective who can see memories")
```

**Make LLM calls**:

```python
from mythos.utils.llm_utils import call_llm

response = call_llm(
    prompt="Write a scene...",
    tier="big",           # fast/medium/big
    temperature=0.8,
    max_tokens=2000
)
```

**Track progress**:

```python
from mythos.utils.progress_tracker import start_story_progress

tracker = start_story_progress("My Story")
tracker.start_step("Creating concept")
# ... work ...
tracker.complete_step("Creating concept", "Concept created")
```
