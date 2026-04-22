# vecr-compress

[vecr-compress](https://github.com/h2cker/vecr) is an open-source LLM context compressor with a deterministic retention contract. It pins structured tokens (order IDs, dates, URLs, emails, code references) via an auditable regex whitelist before running token-budget packing. Filler phrases are hard-dropped; remaining sentences are scored by entropy and structural signals (digits, braces, capitalization) and packed greedily into the token budget.

## Overview

| Property | Value |
|---|---|
| Package | `vecr-compress` (install with `[langchain]` extra) |
| Import path | `vecr_compress.adapters.langchain` |
| License | Apache 2.0 |
| Python | 3.10+ |
| Retention contract | Deterministic (regex whitelist, 13 built-in rules) |
| Streaming | No (one-shot, synchronous) |

## Installation

```bash
pip install 'vecr-compress[langchain]'
```

> The older `langchain-vecr-compress` shim package (0.1.0) re-exports this same adapter and is now deprecated in favour of the `[langchain]` extra on the core package. Existing installs keep working; new projects should use the extra.

## Usage

```python
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from vecr_compress.adapters.langchain import VecrContextCompressor

compressor = VecrContextCompressor(budget_tokens=2000)

compressed = compressor.compress_messages([
    SystemMessage(content="You are a refund analyst."),
    HumanMessage(content="Order ORD-99172 placed 2026-03-15. Amount $1,499.00."),
    HumanMessage(content="What is the refund status?"),
])
```

`AIMessage` objects with `tool_calls` are preserved verbatim and round-trip intact.

## Advanced usage

Access the full compression report for telemetry:

```python
result = compressor.compress_with_report(messages)
print(f"Ratio: {result.ratio:.1%}, pinned facts: {len(result.retained_matches)}")
```

### Opt-in question-aware scoring (v0.1.3+)

For natural-language QA workloads (long prose contexts, real user questions), enable `use_question_relevance=True` to blend Jaccard question overlap into the default heuristic scorer. On the HotpotQA dev probe (N=100, distractor split) this lifts supporting-fact survival at ratio 0.5 by **+9.9 percentage points** (58.0% → 67.9%). Off by default so the deterministic retention contract stays the loud promise. See [BENCHMARK.md](https://github.com/h2cker/vecr/blob/main/docs/BENCHMARK.md#hotpotqa-spike--where-the-synthetic-bench-hits-its-ceiling) for methodology.

```python
compressor = VecrContextCompressor(
    budget_tokens=2000,
    use_question_relevance=True,
)
```

The last `HumanMessage` is auto-picked as the question; override with the `question=` kwarg on `compress_messages()` if needed.

### Custom retention rules

```python
import re
from vecr_compress import RetentionRule, DEFAULT_RULES

rules = DEFAULT_RULES.with_extra([
    RetentionRule(name="ticket", pattern=re.compile(r"\bTICKET-\d{4,8}\b")),
])
compressor = VecrContextCompressor(budget_tokens=2000, retention_rules=rules)
```

## API reference

See the [vecr-compress GitHub repo](https://github.com/h2cker/vecr) for full API docs, the retention contract specification ([RETENTION.md](https://github.com/h2cker/vecr/blob/main/RETENTION.md)), and changelog.
