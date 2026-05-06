# LangSmith Java tracing sample

This folder contains a single-file Java sample you can run with [JBang](https://www.jbang.dev/).

## Prereqs

- Install a JDK (Java 17+ recommended).
  - macOS (Homebrew): `brew install --cask temurin`
- Install JBang.
  - macOS (Homebrew): `brew install jbang`

## Set environment variables

This example calls OpenAI and (optionally) sends traces to LangSmith.

```bash
export OPENAI_API_KEY="..."

# Enable LangSmith tracing
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY="..."

# Optional
export LANGSMITH_PROJECT="java-tracing-sample"
```

## Run

From the repo root:

```bash
jbang src/code-samples/langsmith/TraceablePipeline.java
```

