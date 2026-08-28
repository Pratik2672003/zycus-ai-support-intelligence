import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Chunk:
    document: str
    title: str
    text: str


@lru_cache
def _index():
    chunks: list[Chunk] = []
    for path in sorted((ROOT / "knowledge-base").rglob("*.md")):
        raw = path.read_text(encoding="utf-8")
        for part in re.split(r"\n---+\n", raw):
            clean = part.strip()
            if len(clean) < 30:
                continue
            heading = next((line.lstrip("# ").strip() for line in clean.splitlines() if line.startswith("#")), path.stem)
            chunks.append(Chunk(str(path.relative_to(ROOT)), heading, clean))
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    matrix = vectorizer.fit_transform([c.text for c in chunks])
    return chunks, vectorizer, matrix


def retrieve(query: str) -> dict:
    chunks, vectorizer, matrix = _index()
    scores = cosine_similarity(vectorizer.transform([query]), matrix)[0]
    idx = int(scores.argmax())
    score = float(scores[idx])
    chunk = chunks[idx]
    excerpt = re.sub(r"\s+", " ", chunk.text)[:360]
    return {
        "matched": score >= 0.08,
        "document": chunk.document if score >= 0.08 else None,
        "title": chunk.title if score >= 0.08 else None,
        "score": round(min(score * 2.5, 1.0), 3),
        "excerpt": excerpt if score >= 0.08 else None,
    }

