# Incremental Manuscript Building & Opening Scene Implementation Plan

## Overview

Transform the current "all-at-once" manuscript building into an incremental, user-controlled process while adding a dedicated Opening Scene asset based on previous implementation patterns.

## Research Findings: Previous Opening Scene Implementation

From git commit `19d9961` ("got it opening scene"), the previous opening scene was implemented as:

### **Original Prompt Structure**

```python
prompt = (
    "Draft a compelling 500 word opening scene for the following chapter summary. "
    "Ensure that it grips the reader so that they want to read more of the story.\n" +
    "Here is the broader context for the story:\n" +
    self.story.concept +
    "\n"
)
if chapter_summary:
    prompt += (
        "Here is the chapter summary:\n" +
        chapter_summary +
        "\n"
    )
if self.story.writing_style:
    prompt += (
        "Here is the writing style:\n" +
        self.story.writing_style +
        "\n"
    )
```

### **Key Characteristics**

- **Target**: 500 words
- **Context Sources**: Story concept, chapter summary, writing style
- **Focus**: "Grips the reader so they want to read more"
- **Generation Method**: Narrative text (not planning text)
- **Output**: Saved as `opening_scene.md` in story directory

---

## 1. Opening Scene Asset Implementation

### **New Asset Type**

- **Add to AssetTypeNames**: `OPENING_SCENE = "opening_scene"`
- **Directory**: `ASSETS_DIR` (alongside other story assets)
- **Template**: Create `templates/opening_scene_template.md`
- **Generation Timing**: After chapter outlines are generated (requires chapter summary context)

### **Opening Scene Template**

```markdown
# Opening Scene Craft Framework

## Hook Strategy

**What immediately grabs the reader's attention and makes them want to continue reading:**

## Scene Setting

**The specific time, place, and atmosphere where your story begins:**

## Character Introduction

**How we first encounter your protagonist - their situation, state of mind, and immediate circumstances:**

## Conflict/Tension Establishment

**The immediate problem, question, or tension that drives the opening forward:**

## Tone and Voice

**The narrative voice and emotional atmosphere you're establishing:**

## Sensory Details

**Specific sights, sounds, smells, textures that immerse the reader:**

## Opening Lines Options

**2-3 potential opening sentences or paragraphs to test different approaches:**

---

## Integration with Story Context

### **Story Concept Connection**

**How this opening scene reflects and launches your core story concept:**

### **Character Arc Beginning**

**What this scene establishes about your protagonist's starting point:**

### **World/Setting Introduction**

**How this scene efficiently establishes your story world:**
```

### **Opening Scene Generation Approach**

**Two-Phase Process:**

1. **Planning Asset**: Create opening scene framework using template
2. **Narrative Generation**: Generate actual 500-word opening scene

**Simplified Prompt Structure**:

```
"Draft a compelling 500 word opening scene for the following story.
Ensure that it grips the reader so that they want to read more of the story.
Here is the story synopsis: {synopsis}
```

**Simple Dependencies**:

- Use existing synopsis (no need to generate chapter summary)
- Combines story concept, synopsis, and writing style
- **Position**: After story assets, before or after chapter outlines (flexible)
- For dual-system approach: saves both planning asset AND narrative file (`opening_scene.md`)

---

## 2. Incremental Chapter Building

### **Simplified Interactive Approach**

**Core Principle**: Extend existing `confirm_next_step` pattern instead of creating complex menus

**Chapter Writing Flow**:

1. Show progress ("3/8 chapters written, next: chapter_4")
2. Simple 3-choice dialog:
   - "Write next chapter only"
   - "Write all remaining chapters"
   - "Generate EPUB with current chapters"
3. Use existing confirmation patterns for additional choices

**Benefits**:

- Consistent with current UI patterns
- Reduces cognitive load vs. numbered menus
- Maintains natural flow with clear stopping points

### **Key New Methods Needed**

**Chapter Tracking:**

- `write_next_chapter()`: Write the next unwritten chapter in sequence
- `write_all_remaining_chapters()`: Write all chapters that haven't been written yet
- `get_next_chapter_to_write()`: Find which chapter should be written next

**Progress Tracking:**

- `get_written_chapter_count()`: Count completed chapters
- `get_total_chapter_count()`: Count total planned chapters
- `show_chapter_progress()`: Display current progress

**Core Logic:**

- Compare chapter outlines (in `story.assets`) vs. written chapters (in `story.manuscript`)
- Sort chapters by number to maintain sequence
- Use existing `_write_specific_chapters()` method for actual chapter generation

---

## 3. Chapter Outline Strategy

### **Chapter Outline Strategy Options**

**Default Approach**: Generate all chapter outlines at once

- **Rationale**: Outlines are lightweight and provide overall story structure
- **Benefits**: User can see full story arc, make structural adjustments
- **Current Implementation**: Keep existing `generate_chapter_assets()` method

**Optional Approach**: Incremental outline generation

- **When**: User wants more control over individual chapter planning
- **Implementation**: Add user choice before outline generation
- **Pattern**: Use existing `confirm_next_step()` for each chapter outline

**User Choice**:

- Simple 2-option dialog: "All at once" vs. "One by one"
- Default to "all at once" for story structure coherence
- Allow user to review and modify outlines before proceeding to narrative writing

---

## 4. Enhanced Story Building Flow

### **Updated Sequence**

**Current Flow** → **New Flow**

1. **Story Assets** (unchanged)
2. **NEW: Opening Scene Generation**
   - Use existing synopsis as context
   - Can generate after story assets (flexible timing)
3. **Chapter Outlines**
   - Add user choice: "All at once" vs. "One by one"
   - Default to all at once for story structure
4. **Chapter Writing** (NEW: Incremental approach)
   - Show progress ("2/8 chapters written")
   - User choice each iteration:
     - Write next chapter only
     - Write all remaining chapters
     - Generate EPUB with current chapters
5. **EPUB Generation**
   - Available anytime after first chapter
   - Final prompt when all chapters complete

### **Key Changes**

- **Incremental by Default**: One chapter at a time unless user chooses otherwise
- **Progress Visibility**: Always show current chapter status
- **Exit Flexibility**: User can generate EPUB and resume later
- **Natural Stopping Points**: Use existing `confirm_next_step` pattern

---

## 5. EPUB Generation Independence

### **Current State**: ✅ Already Works

The existing `create_epub()` function already works with partial manuscripts:

```python
# From mythos/utils/epub.py
for chapter_name, story_asset in story.manuscript.items():
    # Processes whatever chapters exist in story.manuscript
```

### **Enhanced EPUB Generation**

**Core Capability**: Generate EPUB from any number of written chapters

**Key Features**:

- Works with 1 chapter or all chapters
- Shows progress ("EPUB includes 3/8 chapters")
- Clear messaging about remaining chapters
- Uses existing `create_epub()` function

**User Experience**:

- Available as option after each chapter
- Clear indication of what's included
- Ability to continue writing later and regenerate

---

## 6. Implementation Sequence

### **Phase 1: Opening Scene Asset**

1. ✅ Add `OPENING_SCENE` to `AssetTypeNames` enum
2. ✅ Create `templates/opening_scene_template.md`
3. ✅ Add opening scene to `AssetTypes` configuration
4. ✅ Implement `generate_opening_scene_asset()` method with chapter summary context
5. ✅ Integrate into story building flow AFTER chapter outlines (correct sequence)

### **Phase 2: Incremental Chapter Writing**

1. ✅ Implement new chapter writing methods (`write_next_chapter`, `write_all_remaining_chapters`)
2. ✅ Create simplified choice system using existing `confirm_next_step` patterns
3. ✅ Add chapter progress tracking methods
4. ✅ Update main `build_story` flow with incremental chapter loop

### **Phase 3: Optional Incremental Outlines**

1. ✅ Implement `generate_chapter_assets_incremental()`
2. ✅ Add outline strategy choice menu
3. ✅ Integrate strategy choice into build flow

### **Phase 4: Enhanced User Experience**

1. ✅ Add chapter-specific progress displays
2. ✅ Implement EPUB generation at any stage
3. ✅ Add review and navigation options
4. ✅ Test full workflow end-to-end

---

## 7. User Experience Flow

```
1. Story Concept & Assets Generation
   ↓
2. Opening Scene Framework & Narrative
   (use synopsis as context - simple!)
   ↓
3. Choose Outline Strategy:
   • All at once (default)
   • One by one (optional)
   ↓
4. Incremental Chapter Writing:
   • Write next chapter (default)
   • Write all remaining chapters
   • Generate EPUB with current chapters
   ↓
5. EPUB Generation (available anytime after Chapter 1)
```

---

## 8. Benefits

### **Token Efficiency**

- Only generates chapters when user is ready to read them
- Reduces wasted tokens on unread content

### **User Control**

- Multiple workflow options for different user preferences
- Can stop and resume at any point
- Can generate EPUB at any stage

### **Better Story Starts**

- Dedicated opening scene asset ensures strong story beginnings
- Combines framework planning with narrative generation

### **Backward Compatibility**

- Bulk options preserve current workflow for users who prefer it
- Incremental features are optional enhancements

### **Flexible Publishing**

- EPUB generation works with any number of written chapters
- Supports iterative publishing workflow

---

## 9. Files to Modify

### **Core Implementation**

- `mythos/config/settings.py` - Add OPENING_SCENE asset type
- `mythos/services/story_builder.py` - Main implementation
- `templates/opening_scene_template.md` - New template

### **Supporting Files**

- `__main__.py` - Update CLI integration if needed
- Tests - Add test coverage for new functionality

---

## 10. Future Enhancements

### **Chapter Dependencies**

- Track chapter dependencies for non-linear writing
- Allow writing chapters out of order

### **Chapter Branching**

- Support multiple chapter versions
- A/B testing for different chapter approaches

### **Collaborative Features**

- Chapter-level sharing and feedback
- Multi-author chapter assignment

### **Analytics**

- Track which chapters get read vs. skipped
- User engagement metrics per chapter

---

## 11. Plan Improvements Made

### **Fixed Critical Issues**

1. **Corrected Sequence**: Opening scene now generates AFTER chapter outlines (requires chapter summary context)
2. **Fixed Code Logic**: `write_specific_chapter_by_title` now properly validates chapter outline assets
3. **Simplified User Flow**: Replaced complex menu system with existing `confirm_next_step` patterns
4. **Better Integration**: Uses established UI patterns instead of creating new ones

### **Key Changes from Original Plan**

- **Opening Scene Timing**: Moved from "after assets, before outlines" to "after outlines"
- **Prompt Structure**: Uses chapter summary as primary context (matches git history research)
- **Interactive Flow**: Simple choices instead of numbered menus
- **Code Validation**: Added proper error handling for missing chapter outlines
- **UI Consistency**: Extends existing patterns rather than creating new ones

### **Maintained Features**

- **Dual Opening Scene System**: Planning asset + narrative generation (as requested)
- **Incremental Chapters**: One-at-a-time with bulk option
- **EPUB Flexibility**: Generate at any stage after first chapter
- **Backward Compatibility**: All existing workflows preserved
