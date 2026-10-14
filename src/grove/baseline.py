"""Port of repowire daemon-go/service/orchestrator_recall.go scoring.

Token overlap over files: per token, occurrences in label+content capped at 4,
plus 2 when the token is in the label; files with no matching line are
dropped; ties break by label; at most MAX_HITS.
"""

import re
from collections.abc import Iterable
from dataclasses import dataclass

from grove.corpus import Doc

TOKEN_RE = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_.@/-]{2,}")
STOP = {"from", "with", "that", "this", "there", "reply", "ack", "ask", "message", "repowire"}
MAX_HITS = 3
SNIPPET_BYTES = 220


@dataclass(frozen=True)
class Hit:
    label: str
    snippet: str
    score: int


def query_tokens(*parts: str) -> set[str]:
    tokens = set()
    for token in TOKEN_RE.findall(" ".join(parts)):
        token = token.strip("._-/@").lower()
        if token and token not in STOP:
            tokens.add(token)
    return tokens


def score(tokens: set[str], doc: Doc) -> Hit | None:
    lower_label = doc.label.lower()
    lower = (doc.label + "\n" + doc.text).lower()
    total = 0
    for token in tokens:
        total += min(lower.count(token), 4)
        if token in lower_label:
            total += 2
    if total == 0:
        return None
    best, best_score = "", 0
    for line in doc.text.split("\n"):
        clean = line.strip()
        line_score = sum(token in clean.lower() for token in tokens)
        if line_score > best_score or (line_score == best_score and line_score > 0 and (best == "" or len(clean.encode()) < len(best.encode()))):
            best, best_score = clean, line_score
    if not best:
        return None
    raw = best.encode()
    if len(raw) > SNIPPET_BYTES:
        best = raw[: SNIPPET_BYTES - 1].decode("utf-8", errors="replace") + "…"
    return Hit(doc.label, best, total)


def rank(tokens: set[str], docs: Iterable[Doc], limit: int | None = MAX_HITS) -> list[Hit]:
    hits = [h for h in (score(tokens, d) for d in docs) if h]
    hits.sort(key=lambda h: (-h.score, h.label))
    return hits[:limit] if limit else hits
