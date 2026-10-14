"""grove experiment steps: python -m grove <step>.

extract  turns from data/state.db (a copy of ~/.repowire/state.db) -> data/turns.jsonl
verify   ported baseline against the recorded recall blocks -> data/verify.jsonl
label    frontier usefulness labels -> data/labels.jsonl
spotcheck 30 labelled turns for a human check -> data/spotcheck.md
propose  frontier split-question candidates -> data/candidates.json
route    Jev answers for every candidate on every memory and turn -> data/routes.jsonl
evaluate select the tree, score both recalls -> data/per_turn.jsonl, results.md
"""

import random
import sys
from dataclasses import asdict
from datetime import datetime

from grove import forest
from grove.baseline import query_tokens, rank
from grove.corpus import load_corpus
from grove.evaluate import evaluate
from grove.frontier import client, run
from grove.io import DATA, read_jsonl, write_jsonl
from grove.label import request
from grove.turns import load_turns

SINCE = "2026-09-30"  # 14 days before 2026-10-14


def baseline_tokens(turn: dict) -> set[str]:
    """The daemon's query: text, sender name and id, target name, id and circle."""
    return query_tokens(turn["body"], turn["sender"], turn["sender_id"], turn["target"], turn["target_id"], "1")


def extract() -> None:
    turns = load_turns(DATA / "state.db", SINCE)
    print(f"{len(turns)} turns -> {write_jsonl('turns.jsonl', map(asdict, turns))}")


def verify() -> None:
    """Exact ordered match, else whether a differing file changed after the turn.

    The recall is computed at delivery; the journal logs the turn when the
    client accepts it, so a file written shortly before the logged time can
    postdate the recall. Modification times are compared with a 5 minute
    allowance for that gap.
    """
    docs = load_corpus()
    rows = []
    for turn in read_jsonl("turns.jsonl"):
        ported = [h.label for h in rank(baseline_tokens(turn), docs)]
        logged = datetime.fromisoformat(turn["ts"]).timestamp()
        changed = {d.label for d in docs if d.mtime > logged - 300}
        differing = set(ported) ^ set(turn["recorded"]) or set(ported)
        exact = ported == turn["recorded"]
        rows.append({"id": turn["id"], "exact": exact, "drift": not exact and bool(differing & changed or set(turn["recorded"]) - {d.label for d in docs})})
    write_jsonl("verify.jsonl", rows)
    exact, drift = sum(r["exact"] for r in rows), sum(r["drift"] for r in rows)
    print(f"exact {exact}/{len(rows)}, corpus drift {drift}, unexplained {len(rows) - exact - drift}")


def label() -> None:
    docs, done = load_corpus(), {r["id"] for r in read_jsonl("labels.jsonl")}
    turns = [t for t in read_jsonl("turns.jsonl") if t["id"] not in done]
    results = run(client(), [request(t, docs) for t in turns], tag="label")
    rows = read_jsonl("labels.jsonl") + [{"id": k, **v} for k, v in results.items() if v]
    write_jsonl("labels.jsonl", rows)


def spotcheck() -> None:
    """30 turns for a human check: 20 low-confidence, 10 high, seed 0."""
    labels = {r["id"]: r for r in read_jsonl("labels.jsonl")}
    turns = read_jsonl("turns.jsonl")
    low = [t for t in turns if labels[t["id"]]["confidence"] == "low"]
    high = [t for t in turns if labels[t["id"]]["confidence"] == "high"]
    rng = random.Random(0)
    sample = sorted(rng.sample(low, 20) + rng.sample(high, 10), key=lambda t: t["ts"])
    lines = ["# grove label spot-check", "", "Mark each row: `verdict: agree` or `verdict: disagree` (optionally which memories are wrong or missing).", ""]
    for n, t in enumerate(sample, 1):
        lab = labels[t["id"]]
        lines += [f"## {n}. {t['ts']} from {t['sender']} ({lab['confidence']} confidence)", f"id: `{t['id']}`", "", "```", t["body"][:4000], "```", ""]
        lines += ["Useful (most useful first):"] + [f"- {u}" for u in lab["useful"]] + ["", f"Reason: {lab['reason']}", "", "verdict: ", ""]
    (DATA / "spotcheck.md").write_text("\n".join(lines))
    print(DATA / "spotcheck.md")


STEPS = {f.__name__: f for f in (extract, verify, label, spotcheck, forest.propose, forest.route, evaluate)}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in STEPS:
        sys.exit(__doc__)
    STEPS[sys.argv[1]]()
