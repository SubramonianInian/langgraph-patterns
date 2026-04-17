"""Runnable demo of the Tool Guardrails pattern.

Usage:
    python -m patterns.tool_guardrails.example
"""

from patterns.tool_guardrails.graph import build_graph


def main() -> None:
    graph = build_graph()
    result = graph.invoke(
        {
            "question": "Who were the top 10 customers by revenue last quarter?",
            "proposed_sql": "",
            "proposed_reason": "",
            "validation_errors": [],
            "attempts": 0,
            "max_attempts": 3,
            "result": "",
        }
    )

    print(f"Attempts: {result['attempts']}\n")
    print(result["result"])


if __name__ == "__main__":
    main()
