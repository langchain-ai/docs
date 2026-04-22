# vecr-compress

[vecr-compress](https://github.com/h2cker/vecr) is an open-source LLM context compressor with a deterministic retention contract. It pins structured tokens — order IDs, dates, URLs, emails, code references — via an auditable regex whitelist before running token-budget packing. Filler phrases are hard-dropped; remaining sentences are ranked by question-aware Jaccard scoring.

## Overview

| Property | Value |
|---|---|
| Package | `langchain-vecr-compress` |
| License | Apache 2.0 |
| Python | 3.10+ |
| Retention contract | Deterministic (regex whitelist, 13 built-in rules) |
| Streaming | No (one-shot, synchronous) |

## Installation

```bash
pip install langchain-vecr-compress
```

## Usage

```python
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_vecr_compress import VecrContextCompressor

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

Add custom retention rules for domain-specific identifiers:

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
