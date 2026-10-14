"""Shared scoring for recall methods on labelled turns, and the first experiment's results.md."""

import itertools
import json
import re
import sqlite3
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from math import comb
from pathlib import Path
from typing import Any

from grove.baseline import Hit, rank, score, top, turn_tokens
from grove.corpus import Doc, load_corpus
from grove.forest import FACETS, candidate_stats, path, select
from grove.frontier import MODEL
from grove.io import DATA, read_jsonl, write_jsonl

REPO = Path(__file__).resolve().parents[2]
K = 3
DEPTHS = (1, 2, 3)
ALWAYS_ON = 0.25  # a memory labelled useful on more than this share of turns is format, not topic
ALWAYS_ON_LOOSE = 0.15
PRIMARY = "disjoint, topical (primary)"
VIEWS = ("topical", "all")
# Low-confidence reasons that say the referent is unclear or no memory covers it.
UNCOVERED_RE = re.compile(
    r"no memory|none of the memories|cover[s]? (it|that|dbos)|nothing in the index|no (clear )?(matching )?project (memory|context)|no clear|unclear|isn't visible|without the prior context|no prior context|referent",
    re.IGNORECASE,
)

Row = dict[str, Any]


def sign_test(wins: int, losses: int) -> float:
    """Exact two-sided binomial sign test, ties dropped."""
    n = wins + losses
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(comb(n, k) for k in range(min(wins, losses) + 1)) / 2**n)


def epoch(ts: str) -> float:
    return datetime.fromisoformat(ts).timestamp()


def sender_project(name: str) -> str:
    """repowire.route-x-claude-code -> repowire; torale-codex -> torale."""
    return re.sub(r"(-\d+)?-(claude-code|codex|pi|opencode)$", "", name.split(".")[0])


def always_on(labels: dict[str, list[str]], share: float) -> set[str]:
    counts = Counter(u for us in labels.values() for u in us)
    return {u for u, n in counts.items() if n > share * len(labels)}


def table(header: list[str], rows: list[list]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
    return out + ["| " + " | ".join(str(c) for c in row) + " |" for row in rows]


def rate(xs: list[bool]) -> str:
    return f"{sum(xs) / len(xs):.3f}" if xs else "n/a"


@dataclass
class Setup:
    """Corpus, turns, label views and switch flags shared by every experiment."""

    docs: list[Doc]
    turns: list[Row]
    labels: dict[str, Row]
    views: dict[str, dict[str, list[str]]]
    format_25: set[str]
    format_15: set[str]
    flags: dict[str, list[bool | None]]

    @classmethod
    def load(cls) -> "Setup":
        turns = read_jsonl("turns.jsonl")
        labels = {r["id"]: r for r in read_jsonl("labels.jsonl")}
        full = {k: v["useful"] for k, v in labels.items()}
        format_25, format_15 = always_on(full, ALWAYS_ON), always_on(full, ALWAYS_ON_LOOSE)
        views = {
            "all": full,
            "topical": {k: [u for u in us if u not in format_25] for k, us in full.items()},
            "topical15": {k: [u for u in us if u not in format_15] for k, us in full.items()},
        }
        return cls(load_corpus(), turns, labels, views, format_25, format_15, switches(turns, views))

    def hits(self, turn: Row) -> list[Hit]:
        """Every memory the baseline scores for this turn."""
        tokens = turn_tokens(turn)
        return [h for h in (score(tokens, d) for d in self.docs) if h]

    def rows(self, recall: Callable[[Row, list[Hit]], dict[str, list[str]]]) -> list[Row]:
        """One row per turn; recall(turn, baseline_hits) adds the experiment's methods."""
        rows = []
        for i, t in enumerate(self.turns):
            hits = self.hits(t)
            methods = {"recorded": t["recorded"], "baseline": [h.label for h in top(hits)], **recall(t, hits)}
            useful = {v: self.views[v][t["id"]] for v in VIEWS}
            rows.append(
                {
                    "id": t["id"],
                    "ts": t["ts"],
                    "sender": t["sender"],
                    "confidence": self.labels[t["id"]]["confidence"],
                    "useful": useful,
                    "recall": methods,
                    "switch": {name: f[i] for name, f in self.flags.items()},
                    "hit": {v: {m: bool(set(r[:K]) & set(useful[v])) for m, r in methods.items()} for v in VIEWS},
                }
            )
        return rows

    def intro(self, rows: list[Row], title: str) -> list[str]:
        full = self.views["all"]
        low = [self.labels[r["id"]] for r in rows if r["confidence"] == "low"]
        uncovered = sum(bool(UNCOVERED_RE.search(lab["reason"])) for lab in low)
        return [
            f"# {title}",
            "",
            (
                f"{len(rows)} inbound orchestrator turns (2026-10-06 to 2026-10-14: every delivered message in the 14-day window that carried a recall block), {len(self.docs)} memory files. "
                f"Labels: first pass by claude-opus-5-5 from the turn and the memory index; {len(low)} of {len(rows)} rows are marked low confidence. "
                "The orchestrator spot-checked 30 rows (20 low, 10 high confidence): 26 agree, 4 disagree, all four in the low-confidence pool."
            ),
            "",
            f"Coverage, not recall: {uncovered} of the {len(low)} low-confidence rows give as their reason that the referent is unclear or that no memory covers it (keyword match on the labeller's reason). Three of the four spot-check disagreements were of this kind.",
            "",
            f"Always-on memories: labelled useful on more than {ALWAYS_ON:.0%} of turns, treated as format rather than topic: "
            + ", ".join(f"`{u}` ({sum(u in us for us in full.values())})" for u in sorted(self.format_25))
            + f". At {ALWAYS_ON_LOOSE:.0%} the list grows to {len(self.format_15)}. `topical` labels drop the {ALWAYS_ON:.0%} list; {sum(not v for v in self.views['topical'].values())} turns are left with no topical memory and are excluded from topical hit rates.",
            "",
        ]


def switches(turns: list[Row], views: dict[str, dict[str, list[str]]]) -> dict[str, list[bool | None]]:
    """Per turn, whether it switches under each definition; None for the first turn."""
    defs: dict[str, Callable[[Row, Row], bool]] = {
        PRIMARY: lambda a, b: not set(views["topical"][a["id"]]) & set(views["topical"][b["id"]]),
        "disjoint, all labels": lambda a, b: not set(views["all"][a["id"]]) & set(views["all"][b["id"]]),
        "disjoint, topical at 15%": lambda a, b: not set(views["topical15"][a["id"]]) & set(views["topical15"][b["id"]]),
        "top-1 differs, topical": lambda a, b: views["topical"][a["id"]][:1] != views["topical"][b["id"]][:1],
        "set differs, all labels": lambda a, b: set(views["all"][a["id"]]) != set(views["all"][b["id"]]),
        "sender project differs (no label)": lambda a, b: sender_project(a["sender"]) != sender_project(b["sender"]),
    }
    return {name: [None] + [f(cur, prev) for prev, cur in itertools.pairwise(turns)] for name, f in defs.items()}


def split(rows: list[Row], name: str, view: str) -> dict[str, list[Row]]:
    scored = [r for r in rows if r["useful"][view]]
    return {"overall": scored, "continuation": [r for r in scored if r["switch"][name] is False], "switch": [r for r in scored if r["switch"][name]]}


def compare(name: str, view: str, group: str, rs: list[Row], method: str) -> list:
    """One paired row: method against baseline on the same turns."""
    w = sum(r["hit"][view][method] and not r["hit"][view]["baseline"] for r in rs)
    lo = sum(r["hit"][view]["baseline"] and not r["hit"][view][method] for r in rs)
    return [name, view, group, len(rs), method, rate([r["hit"][view]["baseline"] for r in rs]), rate([r["hit"][view][method] for r in rs]), f"{w}-{lo}", f"{sign_test(w, lo):.3g}"]


def hit_section(rows: list[Row], methods: list[str], note: str) -> list[str]:
    out = ["## hit@3", ""]
    for view, title in [("topical", "Topical labels (primary)"), ("all", "All labels")]:
        groups = split(rows, PRIMARY, view)
        out += [
            f"{title}, switch = topical useful set shares nothing with the previous turn's (n: overall {len(groups['overall'])}, continuation {len(groups['continuation'])}, switch {len(groups['switch'])}):",
            "",
        ]
        out += table(["method", "overall", "continuation", "switch"], [[m, *(rate([r["hit"][view][m] for r in g]) for g in groups.values())] for m in methods])
        out += [""]
    high = [r for r in rows if r["confidence"] == "high" and r["useful"]["topical"]]
    out += [f"High-confidence rows only, topical labels ({len(high)} turns): " + ", ".join(f"{m} {rate([r['hit']['topical'][m] for r in high])}" for m in methods), ""]
    returned = {m: sum(len(r["recall"][m][:K]) for r in rows) / len(rows) for m in methods}
    return out + [f"Mean memories returned per turn ({note}): " + ", ".join(f"{m} {v:.2f}" for m, v in returned.items()), ""]


def paired_section(rows: list[Row], methods: list[str], sensitivity: list[str], flags: dict) -> list[str]:
    out = ["## Paired comparison against baseline", "", "Per turn, win = method hits and baseline misses. Exact two-sided sign test, ties dropped.", ""]
    paired = [compare(PRIMARY, view, group, rs, m) for view in VIEWS for group, rs in split(rows, PRIMARY, view).items() for m in methods]
    paired += [compare(name, "topical", group, split(rows, name, "topical")[group], m) for name in flags if name != PRIMARY for group in ("continuation", "switch") for m in sensitivity]
    out += table(["switch definition", "labels", "turns", "n", "method", "baseline hit@3", "method hit@3", "wins-losses", "p"], paired)
    return out + [
        "",
        f"Sensitivity rows (below the primary block) compare {', '.join(sensitivity)} only. `sender project differs` uses no label: it is the only switch signal a deployed index could act on.",
        "",
    ]


def agreement(pairs: list[tuple[str, str]], memory_keys: list[str]) -> tuple[float, float]:
    """Observed share of (turn key, memory key) matches, and the share expected for a random memory."""
    observed = sum(a == b for a, b in pairs) / len(pairs)
    chance = sum(sum(m == a for m in memory_keys) / len(memory_keys) for a, _ in pairs) / len(pairs)
    return observed, chance


def cost_section(note: str) -> list[str]:
    calls = read_jsonl("jev_calls.jsonl")
    by_tag = Counter[str]()
    for r in calls:
        by_tag[r["tag"]] += r["input_tokens"]
    jev_tokens = sum(by_tag.values())
    frontier = read_jsonl("frontier_spend.jsonl")
    out = ["## Cost", "", "Cumulative across all experiments.", ""]
    out += table(
        ["item", "usage", "USD"],
        [
            *[[f"Jev: {tag}", f"{n:,} input tokens", f"{n * 1.21 / 28.8e6:.3f}"] for tag, n in by_tag.items()],
            ["Jev total", f"{jev_tokens:,} input tokens", f"{jev_tokens * 1.21 / 28.8e6:.3f}"],
            *[[f"{r.get('model', MODEL)}: {r['tag']}", f"{r['requests']} requests", f"{r['usd']:.3f}"] for r in frontier],
            ["frontier total", "", f"{sum(r['usd'] for r in frontier):.3f}"],
        ],
    )
    return out + ["", f"Jev USD is estimated at the router paper's rate ($1.21 per 28.8M input tokens). {note}", ""]


def evaluate() -> None:
    """First experiment: binary tree, hard restriction to the turn's path."""
    s = Setup.load()
    candidates = json.loads((DATA / "candidates.json").read_text())
    routes = read_jsonl("routes.jsonl")
    p = {r["id"]: r["p"] for r in routes}
    stats = candidate_stats(candidates, routes)
    tree = select(candidates, stats)
    mem_path = {d.label: path(p[d.label], tree) for d in s.docs}
    turn_path = {t["id"]: path(p[t["id"]], tree) for t in s.turns}

    def recall(t: Row, hits: list[Hit]) -> dict[str, list[str]]:
        tp = turn_path[t["id"]]
        return {f"forest-d{d}": [h.label for h in top([h for h in hits if mem_path[h.label][:d] == tp[:d]])] for d in DEPTHS}

    rows = s.rows(recall)
    for row in rows:
        row["path"] = turn_path[row["id"]]
    write_jsonl("per_turn.jsonl", rows)
    methods = ["recorded", "baseline", *(f"forest-d{d}" for d in DEPTHS)]

    out = s.intro(rows, "grove first experiment: results")
    out += [
        (
            "Methods: `recorded` is the recall block the daemon attached at delivery. `baseline` is the Go scorer ported to Python and run on today's corpus (the corpus the forest and the labeller see). "
            "`forest-dN` is the baseline scorer restricted to memories that share the turn's path to depth N. hit@3 = at least one labelled-useful memory in the top 3."
        ),
        "",
    ]
    intro_end = len(out)
    out += ["## Tree", ""]
    out += table(
        ["depth", "facet", "question", "memories yes", "turns yes", "balance", "decisiveness"],
        [
            [
                i + 1,
                FACETS[i],
                candidates[k]["question"],
                f"{stats[k]['yes_memory']}/{len(s.docs)}",
                f"{stats[k]['yes_turn']}/{len(s.turns)}",
                f"{stats[k]['balance']:.2f}",
                f"{stats[k]['decisive']:.2f}",
            ]
            for i, k in enumerate(tree)
        ],
    )
    leaves, turn_leaves = Counter(mem_path.values()), Counter(turn_path.values())
    out += ["", "Leaves (path: memories / turns): " + ", ".join(f"`{leaf}` {leaves[leaf]} / {turn_leaves[leaf]}" for leaf in sorted(set(leaves) | set(turn_leaves))), ""]
    out += [
        "Candidates proposed by claude-opus-5-5 from a 60-file sample. Selection uses no labels: balance (entropy of the yes share on memories) times decisiveness (mean 2|p-0.5| on turns), best per facet.",
        "",
    ]
    out += table(
        ["key", "facet", "question", "balance", "decisiveness", "score"],
        [[k, q["facet"], q["question"], f"{stats[k]['balance']:.2f}", f"{stats[k]['decisive']:.2f}", f"{stats[k]['score']:.2f}"] for k, q in candidates.items()],
    )

    out += [
        "",
        "## Path agreement by depth",
        "",
        "Over (turn, labelled-useful memory) pairs: the share where the memory's path matches the turn's to depth N. Chance is the agreement expected for a memory drawn at random from the corpus.",
        "",
    ]
    agree_rows = []
    subsets: list[tuple[str, str, Callable[[Row], bool]]] = [
        ("all labels", "all", lambda _: True),
        ("topical labels", "topical", lambda _: True),
        ("topical, high confidence", "topical", lambda r: r["confidence"] == "high"),
        ("topical, switch turns", "topical", lambda r: bool(r["switch"][PRIMARY])),
    ]
    for name, view, keep in subsets:
        for d in DEPTHS:
            pairs = [(r["path"][:d], mem_path[u][:d]) for r in rows if keep(r) for u in r["useful"][view]]
            observed, chance = agreement(pairs, [mp[:d] for mp in mem_path.values()])
            agree_rows.append([name, len(pairs), d, f"{observed:.3f}", f"{chance:.3f}"])
    out += table(["pairs", "n", "depth", "agreement", "chance"], agree_rows)
    out += ["", "Share of turns whose path reaches at least one useful memory at depth N (the ceiling on forest hit@k):", ""]
    out += table(
        ["depth", "all labels", "topical"],
        [[d, *(rate([any(mem_path[u][:d] == r["path"][:d] for u in r["useful"][v]) for r in rows if r["useful"][v]]) for v in ("all", "topical"))] for d in DEPTHS],
    )
    out += [""]
    out += hit_section(rows, methods, "a leaf can hold fewer than 3 scoring memories")
    out += paired_section(rows, ["forest-d1", "forest-d2", "forest-d3", "recorded"], ["forest-d3"], s.flags)

    repeat = read_jsonl("routes_repeat.jsonl")
    same = [path(r["p"], tree) == path(p[r["id"]], tree) for r in repeat]
    delta = [abs(r["p"][k] - p[r["id"]][k]) for r in repeat for k in candidates]
    out += [
        "## Classifier stability",
        "",
        f"{len(repeat)} items (10 memories, 10 turns) routed twice: identical depth-3 path for {sum(same)}/{len(same)}; mean |Δp| across all candidate questions {sum(delta) / len(delta):.3f}.",
        "",
    ]
    out += drift_section(s.turns, s.docs)
    out += cost_section("At index time a memory costs one Jev call; at recall time a turn costs one Jev call with the three chosen questions.")

    groups = split(rows, PRIMARY, "topical")
    head = [compare(PRIMARY, "topical", g, groups[g], "forest-d3") for g in ("overall", "switch")]
    out[intro_end:intro_end] = [
        "## Headline",
        "",
        (
            f"Path agreement for (turn, useful memory) pairs, topical labels: {agree_rows[3][3]} / {agree_rows[4][3]} / {agree_rows[5][3]} at depth 1 / 2 / 3 against chance {agree_rows[3][4]} / {agree_rows[4][4]} / {agree_rows[5][4]}. "
            f"hit@3, topical labels: baseline {head[0][5]} vs forest-d3 {head[0][6]} overall (wins-losses {head[0][7]}, p = {head[0][8]}); on switch turns baseline {head[1][5]} vs forest-d3 {head[1][6]} ({head[1][7]}, p = {head[1][8]}). "
            "The forest agrees with the labels well above chance but not enough: by depth 3 two thirds of useful memories sit off the turn's path, and the token-overlap baseline beats it, most clearly on switches. The depth-1 forest ties the baseline."
        ),
        "",
    ]
    (REPO / "results.md").write_text("\n".join(out))
    print(REPO / "results.md")


def drift_section(turns: list[Row], docs: list[Doc]) -> list[str]:
    """How the port matched the recorded blocks, and how much of the gap is the orchestrator's own later edits."""
    verify = {r["id"]: r for r in read_jsonl("verify.jsonl")}
    conn = sqlite3.connect(f"file:{DATA / 'state.db'}?immutable=1", uri=True)
    (last,) = conn.execute("select max(timestamp) from events where session_id = ?", (turns[-1]["session"],)).fetchone()
    session_end = epoch(last)
    drift = [t for t in turns if verify[t["id"]]["drift"]]
    in_session = 0
    for t in drift:
        involved = {h.label for h in rank(turn_tokens(t), docs)} | set(t["recorded"])
        in_session += any(d.label in involved and epoch(t["ts"]) - 300 < d.mtime <= session_end for d in docs)
    sessions = {t["session"] for t in turns}
    return [
        "## Baseline port and corpus drift",
        "",
        (
            f"The port reproduces the recorded recall block exactly (same files, same order) on {sum(v['exact'] for v in verify.values())} of {len(verify)} turns. "
            f"Each of the other {len(drift)} involves a file modified after the turn, or written within five minutes before it was logged (the daemon computes recall at delivery, before the client logs the turn); none is unexplained. "
            f"The turns span {len(sessions)} orchestrator session(s); in {in_session} of the {len(drift)} drift rows a file involved was edited between five minutes before the turn and the end of that session, that is by the orchestrator while handling the turn or after it."
        ),
        "",
        (
            "Leakage direction: the corpus is today's, so memories the orchestrator wrote in response to a turn are visible to every method and to the labeller. "
            "That helps the baseline and the forest alike wherever both rank the new file, and it inflates hit rates relative to the recorded block, which saw the older corpus."
        ),
        "",
    ]
