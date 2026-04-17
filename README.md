# LangGraph Patterns

**Reusable building blocks for production LangGraph agents.**

Most LangGraph examples are toy demos. This repo is a growing library of **opinionated patterns** for the problems you actually hit when shipping agentic systems — routing, self-correction, human-in-the-loop, graceful degradation.

Each pattern is:
- 🧩 **Self-contained** — copy a folder into your project and it works
- 📐 **Minimal** — no framework sprawl; just LangGraph + a chat model
- 🧠 **Explained** — every pattern has a README covering *when to use*, *tradeoffs*, and a diagram
- 🔁 **Provider-agnostic** — swap between Anthropic, OpenAI, Azure OpenAI with one env var

---

## 🗂 Pattern index

| # | Pattern | Status | What it solves |
|---|---------|--------|----------------|
| 01 | [Router / Supervisor](patterns/router) | ✅ | Classify a request and dispatch to the right specialist subgraph |
| 02 | [Reflect & Retry](patterns/reflect_retry) | ✅ | Loop a draft through a critic until it passes a quality bar |
| 03 | Human-in-the-Loop | 🚧 | Pause for approval; resume with injected feedback |
| 04 | Plan → Execute | 📋 | Decouple planning from execution for auditable reasoning |
| 05 | Map-Reduce (Fan-out / Fan-in) | 📋 | Parallelize independent subtasks and aggregate results |
| 06 | Memory (Short + Long Term) | 📋 | Separate conversation memory from durable knowledge |
| 07 | Tool Guardrails | 📋 | Validate structured tool calls; rollback on failure |
| 08 | Self-Heal | 📋 | Graceful degradation when a tool or model call fails |

Legend: ✅ shipped · 🚧 in progress · 📋 planned

---

## 🚀 Getting started

**Requirements:** Python 3.11+

```bash
git clone https://github.com/SubramonianInian/langgraph-patterns.git
cd langgraph-patterns
pip install -e .
cp .env.example .env   # add your API key
```

**Run a pattern:**

```bash
python -m patterns.router.example
python -m patterns.reflect_retry.example
```

---

## 🔌 Switching model providers

Every pattern uses a shared model factory. Set one env var:

```bash
# Anthropic (default)
LLM_MODEL=anthropic:claude-sonnet-4-5

# OpenAI
LLM_MODEL=openai:gpt-4o

# Azure OpenAI
LLM_MODEL=azure_openai:gpt-4
```

See [`shared/llm.py`](shared/llm.py) for the one-line factory.

---

## 🎯 Design philosophy

1. **A pattern should fit in your head.** If the graph needs more than one diagram, it's two patterns.
2. **State is a contract.** Each pattern declares a `TypedDict` state; nodes read and write to it explicitly. No hidden side effects.
3. **Fail loudly in development, gracefully in production.** Every pattern has a `max_attempts` / timeout / fallback where it matters.
4. **Measurable before clever.** Patterns expose the signals you'd want to log: which node fired, how many retries, why a route was chosen.

---

## 🤝 Contributing

Each pattern lives in its own folder. To add one:

1. Create `patterns/NN-name/` with `README.md`, `graph.py`, `example.py`
2. Follow the structure of an existing pattern
3. Add it to the index table above

---

## 📜 License

MIT — use these patterns however helps you ship.
