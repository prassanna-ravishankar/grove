"""The orchestrator memory corpus, read exactly as Repowire's recall reads it."""

from dataclasses import dataclass
from pathlib import Path

ROOT = Path.home() / ".repowire" / "orchestrator"
MAX_FILE_BYTES = 12000  # daemon.orchestrator_recall.max_file_chars (bytes in Go)


@dataclass(frozen=True)
class Doc:
    label: str  # path relative to ROOT, e.g. "memory/foo.md"
    text: str  # first MAX_FILE_BYTES bytes
    mtime: float


def load_corpus(root: Path = ROOT) -> list[Doc]:
    """comms.md, projects.md, then memory/*.md sorted, MEMORY.md excluded."""
    paths = [root / "comms.md", root / "projects.md"]
    paths += [p for p in sorted(root.glob("memory/*.md")) if p.name != "MEMORY.md"]
    docs = []
    for path in paths:
        if not path.exists():
            continue
        raw = path.read_bytes()[:MAX_FILE_BYTES]
        label = str(path.relative_to(root))
        docs.append(Doc(label, raw.decode("utf-8", errors="replace"), path.stat().st_mtime))
    return docs


def summary(doc: Doc, chars: int = 300) -> str:
    """Frontmatter name and description if present, else the first lines."""
    lines = doc.text.splitlines()
    if lines and lines[0].strip() == "---":
        fields = {}
        for line in lines[1:]:
            if line.strip() == "---":
                break
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
        if fields.get("description"):
            return fields["description"][:chars]
    body = " ".join(line.strip() for line in lines if line.strip() and line.strip() != "---")
    return body[:chars]
