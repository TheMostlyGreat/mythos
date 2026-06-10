# October 2025 AI Model Upgrade

## 🚀 Latest Models Configured

### Production Configuration

- **FAST**: `gpt-5-mini` (OpenAI) - Ultra-fast, cost-effective GPT-5 variant
- **MEDIUM**: `claude-sonnet-4` (Anthropic) - Best balance, 72.7% SWE-bench score
- **BIG**: `gpt-5` (OpenAI) - 400K context, reasoning_effort & verbosity controls

### Backup Models

- **Fast Backup**: `gpt-4o-mini-2024-07-18` (proven stable)
- **Medium Backup**: `claude-opus-4` (most powerful Anthropic model)
- **Big Backup**: `gpt-5`

## ✨ October 2025 Features Enabled

### GPT-5 (Released August 2025)

✅ **400,000 token context** (vs 128K in GPT-4o)
✅ **reasoning_effort**: minimal, low, medium (default), high
✅ **verbosity**: low, medium (default), high
✅ **$1.25/1M input tokens** (90% cache discount)
✅ **$10/1M output tokens**
✅ **74.9% SWE-bench Verified**, 88% Aider polyglot

### Claude 4 (Released May 2025)

✅ **Sonnet 4**: 72.7% SWE-bench, 65% fewer shortcut errors
✅ **Opus 4**: Most powerful for complex reasoning & coding
✅ **Extended thinking**: Native API support with budget_tokens (1K-128K)
✅ **Interleaved thinking**: Thinking between tool calls

### Anthropic Prompt Caching

✅ **Up to 90% cost savings** on repeated calls
✅ **Automatic cache management** - no manual tracking needed
✅ **Works with**: System prompts, tools, examples
✅ **5-minute TTL** (default) or 1-hour cache

## 🔧 Configuration Options

All configurable in `mythos/config/settings.py`:

```python
# Current Production Setup
FAST_MODEL = ("openai", "gpt-5-mini")
MEDIUM_MODEL = ("anthropic", "claude-sonnet-4")
BIG_MODEL = ("openai", "gpt-5")

# Features
ENABLE_PROMPT_CACHING = True              # 90% cost savings
DEFAULT_THINKING_BUDGET = 4000            # Claude 4 thinking tokens
ENABLE_INTERLEAVED_THINKING = True        # Thinking between tool calls
DEFAULT_REASONING_EFFORT = "medium"       # GPT-5 reasoning depth
DEFAULT_VERBOSITY = "medium"              # GPT-5 answer length
```

## 📊 Performance Improvements

| Feature           | Impact                            |
| ----------------- | --------------------------------- |
| Prompt Caching    | Up to 90% cost reduction          |
| GPT-5 Context     | 3x larger (400K vs 128K)          |
| Claude Sonnet 4   | 72.7% SWE-bench (best in class)   |
| Extended Thinking | Better reasoning on complex tasks |
| GPT-5 Reasoning   | Configurable depth vs speed       |

## 🎯 Migration Notes

### Breaking Changes

None! Backward compatible with all existing code.

### Recommended Actions

1. Test GPT-5 with your workload (`reasoning_effort: high` for complex tasks)
2. Enable prompt caching (already on by default)
3. Try Claude Sonnet 4 for coding tasks (best SWE-bench score)
4. Use extended thinking for multi-step reasoning

### Cost Optimization Tips

- Use `gpt-5-mini` for fast/cheap tier (cost-optimized config)
- Enable prompt caching (saves 90% on system prompts)
- Use `reasoning_effort: minimal` for simple tasks
- Cache tool definitions and examples

## 🔗 References

- [GPT-5 API Docs](https://platform.openai.com/docs/models/gpt-5)
- [Claude 4 Release](https://www.anthropic.com/news/claude-4)
- [Prompt Caching Guide](https://docs.claude.com/en/docs/build-with-claude/prompt-caching)
