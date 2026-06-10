# Multi-Tier LLM System Implementation Plan

## 🎯 **Project Goals**

### **Primary Objectives**

1. **Cost Optimization**: Use appropriate model sizes for different tasks
2. **Quality Optimization**: Match model capabilities to task complexity
3. **Provider Flexibility**: Switch between OpenAI and Anthropic easily
4. **Developer Experience**: Minimal code changes, maximum configurability

### **Success Criteria**

- [ ] Can configure different models for FAST/MEDIUM/BIG tiers
- [ ] Can switch providers without code changes
- [ ] Existing code continues to work unchanged
- [ ] Clear cost/quality trade-offs for each tier
- [ ] Simple environment variable configuration

---

## 📋 **Technical Requirements**

### **Model Tier Definition** ⚡ **UPDATED FOR 2025**

```
FAST Tier:
- Use Cases: Summarization, intent detection, simple analysis, quick responses
- Target Models: GPT-4.1-nano ($0.10/$0.40), GPT-4o-mini, Claude-Haiku
- Priority: Speed + Cost (sub-second responses)

MEDIUM Tier:
- Use Cases: Planning, asset creation, research, critical analysis
- Target Models: GPT-4.1-mini ($0.40/$1.60), o4-mini ($1.10/$4.40), Claude-Sonnet
- Priority: Balance of quality + cost + 1M context

BIG Tier:
- Use Cases: Narrative writing, complex creative tasks, reasoning
- Target Models: GPT-4.1 ($2.00/$8.00), o3 ($1.00/$4.00), GPT-4.5 ($75/$150), Claude-Opus
- Priority: Maximum quality + large context + reasoning
```

### **Configuration Format**

```bash
# Environment variables in format "provider:model"
FAST_MODEL="openai:gpt-4.1-nano"      # 🚀 NEW: Fastest & cheapest
MEDIUM_MODEL="openai:gpt-4.1-mini"    # 🚀 NEW: 1M context + great cost/perf
BIG_MODEL="openai:o3"                 # 🚀 NEW: Built-in tools + reasoning
```

### **Backward Compatibility Requirements**

- All existing function signatures remain unchanged
- No breaking changes to public APIs
- Existing code automatically uses appropriate tiers

---

## 🏗️ **Implementation Architecture**

### **Core Components**

#### **1. Configuration Layer**

```python
# mythos/config/settings.py
FAST_MODEL = os.getenv("FAST_MODEL", "openai:gpt-4.1-nano")
MEDIUM_MODEL = os.getenv("MEDIUM_MODEL", "openai:gpt-4.1-mini")
BIG_MODEL = os.getenv("BIG_MODEL", "openai:o3")

def parse_model_config(model_string: str) -> tuple[str, str]:
    """Parse 'provider:model' into (provider, model)"""
```

#### **2. Unified LLM Interface**

```python
# mythos/utils/llm_utils.py
def call_llm(
    prompt: str,
    system_prompt: str = PLANNING_SYSTEM_PROMPT,
    tier: Literal["fast", "medium", "big"] = "medium",
    json_output: bool = False,
    json_schema: Optional[Dict[str, Any]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    **kwargs
) -> str:
```

#### **3. Provider Adapters**

```python
def _call_openai(prompt, system_prompt, model, json_output, json_schema, tools, **kwargs) -> str:
def _call_anthropic(prompt, system_prompt, model, json_output, tools, **kwargs) -> str:
```

#### **4. Function Updates**

```python
# mythos/services/writer.py - Update existing functions to use tiers
generate_planning_text()    # → tier="medium"
generate_narrative_text()   # → tier="big"
summarize_text()           # → tier="fast"
generate_character_list()  # → tier="medium"
generate_web_enhanced_research() # → tier="medium"
```

---

## 📊 **Function-to-Tier Mapping** ⚡ **UPDATED FOR 2025**

### **FAST Tier Functions** 🚀

| Function           | Current Usage       | **OpenAI 2025**                  | **Anthropic 2025**              | Recommended                    |
| ------------------ | ------------------- | -------------------------------- | ------------------------------- | ------------------------------ |
| `summarize_text()` | All asset summaries | GPT-4.1-nano<br>$0.10/$0.40      | Claude Haiku 3<br>$0.25/$1.25   | 🏆 OpenAI (60% cheaper)        |
| Intent detection   | User input parsing  | GPT-4.1-nano<br>Sub-second speed | Claude Haiku 3.5<br>$0.80/$4.00 | 🏆 OpenAI (4x faster, cheaper) |

### **MEDIUM Tier Functions** 🎯

| Function                      | Current Usage        | **OpenAI 2025**                          | **Anthropic 2025**                     | Recommended                                     |
| ----------------------------- | -------------------- | ---------------------------------------- | -------------------------------------- | ----------------------------------------------- |
| `generate_planning_text()`    | Most planning assets | GPT-4.1-mini<br>$0.40/$1.60 + 1M context | Claude Sonnet 4<br>$3.00/$15.00 + 200k | 🏆 OpenAI (87% cheaper + 5x context)            |
| `generate_character_list()`   | Character creation   | GPT-4.1-mini<br>1M context perfect       | Claude Sonnet 4<br>Premium quality     | ⚖️ Either (OpenAI for cost, Claude for quality) |
| `generate_chapter_list()`     | Chapter planning     | GPT-4.1-mini<br>Excellent value          | Claude Sonnet 4<br>Extended thinking   | 🏆 OpenAI (great cost/performance)              |
| Critical perspective analysis | Story analysis       | GPT-4.1-mini<br>Good reasoning           | Claude Sonnet 4<br>Constitutional AI   | ⚖️ Either (depends on safety needs)             |

### **BIG Tier Functions** 🎭

| Function                    | Current Usage     | **OpenAI 2025**             | **Anthropic 2025**                        | Recommended                                   |
| --------------------------- | ----------------- | --------------------------- | ----------------------------------------- | --------------------------------------------- |
| `generate_narrative_text()` | Chapter writing   | o3<br>$1.00/$4.00 + tools   | Claude Opus 4<br>$15.00/$75.00 + thinking | ⚖️ **Hybrid**: o3 for speed, Opus for premium |
| Complex reasoning           | Advanced analysis | o3<br>Built-in capabilities | Claude Opus 4<br>Extended thinking        | 🏆 Claude (reasoning specialist)              |

### **💡 Strategic Recommendations by Function Type**

- **Speed-critical** (summaries, intent): **All OpenAI** for sub-second responses
- **Cost-sensitive** (bulk processing): **All OpenAI** for 60-93% savings
- **Quality-critical** (narrative, reasoning): **Hybrid** OpenAI + Anthropic
- **Context-heavy** (long documents): **OpenAI** for 1M token windows

---

## 🔧 **Implementation Steps**

### **Phase 1: Core Infrastructure** (1 hour)

1. **Add configuration constants** to `settings.py`
2. **Create `parse_model_config()`** helper function
3. **Implement `call_llm()`** unified interface
4. **Add provider adapter functions**

### **Phase 2: Function Updates** (45 minutes)

5. **Update writer.py functions** to use `call_llm()`
6. **Update story_builder.py direct calls** to use `call_llm()`
7. **Update story_questioner.py calls** to use `call_llm()`

### **Phase 3: Testing & Validation** (30 minutes)

8. **Test each tier configuration**
9. **Verify backward compatibility**
10. **Test provider switching**

### **Phase 4: Documentation** (15 minutes)

11. **Update configuration docs**
12. **Add usage examples**

---

## 🧪 **Testing Strategy**

### **Unit Tests**

- [ ] `parse_model_config()` with valid/invalid inputs
- [ ] `call_llm()` with each tier
- [ ] Provider adapter functions
- [ ] Backward compatibility for existing functions

### **Integration Tests**

- [ ] Full story generation with different configurations
- [ ] Provider switching mid-workflow
- [ ] Cost optimization scenarios

### **Configuration Tests**

```bash
# Test various configurations
export FAST_MODEL="openai:gpt-4o-mini"
export MEDIUM_MODEL="anthropic:claude-sonnet"
export BIG_MODEL="anthropic:claude-opus"
# Run test suite

export FAST_MODEL="anthropic:claude-haiku"
export MEDIUM_MODEL="openai:gpt-4o"
export BIG_MODEL="openai:gpt-4o"
# Run test suite
```

---

## 📈 **Configuration Examples** ⚡ **UPDATED FOR 2025**

### **🏆 Recommended Production Setup**

```bash
# Optimal cost/quality/context balance (2025 models)
export FAST_MODEL="openai:gpt-4.1-nano"     # $0.10/$0.40 per 1M tokens + 1M context
export MEDIUM_MODEL="openai:gpt-4.1-mini"   # $0.40/$1.60 per 1M tokens + 1M context
export BIG_MODEL="openai:o3"                # $1.00/$4.00 per 1M tokens + built-in tools
```

### **💰 Ultra-Budget Setup**

```bash
# Maximum cost savings
export FAST_MODEL="openai:gpt-4.1-nano"     # Fastest & cheapest
export MEDIUM_MODEL="openai:gpt-4.1-nano"   # Same model for consistency
export BIG_MODEL="openai:gpt-4.1-mini"      # Step up only when needed
```

### **🎯 Quality-Focused Setup**

```bash
# Best models regardless of cost
export FAST_MODEL="openai:gpt-4.1-mini"     # Still fast but higher quality
export MEDIUM_MODEL="openai:o4-mini"        # Reasoning capabilities
export BIG_MODEL="openai:gpt-4.5"           # Premium creative model (expensive!)
```

### **🔄 All-Anthropic Setup**

```bash
# Full Anthropic stack (still supported)
export FAST_MODEL="anthropic:claude-haiku"
export MEDIUM_MODEL="anthropic:claude-sonnet"
export BIG_MODEL="anthropic:claude-opus"
```

### **⚡ Speed-Optimized Setup**

```bash
# For latency-critical applications
export FAST_MODEL="openai:gpt-4.1-nano"     # OpenAI's fastest model
export MEDIUM_MODEL="openai:gpt-4.1-nano"   # Consistency in speed
export BIG_MODEL="openai:o4-mini"           # Fast reasoning model
```

### **🎯 Quality-First Hybrid**

```bash
# Mix providers for maximum quality
export FAST_MODEL="openai:gpt-4.1-nano"         # Best speed/cost ratio
export MEDIUM_MODEL="anthropic:claude-sonnet-4" # Premium reasoning
export BIG_MODEL="anthropic:claude-opus-4"      # Extended thinking
```

### **💡 Smart Hybrid Strategy**

```bash
# OpenAI for speed/cost + Anthropic for complexity
export FAST_MODEL="openai:gpt-4.1-nano"      # Sub-second responses
export MEDIUM_MODEL="openai:gpt-4.1-mini"    # 1M context + great value
export BIG_MODEL="anthropic:claude-opus-4"   # Extended thinking when needed
```

---

## 🚧 **Implementation Challenges & Solutions**

### **Challenge 1: Provider Differences**

**Problem**: OpenAI has structured outputs, Anthropic doesn't  
**Solution**: Graceful degradation - add JSON instruction to system prompt for Anthropic

### **Challenge 2: Model Override**

**Problem**: Need to temporarily change global model settings  
**Solution**: Context manager or temporary override pattern

### **Challenge 3: Tool Support**

**Problem**: Different tool formats between providers  
**Solution**: Adapter layer that converts tool specifications

### **Challenge 4: Error Handling**

**Problem**: Different error types between providers  
**Solution**: Consistent error handling in `call_llm()`

---

## 💰 **Cost Impact Analysis** ⚡ **MASSIVE 2025 SAVINGS**

### **Previous State** (All GPT-4o equivalent)

- Summarization: $5.00 per 1M input tokens
- Planning: $5.00 per 1M input tokens
- Narrative: $5.00 per 1M input tokens

### **🚀 New Optimized State** (2025 Tiered approach)

- Summarization (FAST): $0.10 per 1M input tokens ⚡ **GPT-4.1-nano**
- Planning (MEDIUM): $0.40 per 1M input tokens ⚡ **GPT-4.1-mini + 1M context**
- Narrative (BIG): $1.00 per 1M input tokens ⚡ **o3 with built-in tools**

### **🎉 Estimated Savings**

- **Summarization**: **98% cost reduction** (was $5.00 → now $0.10)
- **Planning**: **92% cost reduction** (was $5.00 → now $0.40)
- **Narrative**: **80% cost reduction** (was $5.00 → now $1.00)
- **Overall**: **85-95% cost reduction** (depending on usage mix)

### **🔥 Additional Benefits (OpenAI Strategy)**

- **1M token context** on FAST & MEDIUM tiers (vs Anthropic's 200k)
- **Built-in tools** on BIG tier (web search, Python, image analysis)
- **4x faster speed** on FAST tier (GPT-4.1-nano is OpenAI's fastest)
- **Better coding performance** across all tiers

### **🎭 Anthropic Alternative Benefits**

- **Extended thinking** for complex reasoning and chain-of-thought
- **Constitutional AI** for safer, more aligned responses
- **Premium quality** on creative and analytical tasks
- **200k context** still excellent for most use cases

---

## 🎯 **Success Metrics**

### **Functional Metrics**

- [ ] All existing tests pass
- [ ] Can switch providers via environment variables
- [ ] No breaking changes to public APIs
- [ ] All three tiers can use either provider

### **Quality Metrics**

- [ ] FAST tier adequate for summarization
- [ ] MEDIUM tier maintains planning quality
- [ ] BIG tier improves or maintains narrative quality

### **Developer Experience Metrics**

- [ ] Configuration takes < 30 seconds
- [ ] Clear documentation and examples
- [ ] Error messages are helpful
- [ ] Easy to debug configuration issues

---

## 📝 **Migration Strategy**

### **Zero-Downtime Migration**

1. **Add new system alongside existing** (no changes to existing functions)
2. **Update functions internally** to use new system
3. **Test thoroughly** with existing workflows
4. **Deploy with current configuration** (no behavior change)
5. **Gradually optimize** configurations in production

### **Rollback Plan**

- Keep existing `call_OpenAI_API()` and `call_Anthropic_API()` functions
- Simple revert: change function implementations back
- No data migration needed
- Configuration is purely runtime

---

## 🤝 **Alignment Questions**

Before implementation, please confirm:

1. **Tier assignments**: Do you agree with the FAST/MEDIUM/BIG function assignments?
2. **Configuration format**: Is `"provider:model"` format acceptable?
3. **Default models**: Are the proposed defaults good for your use case?
4. **Provider differences**: Acceptable to handle graceful degradation for missing features?
5. **Implementation scope**: Any additional functions that need tier assignment?

---

## 📅 **Timeline**

| Phase                     | Duration    | Dependencies         |
| ------------------------- | ----------- | -------------------- |
| Planning alignment        | 30 min      | This document review |
| Phase 1: Infrastructure   | 1 hour      | Approved plan        |
| Phase 2: Function updates | 45 min      | Phase 1 complete     |
| Phase 3: Testing          | 30 min      | Phase 2 complete     |
| Phase 4: Documentation    | 15 min      | Phase 3 complete     |
| **Total**                 | **3 hours** |                      |

---

## 🚨 **CRITICAL UPDATE: 2025 Model Revolution Impact**

### **🔥 OpenAI vs Anthropic 2025 Model Analysis**

#### **🥇 OpenAI DOMINATES on Cost & Context**

```bash
# 2025 OPENAI OPTIMAL SETUP - Massive savings + huge context
export FAST_MODEL="openai:gpt-4.1-nano"     # $0.10/$0.40 + 1M context
export MEDIUM_MODEL="openai:gpt-4.1-mini"   # $0.40/$1.60 + 1M context
export BIG_MODEL="openai:o3"                # $1.00/$4.00 + built-in tools
```

#### **🥈 Anthropic Strong on Quality & Safety**

```bash
# 2025 ANTHROPIC SETUP - Premium quality + extended thinking
export FAST_MODEL="anthropic:claude-haiku-3"    # $0.25/$1.25 + 200k context
export MEDIUM_MODEL="anthropic:claude-sonnet-4" # $3.00/$15.00 + 200k context
export BIG_MODEL="anthropic:claude-opus-4"      # $15.00/$75.00 + extended thinking
```

### **📊 Head-to-Head Comparison**

| Tier       | OpenAI 2025                               | Anthropic 2025                                      | Winner        | Why                                 |
| ---------- | ----------------------------------------- | --------------------------------------------------- | ------------- | ----------------------------------- |
| **FAST**   | GPT-4.1-nano<br>$0.10/$0.40<br>1M context | Claude Haiku 3<br>$0.25/$1.25<br>200k context       | 🏆 **OpenAI** | 60% cheaper + 5x larger context     |
| **MEDIUM** | GPT-4.1-mini<br>$0.40/$1.60<br>1M context | Claude Sonnet 4<br>$3.00/$15.00<br>200k context     | 🏆 **OpenAI** | 87% cheaper + 5x larger context     |
| **BIG**    | o3<br>$1.00/$4.00<br>Built-in tools       | Claude Opus 4<br>$15.00/$75.00<br>Extended thinking | 🏆 **OpenAI** | 93% cheaper + built-in capabilities |

### **🎯 Strategic Recommendations**

#### **Cost-Optimized Strategy** (Recommended)

```bash
# BEST VALUE: All OpenAI for massive savings
export FAST_MODEL="openai:gpt-4.1-nano"
export MEDIUM_MODEL="openai:gpt-4.1-mini"
export BIG_MODEL="openai:o3"
# Total savings: 85-95% vs current costs
```

#### **Quality-First Strategy**

```bash
# PREMIUM QUALITY: Mix for best capabilities
export FAST_MODEL="openai:gpt-4.1-nano"      # Best speed/cost
export MEDIUM_MODEL="anthropic:claude-sonnet-4" # Premium reasoning
export BIG_MODEL="anthropic:claude-opus-4"      # Extended thinking
# Cost impact: ~40% savings vs current, maximum quality
```

#### **Hybrid Strategy** (Best of Both)

```bash
# BALANCED: OpenAI for speed/cost, Anthropic for complex work
export FAST_MODEL="openai:gpt-4.1-nano"      # 4x faster, cheapest
export MEDIUM_MODEL="openai:gpt-4.1-mini"    # 1M context, great value
export BIG_MODEL="anthropic:claude-opus-4"   # Extended thinking for complexity
# Cost impact: ~70% savings vs current
```

### **🔑 Key Insights**

1. **OpenAI wins on economics**: 60-93% cheaper across all tiers
2. **OpenAI wins on context**: 1M tokens vs Anthropic's 200k
3. **Anthropic wins on safety**: Constitutional AI + extended thinking
4. **OpenAI wins on speed**: GPT-4.1-nano is fastest model available
5. **Both support tools**: Built-in capabilities vs external APIs

### **🤝 Updated Alignment Questions**

1. **Cost vs Quality**: Accept 85-95% savings with OpenAI, or pay premium for Anthropic quality?
2. **Context needs**: Is 1M tokens (OpenAI) vs 200k tokens (Anthropic) important for your use case?
3. **Speed requirements**: Does GPT-4.1-nano's sub-second speed matter for UX?
4. **Extended thinking**: Do you need Claude's chain-of-thought for complex reasoning?
5. **Hybrid approach**: Mix providers (OpenAI for speed/cost + Anthropic for quality)?

---

**OpenAI's 2025 revolution is MASSIVE - but Anthropic still has quality advantages. Your call!** ⚖️🚀
