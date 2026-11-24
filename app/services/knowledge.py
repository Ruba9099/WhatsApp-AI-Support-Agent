"""Tiny knowledge base: loads the business's .md/.txt files and finds relevant parts.

Each file is split into paragraphs ("chunks"). For a question we score every chunk
by how many meaningful words it shares with the question and keep the best ones.
This is simple keyword retrieval, good enough for an FAQ of a small business.
Phase 2 on the roadmap swaps it for vector embeddings.
"""
import re
from pathlib import Path

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "be", "to", "of", "and", "or", "in", "on",
    "for", "with", "do", "does", "you", "your", "i", "me", "my", "we", "our", "it",
    "what", "how", "when", "where", "can", "hi", "hello", "please", "there", "this",
    "that", "have", "has", "at", "any", "about",
}

_WORD = re.compile(r"[a-z0-9]+")


def _words(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in STOPWORDS and len(w) > 1}


class KnowledgeBase:
    def __init__(self, chunks: list[str]):
        self.chunks = chunks
        self._index = [_words(c) for c in chunks]

    @classmethod
    def from_directory(cls, directory: str | Path) -> "KnowledgeBase":
        path = Path(directory)
        chunks: list[str] = []
        if path.is_dir():
            for file in sorted(path.glob("*")):
                if file.suffix.lower() in {".md", ".txt"}:
                    text = file.read_text(encoding="utf-8")
                    chunks += [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        return cls(chunks)

    def search(self, question: str, top_k: int = 3) -> list[str]:
        query = _words(question)
        if not query:
            return []
        scored = [
            (len(query & words), i) for i, words in enumerate(self._index) if query & words
        ]
        scored.sort(key=lambda s: (-s[0], s[1]))
        return [self.chunks[i] for _, i in scored[:top_k]]
