"""Reflection memory — learn from past pipeline runs.

Inspired by TradingAgents' FinancialSituationMemory with BM25 retrieval.
Stores per-agent reflections in SQLite and retrieves relevant past experiences
to inject as context for future runs.

Architecture:
  ┌─────────────┐
  │  SQLite DB   │ ← stores reflections per agent
  └──────┬──────┘
         │ query(agent_id, text)
  ┌──────▼──────┐
  │  BM25 Rank  │ ← ranks by relevance using term frequency
  └──────┬──────┘
         │ top-K most relevant
  ┌──────▼──────┐
  │  Agent ctx  │ ← injected as "past experience" context
  └─────────────┘
"""

from __future__ import annotations

import math
import re
import sqlite3
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import structlog

logger = structlog.get_logger()

_DB_PATH = Path("data/reflection_memory.db")


@dataclass
class Reflection:
    """A stored reflection from a past pipeline run."""

    id: int
    agent_id: str
    execution_id: str
    content: str
    score: float = 0.0  # BM25 relevance score (set during retrieval)


def _tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation tokenizer for BM25."""
    return re.findall(r"\w+", text.lower())


class ReflectionMemory:
    """Per-agent reflection memory with BM25 retrieval.

    Thread-safe: creates a new SQLite connection per operation.
    """

    def __init__(self, db_path: Path | str = _DB_PATH) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self._db_path))

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reflections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    execution_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_reflections_agent
                ON reflections(agent_id)
            """)

    def store(self, agent_id: str, execution_id: str, content: str) -> None:
        """Store a reflection from a pipeline run."""
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO reflections (agent_id, execution_id, content) VALUES (?, ?, ?)",
                (agent_id, execution_id, content),
            )
        logger.debug("reflection_stored", agent=agent_id, execution=execution_id)

    def retrieve(self, agent_id: str, query: str, top_k: int = 3) -> list[Reflection]:
        """Retrieve top-K most relevant past reflections using BM25 scoring."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, agent_id, execution_id, content FROM reflections WHERE agent_id = ?",
                (agent_id,),
            ).fetchall()

        if not rows:
            return []

        # Build BM25 index over all reflections for this agent
        documents = [
            Reflection(id=r[0], agent_id=r[1], execution_id=r[2], content=r[3])
            for r in rows
        ]
        scored = self._bm25_rank(documents, query, top_k)
        return scored

    def retrieve_formatted(self, agent_id: str, query: str, top_k: int = 3) -> str:
        """Retrieve and format reflections as injectable context."""
        reflections = self.retrieve(agent_id, query, top_k)
        if not reflections:
            return ""

        lines = ["── Past Experience (from similar runs) ──"]
        for i, ref in enumerate(reflections, 1):
            lines.append(f"\n[Experience {i}] (score: {ref.score:.2f})")
            # Truncate long reflections to keep context manageable
            content = ref.content[:1500] + "..." if len(ref.content) > 1500 else ref.content
            lines.append(content)
        return "\n".join(lines)

    def clear(self, agent_id: str | None = None) -> int:
        """Clear reflections. If agent_id given, clear only that agent's."""
        with self._connect() as conn:
            if agent_id:
                cursor = conn.execute(
                    "DELETE FROM reflections WHERE agent_id = ?", (agent_id,),
                )
            else:
                cursor = conn.execute("DELETE FROM reflections")
            return cursor.rowcount

    @staticmethod
    def _bm25_rank(
        documents: list[Reflection],
        query: str,
        top_k: int,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> list[Reflection]:
        """BM25 ranking of documents against query.

        Parameters follow standard BM25 defaults (k1=1.5, b=0.75).
        """
        query_tokens = _tokenize(query)
        if not query_tokens:
            return documents[:top_k]

        # Tokenize all documents
        doc_tokens = [_tokenize(doc.content) for doc in documents]
        doc_lens = [len(dt) for dt in doc_tokens]
        avg_dl = sum(doc_lens) / len(doc_lens) if doc_lens else 1

        # Document frequency for IDF
        n = len(documents)
        df: Counter[str] = Counter()
        for tokens in doc_tokens:
            df.update(set(tokens))

        # Score each document
        for i, doc in enumerate(documents):
            tf = Counter(doc_tokens[i])
            score = 0.0
            for term in query_tokens:
                if term not in tf:
                    continue
                term_freq = tf[term]
                doc_freq = df.get(term, 0)
                idf = math.log((n - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
                numerator = term_freq * (k1 + 1)
                denominator = term_freq + k1 * (1 - b + b * doc_lens[i] / avg_dl)
                score += idf * numerator / denominator
            doc.score = score

        # Sort by score descending, take top-K
        documents.sort(key=lambda d: d.score, reverse=True)
        return documents[:top_k]


# Singleton instance
memory = ReflectionMemory()
