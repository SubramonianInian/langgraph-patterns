"""Minimal in-process long-term memory store.

In production, replace with a vector store (pgvector, Pinecone, Weaviate) or
a structured knowledge store. The interface is deliberately small so swapping
it is trivial.
"""

from collections import defaultdict


class LongTermMemory:
    """A tiny keyword-matching store keyed by user_id.

    Replace with a real retriever when you move past the demo.
    """

    def __init__(self) -> None:
        self._by_user: dict[str, list[str]] = defaultdict(list)

    def write(self, user_id: str, fact: str) -> None:
        fact = fact.strip()
        if fact and fact not in self._by_user[user_id]:
            self._by_user[user_id].append(fact)

    def read(self, user_id: str, query: str, k: int = 5) -> list[str]:
        terms = {t.lower() for t in query.split() if len(t) > 3}
        scored = [
            (sum(1 for t in terms if t in fact.lower()), fact)
            for fact in self._by_user[user_id]
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [fact for score, fact in scored if score > 0][:k]


STORE = LongTermMemory()
