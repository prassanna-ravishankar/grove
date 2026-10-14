"""Fourth experiment: usage labels from the orchestrator's own transcript.

A memory is "used" on a turn when its file name, or a [[wikilink]] to it,
appears in what the orchestrator did in response: tool inputs, visible text
and thinking, from the inbound message to the next one. These labels do not
come from the Opus labeller, so re-scoring against them tests whether the
cascade result was agreement with use or agreement with the labeller.
"""

import html
import json
import re
from collections import Counter
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from anthropic.types import MessageParam, TextBlockParam

from grove.cascade import READ, READERS, doc_keys, index, norm
from grove.corpus import Doc
from grove.evaluate import PRIMARY, REPO, Setup, rate, sign_test, table
from grove.frontier import PRICE, client
from grove.io import read_jsonl, write_jsonl

TRANSCRIPTS = Path.home() / ".claude" / "projects" / "-Users-prass--repowire-orchestrator"
EDIT_TOOLS = {"Edit", "MultiEdit", "NotebookEdit"}
# Shell commands that rewrite a file they name: append, tee, in-place sed, Python writes.
EDIT_RE = re.compile(r">>|\btee\b|sed -i|\.write\(|write_text\(|open\([^)]*['\"][wa]")
SOURCES = ("read", "edited", "created", "text", "thinking")
METHODS = ("baseline", "recorded", "haiku", "sonnet", "baseline/project/sonnet", "baseline/sender/sonnet")
LABEL_FREE = "sender project differs (no label)"
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")


def squash(text: str) -> str:
    return re.sub(r"\W+", "", html.unescape(text))


def epoch(ts: str) -> float:
    return datetime.fromisoformat(ts).timestamp()


def inbound(rows: list[dict]) -> Iterator[tuple[int, str, str]]:
    """(row index, timestamp, text) for every message the orchestrator received: prompts and messages queued mid-turn."""
    for i, r in enumerate(rows):
        if r.get("isSidechain"):
            continue
        if r["type"] == "user":
            content = r["message"]["content"]
            if isinstance(content, str):
                yield i, r["timestamp"], content
            elif not any(b.get("type") == "tool_result" for b in content):
                yield i, r["timestamp"], " ".join(b.get("text", "") for b in content)
        elif r["type"] == "attachment" and r["attachment"].get("type") == "queued_command":
            yield i, r["timestamp"], str(r["attachment"].get("prompt"))


class Finder:
    """Memory file names and wikilinks in a piece of text."""

    def __init__(self, docs: list[Doc]):
        names = {d.label: re.escape(d.label.removeprefix("memory/")) for d in docs}
        self.names = {label: re.compile(rf"(?<![\w.-]){n}") for label, n in names.items()}
        self.created = {label: re.compile(rf"(?<!>)>(?!>)\s*\S*{n}") for label, n in names.items()}
        self.slugs = {k: d.label for d in docs for k in doc_keys(d) if k}

    def find(self, text: str) -> set[str]:
        found = {label for label, rx in self.names.items() if rx.search(text)}
        return found | {self.slugs[k] for k in map(norm, WIKILINK_RE.findall(text)) if k in self.slugs}

    def bash(self, command: str) -> tuple[set[str], set[str], set[str]]:
        """(read, edited, created) for one shell command."""
        found = self.find(command)
        created = {label for label in found if self.created[label].search(command)}
        edited = found - created if EDIT_RE.search(command) else set()
        return found - created - edited, edited, created


def mentions(finder: Finder, rows: list[dict]) -> dict[str, set[str]]:
    """Memories named in assistant blocks, by source. Tool inputs split into read, edited and created."""
    out: dict[str, set[str]] = {source: set() for source in SOURCES}
    for r in rows:
        if r["type"] != "assistant" or r.get("isSidechain"):
            continue
        for b in r["message"]["content"]:
            if b["type"] == "tool_use":
                found = finder.find(json.dumps(b["input"], ensure_ascii=False))
                if b["name"] == "Write":
                    out["created"] |= found
                elif b["name"] in EDIT_TOOLS:
                    out["edited"] |= found
                elif b["name"] == "Bash":
                    read, edited, created = finder.bash(str(b["input"].get("command", "")))
                    out["read"] |= read
                    out["edited"] |= edited
                    out["created"] |= created
                else:
                    out["read"] |= found
            elif b["type"] == "text":
                out["text"] |= finder.find(b["text"])
            elif b["type"] == "thinking":
                out["thinking"] |= finder.find(b.get("thinking", ""))
    return out


def extract_usage() -> None:
    """Used memories per turn from the orchestrator transcript -> data/usage.jsonl."""
    s = Setup.load()
    (session,) = {t["session"] for t in s.turns}
    rows = [json.loads(line) for line in (TRANSCRIPTS / f"{session}.jsonl").open()]
    events = [(i, ts, squash(text)) for i, ts, text in inbound(rows)]
    starts = [i for i, _, _ in events]
    finder = Finder(s.docs)
    out, taken = [], set()
    for t in s.turns:
        key = squash(t["body"])[:150]
        gap, start = min((abs(epoch(ts) - epoch(t["ts"])), i) for i, ts, text in events if key in text)
        assert start not in taken, f"two turns match transcript row {start}"
        taken.add(start)
        end = next((i for i in starts if i > start), len(rows))
        by_source = mentions(finder, rows[start + 1 : end])
        out.append({"id": t["id"], "row": start, "gap_s": round(gap, 1), "rows": end - start - 1, **{k: sorted(v) for k, v in by_source.items()}})
    write_jsonl("usage.jsonl", out)
    print(f"{len(out)} turns, {sum(bool(set().union(*(r[k] for k in SOURCES)) - set(r['created'])) for r in out)} with a used memory")


def token_costs(s: Setup) -> dict[str, dict]:
    """Per reader: index tokens, mean message tokens (count_tokens, no generation), and output tokens implied by the logged spend."""
    c = client()
    listing = index(s.docs)
    spend = read_jsonl("frontier_spend.jsonl")
    out = {}
    for name, model in READERS.items():
        system: list[TextBlockParam] = [{"type": "text", "text": READ + listing}]
        probe: list[MessageParam] = [{"role": "user", "content": "x"}]
        base = c.messages.count_tokens(model=model, system=system, messages=probe).input_tokens
        bare = c.messages.count_tokens(model=model, messages=probe).input_tokens

        def count(t: dict, model: str = model) -> int:
            content = f"Message from {t['sender']} to {t['target']}:\n<message>\n{t['body'][:6000]}\n</message>"
            message: MessageParam = {"role": "user", "content": content}
            return c.messages.count_tokens(model=model, messages=[message]).input_tokens

        with ThreadPoolExecutor(4) as pool:
            messages = list(pool.map(count, s.turns))
        price = PRICE[model]
        index_tokens, message_tokens = base - bare, sum(messages) / len(messages)
        runs = [r for r in spend if r.get("model") == model and r["tag"] == f"read {name}"]
        usd, n = sum(r["usd"] for r in runs), sum(r["requests"] for r in runs)
        # Every run sends its first request alone (cache write) and the rest read the cache.
        input_usd = len(runs) * index_tokens * price["cache_write"] + (n - len(runs)) * index_tokens * price["cache_read"] + n * message_tokens * price["input"]
        output_tokens = max(0.0, (usd - input_usd) / price["output"] / n)
        warm = index_tokens * price["cache_read"] + message_tokens * price["input"] + output_tokens * price["output"]
        cold = index_tokens * price["input"] + message_tokens * price["input"] + output_tokens * price["output"]
        out[name] = {"model": model, "index": index_tokens, "message": message_tokens, "output": output_tokens, "warm": warm, "cold": cold, "logged": usd / n}
    return out


def reading(cov: list[list], by_source: Counter, agree: list[list], head: dict, vs_recorded: list[list]) -> str:
    pv = "usage, topical (primary)"

    def h(group: str, m: str) -> str:
        r = head[(pv, group, m)]
        return f"{r[6]} vs {r[5]}, {r[7]}, p = {r[8]}"

    named = sum(by_source[src] for src in ("read", "edited", "text", "thinking"))
    return " ".join(
        [
            "Reading. The usage signal does not confirm the cascade result, and on the turns it covers it leans the other way.",
            f"Only {cov[0][1]} turns leave a memory file name behind, {cov[0][3]} of them switches, so it cannot answer the switch question.",
            f"On those turns the baseline is ahead of Sonnet ({h('overall', 'sonnet')}) and of the sender cascade ({h('overall', 'baseline/sender/sonnet')}), and well ahead of Haiku ({h('overall', 'haiku')}).",
            "The project cascade ties exactly: its trigger does not fire on any covered turn where Sonnet and the baseline differ.",
            f"What `used` measures here: of the {named} mentions that are not file creations, {by_source['edited']} are edits (the orchestrator appending a recurrence or a status line), {by_source['read']} are reads by name, {by_source['text']} are names in visible text, and thinking is not recorded.",
            "So `used` mostly means `updated in response to the turn`.",
            f"It is also biased towards whatever recall showed: {agree[0][6]} of used memories were in the recall block the orchestrator saw, against {agree[0][7]} of the Opus-labelled memories on the same turns.",
            f"The baseline's lead is not corpus leakage: `recorded`, computed before any edit, scores {head[(pv, 'overall', 'recorded')][6]} and still leads Sonnet ({vs_recorded[0][4]}, p = {vs_recorded[0][5]}).",
            f"Agreement between usage and the Opus topical labels is low: mean Jaccard {agree[0][2]}, {agree[0][5]} of used memories labelled, usage a subset of the labelled set on {agree[0][3]} of turns.",
            "So the third experiment's margin was agreement with the labeller, not measurably agreement with use. Because usage is selected by the recall block, low agreement does not show the labels are wrong either.",
            "Neither label set is ground truth. Settling it needs an arm the orchestrator is actually shown, for example the reader's top 3 placed beside the recall block on a share of turns with what it then reads logged, or human labels on a sample.",
        ]
    )


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a | b else 1.0


def evaluate_usage() -> None:
    s = Setup.load()
    usage = {r["id"]: r for r in read_jsonl("usage.jsonl")}
    cascade = {r["id"]: r for r in read_jsonl("per_turn_cascade.jsonl")}
    mentioned = {k: set().union(*(r[src] for src in SOURCES)) for k, r in usage.items()}
    existing = {k: v - set(usage[k]["created"]) for k, v in mentioned.items()}
    views = {
        "usage, topical (primary)": {k: v - s.format_25 for k, v in existing.items()},
        "usage, all": existing,
        "usage, topical, as briefed": {k: v - s.format_25 for k, v in mentioned.items()},
        "usage, topical, reads only": {k: v - set(usage[k]["edited"]) - s.format_25 for k, v in existing.items()},
    }
    order = [t["id"] for t in s.turns]
    flags = {name: dict(zip(order, f)) for name, f in s.flags.items()}

    def hit(view: str, tid: str, m: str) -> bool:
        return bool(set(cascade[tid]["recall"][m][:3]) & views[view][tid])

    def groups(view: str, switch_def: str) -> dict[str, list[str]]:
        scored = [k for k in order if views[view][k]]
        return {"overall": scored, "continuation": [k for k in scored if flags[switch_def][k] is False], "switch": [k for k in scored if flags[switch_def][k]]}

    out = s.intro([cascade[k] for k in order], "grove fourth experiment: usage labels")
    gaps = sorted(r["gap_s"] for r in usage.values())
    thinking = sum(bool(r["thinking"]) for r in usage.values())
    out += [
        (
            "Question: the cascade result (results-cascade.md) was measured against labels from claude-opus-5-5 reading the memory index. "
            "Does it hold against what the orchestrator actually used, and how far did the Opus labels agree with use?"
        ),
        "",
        (
            "Usage labels. All 170 turns are in one orchestrator session. Each turn was matched to its inbound message in the session transcript by its text "
            f"(170/170 matched, each to a distinct message; journal-to-transcript gap median {gaps[len(gaps) // 2]:.0f} s, max {gaps[-1]:.0f} s). "
            "A memory is used on a turn when its file name (memory/*.md, comms.md, projects.md) or a [[wikilink]] to it appears in the assistant's response before the next inbound message, "
            "including messages queued mid-turn: tool inputs (Read paths, Bash commands, Edit and Write targets, heredocs), visible text, and thinking. "
            f"Thinking is mostly not recorded in the transcript: {thinking} turns have a memory named in thinking. "
            "Tool inputs are split by what the call does to the file: `created` (Write, or a single `>` redirection), `edited` (Edit, `>>`, tee, in-place sed, Python writes), otherwise `read`. "
            "The primary view drops memories created during the turn: they did not exist when the turn arrived, so no recall could have returned them (the corpus snapshot is later and holds them, the leakage noted in the first experiment). "
            "`as briefed` keeps them. `reads only` also drops memories edited during the turn, leaving those the orchestrator only looked at or named."
        ),
        "",
        (
            "Two biases to keep in view. The orchestrator saw the recorded recall block, so names it repeats from that block count as used: that favours `recorded` and, through their overlap, the baseline. "
            "And it read memory mostly by grepping the directory or by the recall block itself, so many uses leave no file name behind: coverage is partial, and only turns with at least one used memory are scored. "
            "The always-on filter is the same >25% list as before, taken from the Opus labels."
        ),
        "",
    ]
    intro_end = len(out)

    out += ["## Coverage", ""]
    cov = []
    for view, labels in views.items():
        g = groups(view, PRIMARY)
        cov.append([view, f"{len(g['overall'])}/170", len(g["continuation"]), len(g["switch"]), f"{sum(len(labels[k]) for k in g['overall']) / max(1, len(g['overall'])):.2f}"])
    out += table(["labels", "turns with a used memory", "continuation", "switch", "mean used per scored turn"], cov)
    by_source = Counter(src for r in usage.values() for src in SOURCES for _ in r[src])
    out += ["", "(turn, memory) mentions by source, before any filter (a memory can appear under several): " + ", ".join(f"{src} {by_source[src]}" for src in SOURCES) + ".", ""]

    out += [
        "## Usage against the Opus labels",
        "",
        "Per scored turn (at least one used memory). `in recorded` is the share of memories that were in the recall block the orchestrator saw, for usage and, on the same turns, for the Opus labels.",
        "",
    ]
    agree = []
    for name, (uview, oview) in {"topical": ("usage, topical (primary)", "topical"), "all": ("usage, all", "all")}.items():
        ks = [k for k in order if views[uview][k]]
        u = {k: views[uview][k] for k in ks}
        o = {k: set(s.views[oview][k]) for k in ks}
        used_n = sum(len(u[k]) for k in ks)
        agree.append(
            [
                name,
                len(ks),
                f"{sum(jaccard(u[k], o[k]) for k in ks) / len(ks):.3f}",
                rate([u[k] <= o[k] for k in ks]),
                rate([bool(u[k] & o[k]) for k in ks]),
                f"{sum(len(u[k] & o[k]) for k in ks) / used_n:.3f}",
                f"{sum(len(u[k] & set(cascade[k]['recall']['recorded'])) for k in ks) / used_n:.3f}",
                f"{sum(len(o[k] & set(cascade[k]['recall']['recorded'])) for k in ks) / sum(len(o[k]) for k in ks):.3f}",
            ]
        )
    out += table(["labels", "turns", "mean Jaccard", "usage ⊆ labelled", "any overlap", "used memories labelled", "used memories in recorded", "labelled memories in recorded"], agree)
    out += [""]

    out += ["## hit@3 against usage labels", "", "Per turn, win = method hits and baseline misses. Exact two-sided sign test, ties dropped.", ""]
    hit_rows, paired = [], []
    for view in views:
        for switch_def in (PRIMARY, LABEL_FREE):
            g = groups(view, switch_def)
            for m in METHODS:
                cells = [rate([hit(view, k, m) for k in ks]) for ks in g.values()]
                if switch_def == PRIMARY:
                    hit_rows.append([view, m, *cells])
                for group in ("overall", "switch") if switch_def == PRIMARY else ("switch",):
                    ks = g[group]
                    w = sum(hit(view, k, m) and not hit(view, k, "baseline") for k in ks)
                    lo = sum(hit(view, k, "baseline") and not hit(view, k, m) for k in ks)
                    paired.append([view, switch_def, group, len(ks), m, rate([hit(view, k, "baseline") for k in ks]), rate([hit(view, k, m) for k in ks]), f"{w}-{lo}", f"{sign_test(w, lo):.3g}"])
    out += ["Switch = the primary definition (topical Opus label sets disjoint from the previous turn's); n per view in the coverage table.", ""]
    out += table(["labels", "method", "overall", "continuation", "switch"], hit_rows)
    out += ["", "Paired against the baseline. `sender project differs` is the label-free switch definition, independent of Opus.", ""]
    out += table(["labels", "switch definition", "turns", "n", "method", "baseline hit@3", "method hit@3", "wins-losses", "p"], [r for r in paired if r[4] != "baseline"])
    pv = "usage, topical (primary)"
    vs_recorded = []
    for group, ks in groups(pv, PRIMARY).items():
        w = sum(hit(pv, k, "sonnet") and not hit(pv, k, "recorded") for k in ks)
        lo = sum(hit(pv, k, "recorded") and not hit(pv, k, "sonnet") for k in ks)
        vs_recorded.append([group, len(ks), rate([hit(pv, k, "recorded") for k in ks]), rate([hit(pv, k, "sonnet") for k in ks]), f"{w}-{lo}", f"{sign_test(w, lo):.3g}"])
    out += [
        "",
        "Sonnet against `recorded`, primary usage labels. The recorded block was computed at delivery, before the orchestrator edited anything in response, so it carries none of the corpus leakage the ported baseline has.",
        "",
    ]
    out += table(["turns", "n", "recorded", "sonnet", "wins-losses", "p"], vs_recorded)
    out += [""]

    costs = token_costs(s)
    out += [
        "## Reader cost per turn",
        "",
        (
            "List price. Index and message tokens from count_tokens on the stored requests (no generation); output tokens (including thinking) implied by the logged spend of the 170 reads. "
            "`warm` reads the index from the prompt cache, as in this run; `cold` pays full input price for it. A cascade pays this on the triggered share of turns only; the baseline costs no API call."
        ),
        "",
    ]
    out += table(
        ["reader", "model", "index tokens", "mean message tokens", "mean output tokens", "USD per call, warm", "USD per call, cold", "logged USD per call"],
        [[n, c["model"], f"{c['index']:,}", f"{c['message']:.0f}", f"{c['output']:.0f}", f"{c['warm']:.5f}", f"{c['cold']:.5f}", f"{c['logged']:.5f}"] for n, c in costs.items()],
    )
    shares = {m: sum(cascade[k]["fires"][m] for k in order) / len(order) for m in ("baseline/project/sonnet", "baseline/sender/sonnet")}
    out += ["", "Per turn at the cascade call shares, warm: " + ", ".join(f"`{m}` {p:.3f} x {costs['sonnet']['warm']:.5f} = ${p * costs['sonnet']['warm']:.5f}" for m, p in shares.items()) + ".", ""]

    head = {(r[0], r[2], r[4]): r for r in paired if r[1] == PRIMARY}
    out[intro_end:intro_end] = [
        "## Headline",
        "",
        f"Usage labels (topical) cover {cov[0][1]} turns. Against them, overall: "
        + "; ".join(f"`{m}` {head[(pv, 'overall', m)][6]} vs baseline {head[(pv, 'overall', m)][5]} ({head[(pv, 'overall', m)][7]}, p = {head[(pv, 'overall', m)][8]})" for m in METHODS[1:])
        + ". On switches: "
        + "; ".join(f"`{m}` {head[(pv, 'switch', m)][6]} vs {head[(pv, 'switch', m)][5]} ({head[(pv, 'switch', m)][7]}, p = {head[(pv, 'switch', m)][8]})" for m in METHODS[1:])
        + f". Usage against Opus topical labels: mean Jaccard {agree[0][2]}, usage a subset of the labelled set on {agree[0][3]} of scored turns, {agree[0][5]} of used memories labelled.",
        "",
        reading(cov, by_source, agree, head, vs_recorded),
        "",
    ]
    out += [
        "## Cost of this experiment",
        "",
        "No generation calls: the reads are those stored by the third experiment. count_tokens calls only.",
        "",
    ]
    path = REPO / "results-usage.md"
    path.write_text("\n".join(out))
    print(path)
