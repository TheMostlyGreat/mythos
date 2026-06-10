# Mythos Process Improvement Plan

**Status**: Draft
**Created**: 2025-10-08
**Based on**: "The Smoke and the Sacred" story generation experience

## Executive Summary

The Mythos story generation process successfully produces high-quality fiction with sophisticated world-building and compelling prose. However, operational reliability issues—particularly OpenAI API failures and timeout handling—create significant friction. This plan prioritizes improvements to make the manuscript generation phase as reliable as the planning phase.

## Priority 1: Critical Reliability Improvements

### 1.1 Implement Automatic Model Fallback

**Problem**: When GPT-5 API returns empty responses, the process fails completely, requiring manual configuration changes.

**Solution**: Implement automatic fallback strategy in `llm_utils.py`

**Implementation**:

```python
# In llm_utils.py::call_llm()
def call_llm(prompt, tier="medium", max_retries=3, **kwargs):
    primary_provider, primary_model = get_model_for_tier(tier)

    try:
        return _call_with_provider(primary_provider, primary_model, prompt, **kwargs)
    except ProviderError as e:
        # Log primary failure
        logger.warning(f"{primary_provider} failed after {max_retries} attempts: {e}")

        # Try fallback model for same tier
        fallback_provider, fallback_model = get_fallback_for_tier(tier)
        logger.info(f"Attempting fallback to {fallback_provider}:{fallback_model}")

        try:
            return _call_with_provider(fallback_provider, fallback_model, prompt, **kwargs)
        except ProviderError as fallback_error:
            raise LLMError(f"Both primary and fallback failed: {e}, {fallback_error}")
```

**Configuration**:

```python
# In settings.py
TIER_FALLBACKS = {
    "fast": [
        ("openai", "gpt-5-mini"),
        ("anthropic", "claude-3-5-haiku-20241022")
    ],
    "medium": [
        ("anthropic", "claude-sonnet-4-5-20250929"),
        ("openai", "gpt-5")
    ],
    "big": [
        ("anthropic", "claude-opus-4-1-20250805"),
        ("openai", "gpt-5"),
        ("anthropic", "claude-sonnet-4-5-20250929")  # Cheaper fallback
    ]
}
```

**User Experience**:

```
🤔 AI is processing...
⚠️  OpenAI API experiencing issues (3 failed attempts)
🔄 Switching to Claude Opus 4...
✅ Chapter 1 complete
```

**Estimated Effort**: 4-6 hours
**Testing Required**: Mock API failures, verify fallback triggers correctly

---

### 1.2 Add Chapter-Level Progress Indicators

**Problem**: During manuscript generation, users see only "AI is processing..." with no indication of progress through 9 chapters.

**Solution**: Enhance `ProgressTracker` to show chapter-level detail

**Implementation**:

```python
# In story_builder.py::write_chapters()
tracker = get_progress_tracker()
total_chapters = len(story.manuscript_metadata)

for idx, (chapter_key, chapter_meta) in enumerate(story.manuscript_metadata.items(), 1):
    tracker.start_step(
        name=f"chapter_{idx}",
        message=f"Writing Chapter {idx}/{total_chapters}: {chapter_meta.get('title', chapter_key)}"
    )

    # Generate chapter
    chapter_text = generate_narrative_text(prompt=chapter_prompt)

    # Save immediately
    chapter_path = story_dir / "manuscript" / f"{chapter_key}.md"
    chapter_path.write_text(chapter_text)

    tracker.complete_step(
        name=f"chapter_{idx}",
        message=f"✓ Chapter {idx} saved ({len(chapter_text)} chars)"
    )
```

**User Experience**:

```
📖 Writing Chapters: The Smoke and the Sacred
━━━━━━━━──────────────────── 3/9 (33%)
🔄 Chapter 3: The Infernal Assembly
   Estimated time: 6-8 minutes remaining
```

**Estimated Effort**: 3-4 hours
**Testing Required**: Verify progress updates correctly, test with different chapter counts

---

### 1.3 Implement Per-Chapter File Persistence

**Problem**: When timeouts occur, unclear if any chapters were saved. Need explicit confirmation.

**Solution**: Save each chapter immediately after generation with logging

**Implementation**:

```python
# In story_builder.py::write_chapters()
def write_chapters(self, story: Story) -> None:
    """Write manuscript chapters with per-chapter persistence."""
    logger.info(f"Starting manuscript generation for {len(story.manuscript_metadata)} chapters")

    for idx, (chapter_key, chapter_meta) in enumerate(story.manuscript_metadata.items(), 1):
        try:
            # Generate
            chapter_text = self._generate_chapter_text(story, chapter_key, chapter_meta)

            # Save immediately
            chapter_path = self._save_chapter(story, chapter_key, chapter_text)
            logger.info(f"✅ Saved chapter {idx}/{len(story.manuscript_metadata)}: {chapter_path}")
            print(f"✅ Chapter {idx} saved: {chapter_path.name}")

        except Exception as e:
            logger.error(f"Failed to generate chapter {idx} ({chapter_key}): {e}")
            print(f"❌ Chapter {idx} failed: {e}")
            # Continue with remaining chapters
            continue

    # Report final status
    completed = len(list((story.story_dir / "manuscript").glob("*.md")))
    logger.info(f"Manuscript generation complete: {completed}/{len(story.manuscript_metadata)} chapters")
```

**User Experience**:

```
📖 Writing Chapter 1/9: The Voice in the Lathe
✅ Chapter 1 saved: chapter_1.md (12,847 characters)

📖 Writing Chapter 2/9: The Engineer's Doubt
✅ Chapter 2 saved: chapter_2.md (11,203 characters)
```

**Estimated Effort**: 2-3 hours
**Testing Required**: Verify files saved correctly, test recovery after partial completion

---

### 1.4 Improve Error Messages and User Guidance

**Problem**: Technical error messages confuse non-technical users.

**Solution**: Translate technical errors into actionable user guidance

**Implementation**:

```python
# In llm_utils.py
class UserFriendlyError(Exception):
    """Exception with user-friendly message and technical details."""
    def __init__(self, user_message: str, technical_details: str):
        self.user_message = user_message
        self.technical_details = technical_details
        super().__init__(user_message)

def _handle_provider_error(error: ProviderError, provider: str) -> UserFriendlyError:
    """Convert technical errors to user-friendly messages."""

    if "empty response" in str(error).lower():
        return UserFriendlyError(
            user_message=f"The {provider} API is currently experiencing issues. Trying alternative provider...",
            technical_details=f"ProviderError: {error}"
        )

    if "rate limit" in str(error).lower():
        return UserFriendlyError(
            user_message=f"API rate limit reached. Waiting 30 seconds before retry...",
            technical_details=f"ProviderError: {error}"
        )

    # Default
    return UserFriendlyError(
        user_message=f"Temporary API issue. Retrying...",
        technical_details=f"ProviderError: {error}"
    )
```

**User Experience**:

```
Before:
❌ Failed to build story: Unexpected error in 'chapter_1': LLM call failed:
   OpenAI Chat Completions API failed after 3 attempts: OpenAI returned
   empty response - likely service issue

After:
⚠️  The OpenAI API is experiencing temporary issues
🔄 Switching to Claude Opus 4 and retrying...
✅ Chapter 1 generated successfully with fallback provider
```

**Estimated Effort**: 3-4 hours
**Testing Required**: Verify all error types handled, messages are clear

---

## Priority 2: Enhanced User Experience

### 2.1 Smart Resume with Gap Detection

**Problem**: If generation fails after chapter 5, user must manually determine where to resume.

**Solution**: Automatically detect completed chapters and resume from first gap

**Implementation**:

```python
# In story_builder.py
def smart_resume_chapters(self, story: Story) -> None:
    """Resume chapter generation from first gap."""
    manuscript_dir = story.story_dir / "manuscript"
    manuscript_dir.mkdir(exist_ok=True)

    # Find completed chapters
    existing_chapters = {
        path.stem for path in manuscript_dir.glob("*.md")
    }

    # Find gaps
    expected_chapters = set(story.manuscript_metadata.keys())
    missing_chapters = expected_chapters - existing_chapters

    if not missing_chapters:
        print(f"✅ All {len(expected_chapters)} chapters already complete")
        return

    print(f"📊 Progress: {len(existing_chapters)}/{len(expected_chapters)} chapters complete")
    print(f"📝 Resuming generation for {len(missing_chapters)} remaining chapters...")

    # Generate only missing chapters
    for chapter_key in sorted(missing_chapters):
        chapter_meta = story.manuscript_metadata[chapter_key]
        # ... generate chapter
```

**User Experience**:

```
📊 Loading story: The Smoke and the Sacred
✅ Found 5/9 chapters already complete
📝 Resuming from Chapter 6: The Algorithm of Grief

Would you like to:
1. Continue from Chapter 6 (generate 4 remaining chapters)
2. Regenerate all chapters (will overwrite existing)
3. Exit

Choice: 1
```

**Estimated Effort**: 4-5 hours
**Testing Required**: Test various completion states (0%, 50%, 100%)

---

### 2.2 Add Cost Estimation Before Generation

**Problem**: Users don't know how much story generation will cost before starting.

**Solution**: Estimate token usage and API costs upfront

**Implementation**:

```python
# In story_builder.py
def estimate_story_cost(self, story: Story) -> dict:
    """Estimate token usage and API cost for story generation."""

    # Estimate tokens per phase
    concept_tokens = 3000  # Based on historical data
    assets_tokens = 15000  # ~10 assets × 1500 tokens each
    chapters_tokens = len(story.manuscript_metadata) * 4500  # ~4500 per chapter

    total_tokens = concept_tokens + assets_tokens + chapters_tokens

    # Get cost per tier (using current BIG_MODEL for chapters)
    big_provider, big_model = BIG_MODEL
    cost_per_million = get_model_cost(big_provider, big_model)

    estimated_cost = (total_tokens / 1_000_000) * cost_per_million

    return {
        "total_tokens": total_tokens,
        "estimated_cost_usd": estimated_cost,
        "breakdown": {
            "concept": concept_tokens,
            "assets": assets_tokens,
            "chapters": chapters_tokens
        }
    }
```

**User Experience**:

```
📊 Story Generation Estimate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Concept:    ~3,000 tokens
Assets:     ~15,000 tokens
Chapters:   ~40,500 tokens (9 chapters)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total:      ~58,500 tokens
Estimated:  $0.85 - $1.20 USD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Continue with generation? (y/n):
```

**Estimated Effort**: 3-4 hours
**Testing Required**: Validate estimates against actual usage

---

### 2.3 Quality Validation Pass

**Problem**: No automated checks for consistency or quality issues across chapters.

**Solution**: Post-generation validation with automated checks

**Implementation**:

```python
# In story_builder.py or new validation module
def validate_manuscript(story: Story) -> dict:
    """Run quality checks on completed manuscript."""

    issues = []
    warnings = []

    # Check 1: Chapter length consistency
    chapter_lengths = []
    for chapter_path in (story.story_dir / "manuscript").glob("*.md"):
        length = len(chapter_path.read_text())
        chapter_lengths.append((chapter_path.name, length))

    avg_length = sum(l for _, l in chapter_lengths) / len(chapter_lengths)
    for name, length in chapter_lengths:
        if length < avg_length * 0.5:
            warnings.append(f"{name} is significantly shorter than average ({length} vs {avg_length:.0f} chars)")
        elif length > avg_length * 1.5:
            warnings.append(f"{name} is significantly longer than average ({length} vs {avg_length:.0f} chars)")

    # Check 2: Character name consistency
    character_names = extract_character_names(story)
    for chapter_path in (story.story_dir / "manuscript").glob("*.md"):
        chapter_text = chapter_path.read_text()
        # Check for name variations, misspellings
        # ...

    # Check 3: Incomplete chapters
    for chapter_path in (story.story_dir / "manuscript").glob("*.md"):
        text = chapter_path.read_text()
        if len(text) < 1000:
            issues.append(f"{chapter_path.name} appears incomplete (only {len(text)} characters)")

    return {
        "issues": issues,
        "warnings": warnings,
        "metrics": {
            "avg_chapter_length": avg_length,
            "total_word_count": sum(len(text.split()) for _, text in chapter_lengths)
        }
    }
```

**User Experience**:

```
✅ Manuscript generation complete

📊 Quality Check Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ All 9 chapters generated
✓ Average chapter: 11,500 characters
⚠️ Chapter 7 is 40% shorter than average
⚠️ Character name "Margarethe" appears as "Marguerite" in Chapter 5

Total word count: ~23,000 words
```

**Estimated Effort**: 5-6 hours
**Testing Required**: Test with various story types, validate heuristics

---

### 2.4 Increase Narrative Timeout

**Problem**: 240-second timeout may be insufficient for complex chapters with Claude Opus 4.

**Solution**: Adjust timeout based on tier and operation type

**Implementation**:

```python
# In settings.py
TIMEOUT_SETTINGS = {
    "concept": 300,      # 5 minutes
    "assets": 240,       # 4 minutes
    "narrative_fast": 180,   # 3 minutes
    "narrative_medium": 300,  # 5 minutes
    "narrative_big": 420      # 7 minutes (increased for Claude Opus 4)
}

# In llm_utils.py
def call_llm(prompt, tier="medium", operation_type="default", **kwargs):
    timeout_key = f"{operation_type}_{tier}" if operation_type != "default" else tier
    timeout = TIMEOUT_SETTINGS.get(timeout_key, STANDARD_TIMEOUT)
    # ... use timeout in API call
```

**Estimated Effort**: 1-2 hours
**Testing Required**: Verify longer timeouts work, no regressions

---

## Priority 3: Advanced Features

### 3.1 Chapter-by-Chapter Review Mode

**Problem**: Users may want to review and refine each chapter before proceeding to the next.

**Solution**: Add interactive mode that pauses after each chapter

**Implementation**:

```python
# In story_builder.py
def build_story_interactive(self, user_prompt: str) -> Story:
    """Build story with chapter-by-chapter review."""

    # ... generate concept and assets as normal

    for idx, (chapter_key, chapter_meta) in enumerate(story.manuscript_metadata.items(), 1):
        # Generate chapter
        chapter_text = self._generate_chapter_text(story, chapter_key, chapter_meta)
        self._save_chapter(story, chapter_key, chapter_text)

        # Show preview
        preview = chapter_text[:500] + "..." if len(chapter_text) > 500 else chapter_text
        print(f"\n📖 Chapter {idx} Preview:\n{preview}\n")

        # Prompt for action
        action = input(f"Chapter {idx} complete. [c]ontinue, [r]egenerate, [e]dit, [q]uit: ").lower()

        if action == 'r':
            # Regenerate with higher temperature or different prompt
            pass
        elif action == 'e':
            # Open in editor
            pass
        elif action == 'q':
            print(f"Stopping after chapter {idx}")
            break
```

**Estimated Effort**: 6-8 hours
**Testing Required**: Test all interaction paths, editor integration

---

### 3.2 Parallel Chapter Generation (Experimental)

**Problem**: Sequential generation of 9 chapters takes 40+ minutes. Some chapters could generate in parallel.

**Solution**: Identify independent chapters and generate concurrently

**Implementation**:

```python
# In story_builder.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def write_chapters_parallel(self, story: Story, max_workers: int = 3) -> None:
    """Generate independent chapters in parallel."""

    # Identify chapter dependencies
    dependencies = self._analyze_chapter_dependencies(story)

    # Group into batches (chapters 1-3 sequential, 4-6 can be parallel if independent)
    batches = self._create_generation_batches(story, dependencies)

    for batch_idx, chapter_keys in enumerate(batches):
        print(f"📦 Batch {batch_idx + 1}: Generating {len(chapter_keys)} chapters in parallel")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [
                executor.submit(self._generate_chapter_text, story, key, story.manuscript_metadata[key])
                for key in chapter_keys
            ]

            for future in futures:
                chapter_text = future.result()
                # Save chapter
```

**Challenges**:

- Ensuring narrative consistency across parallel generations
- Managing API rate limits with concurrent requests
- Higher complexity, harder to debug

**Estimated Effort**: 12-16 hours
**Testing Required**: Extensive testing for consistency, rate limit handling
**Recommendation**: Defer to Priority 4 until other improvements proven

---

## Implementation Roadmap

### Phase 1: Critical Reliability (Week 1-2)

1. Automatic model fallback (P1.1) - **6 hours**
2. Chapter-level progress indicators (P1.2) - **4 hours**
3. Per-chapter persistence (P1.3) - **3 hours**
4. Improved error messages (P1.4) - **4 hours**

**Total**: ~17 hours | **Impact**: Eliminates most user-facing failures

### Phase 2: Enhanced UX (Week 3-4)

5. Smart resume with gap detection (P2.1) - **5 hours**
6. Cost estimation (P2.2) - **4 hours**
7. Quality validation (P2.3) - **6 hours**
8. Increased narrative timeout (P2.4) - **2 hours**

**Total**: ~17 hours | **Impact**: Significantly improves user confidence and transparency

### Phase 3: Advanced Features (Month 2+)

9. Chapter-by-chapter review mode (P3.1) - **8 hours**
10. Parallel chapter generation (P3.2) - **16 hours** (if pursued)

**Total**: ~24 hours | **Impact**: Enables power user workflows

---

## Success Metrics

### Reliability Metrics

- **Target**: 95%+ story completion rate (down from current ~40% with OpenAI issues)
- **Measure**: Track `stories_attempted` vs `stories_completed` with full manuscript

### User Experience Metrics

- **Target**: Users know current progress within 5 seconds
- **Measure**: Progress indicator updates at least every 30 seconds during generation

### Cost Transparency Metrics

- **Target**: Cost estimates within 20% of actual
- **Measure**: Compare `estimated_cost` to `actual_token_usage * rate`

### Time to Recovery Metrics

- **Target**: Users can resume failed generation within 1 minute
- **Measure**: Time from failure to successful resume

---

## Testing Strategy

### Unit Tests

- Mock API failures to test fallback logic
- Test progress tracker with various chapter counts
- Validate cost estimation calculations

### Integration Tests

- Full story generation end-to-end with all features enabled
- Simulate API failures mid-generation, verify recovery
- Test resume with 0%, 25%, 50%, 75%, 100% completion states

### User Acceptance Tests

- Non-technical user attempts story generation without documentation
- Measure time-to-completion and error recovery success rate
- Collect feedback on error message clarity

---

## Rollout Plan

### Phase 1 (Immediate)

1. Implement P1.1-P1.4 in feature branch
2. Test against "The Smoke and the Sacred" scenario
3. Merge to main after successful test

### Phase 2 (2-3 weeks)

1. Implement P2.1-P2.4 in feature branch
2. Beta test with 3-5 different story concepts
3. Refine based on feedback

### Phase 3 (1-2 months)

1. Evaluate demand for advanced features
2. Implement highest-priority items
3. Consider parallel generation only if users request faster generation

---

## Risk Assessment

### High Risk Items

- **Parallel chapter generation (P3.2)**: High complexity, uncertain consistency gains
  - _Mitigation_: Defer until proven need, implement simpler solutions first

### Medium Risk Items

- **Automatic fallback (P1.1)**: Could mask persistent issues, higher API costs
  - _Mitigation_: Log all fallbacks, alert if fallback rate >10%

### Low Risk Items

- **Progress indicators (P1.2)**: Minimal risk, pure UX improvement
- **Cost estimation (P2.2)**: Worst case is inaccurate estimate, doesn't break generation

---

## Cost-Benefit Analysis

### High ROI (Implement First)

- **P1.1 Automatic Fallback**: 6 hours → eliminates 60%+ of user-reported failures
- **P1.2 Progress Indicators**: 4 hours → eliminates "is it working?" anxiety
- **P1.3 Per-Chapter Persistence**: 3 hours → enables recovery from any failure point

### Medium ROI (Implement Second)

- **P2.1 Smart Resume**: 5 hours → saves users 10-30 minutes per failed attempt
- **P2.3 Quality Validation**: 6 hours → catches issues before user reads full manuscript

### Lower ROI (Consider Later)

- **P3.1 Interactive Review**: 8 hours → only valuable for users who want iterative refinement
- **P3.2 Parallel Generation**: 16 hours → complex implementation for ~50% time savings

---

## Future Considerations

### Additional Improvements (Not Prioritized)

- **Multi-language support**: Generate stories in languages other than English
- **Custom style training**: Fine-tune models on user's preferred writing style
- **Character consistency checker**: Use embeddings to detect character drift
- **Automated cover art generation**: Integration with image generation APIs
- **EPUB theme customization**: Let users control fonts, colors, layout

### Technical Debt to Address

- Consolidate background bash process management
- Improve logging structure for better debugging
- Add comprehensive type hints throughout codebase
- Create comprehensive API documentation

---

## Conclusion

The Mythos story generation process demonstrates strong core capabilities but needs operational hardening. By implementing the Priority 1 improvements (automatic fallback, progress indicators, per-chapter persistence, better errors), we can transform the user experience from "technical and fragile" to "reliable and transparent."

The recommended approach:

1. **Phase 1 first** (17 hours) - fixes the critical pain points
2. **Evaluate impact** - measure completion rate improvements
3. **Phase 2 next** (17 hours) - if Phase 1 succeeds, add transparency features
4. **Phase 3 selectively** - only implement advanced features if users request them

**Estimated total effort for Phases 1-2**: ~34 hours (~1 week of focused development)

**Expected outcome**: Story generation completion rate improves from ~40% to 95%+, with clear user feedback throughout the process.
