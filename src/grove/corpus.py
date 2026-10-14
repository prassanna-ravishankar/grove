"""The orchestrator memory corpus, read exactly as Repowire's recall reads it."""

import shutil
from dataclasses import dataclass
from pathlib import Path

ROOT = Path.home() / ".repowire" / "orchestrator"
SNAPSHOT = Path(__file__).resolve().parents[2] / "data" / "corpus"
MAX_FILE_BYTES = 12000  # daemon.orchestrator_recall.max_file_chars (bytes in Go)


@dataclass(frozen=True)
class Doc:
    label: str  # path relative to ROOT, e.g. "memory/foo.md"
    text: str  # first MAX_FILE_BYTES bytes
    mtime: float


def corpus_paths(root: Path) -> list[Path]:
    """comms.md, projects.md, then memory/*.md sorted, MEMORY.md excluded."""
    return [root / "comms.md", root / "projects.md"] + [p for p in sorted(root.glob("memory/*.md")) if p.name != "MEMORY.md"]


def snapshot() -> None:
    """Freeze the live corpus under data/corpus, keeping modification times."""
    for path in corpus_paths(ROOT):
        target = SNAPSHOT / path.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    print(f"{len(corpus_paths(SNAPSHOT))} files -> {SNAPSHOT}")


def load_corpus(root: Path | None = None) -> list[Doc]:
    """The snapshot when one exists, else the live directory."""
    root = root or (SNAPSHOT if SNAPSHOT.exists() else ROOT)
    paths = corpus_paths(root)
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
