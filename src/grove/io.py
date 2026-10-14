"""JSONL helpers for the local data/ directory (gitignored)."""

import json
from collections.abc import Iterable
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "data"


def write_jsonl(name: str, rows: Iterable[dict]) -> Path:
    path = DATA / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return path


def read_jsonl(name: str) -> list[dict]:
    path = DATA / name
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def append_jsonl(name: str, row: dict) -> None:
    path = DATA / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
