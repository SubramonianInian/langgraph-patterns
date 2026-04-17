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
| 03 | [Human-in-the-Loop](patterns/hitl) | ✅ | Pause for approval; resume with injected feedback |
| 04 | [Plan → Execute](patterns/plan_execute) | ✅ | Decouple planning from execution for auditable reasoning |
| 05 | [Map-Reduce (Fan-out / Fan-in)](patterns/map_reduce) | ✅ | Parallelize independent subtasks and aggregate results |
| 06 | [Memory (Short + Long Term)](patterns/memory) | ✅ | Separate conversation memory from durable knowledge |
| 07 | [Tool Guardrails](patterns/tool_guardrails) | ✅ | Validate structured tool calls before they run |
| 08 | [Self-Heal](patterns/self_heal) | ✅ | Graceful degradation when a tool or model call fails |

Legend: ✅ shipped

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
python -m patterns.hitl.example
python -m patterns.plan_execute.example
python -m patterns.map_reduce.example
python -m patterns.memory.example
python -m patterns.tool_guardrails.example
python -m patterns.self_heal.example
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
3. **Prompts live next to code, not inside it.** Every pattern keeps its prompts in `prompts.yml` alongside `graph.py` — editable without Python knowledge, diffable in git, portable when a folder is copied into another project.
4. **Fail loudly in development, gracefully in production.** Every pattern has a `max_attempts` / timeout / fallback where it matters.
5. **Measurable before clever.** Patterns expose the signals you'd want to log: which node fired, how many retries, why a route was chosen.

---

## 🤝 Contributing

Each pattern lives in its own folder. To add one:

1. Create `patterns/NN-name/` with `README.md`, `graph.py`, `example.py`
2. Follow the structure of an existing pattern
3. Add it to the index table above

---

## 📜 License

MIT — use these patterns however helps you ship.
