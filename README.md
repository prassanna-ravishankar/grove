# grove

A memory layer for agents built as a decision forest. Each tree is a sequence of
questions a cheap System-1 classifier answers about a memory when it is written
and about a query when it is recalled; a memory's path through the tree is its
partition, and recall follows the same path. Several trees with different
questions, results unioned, give robustness; the trees stay readable and
editable by a human.

Status: two experiments run, 2026-10-14. [results.md](results.md): on real
orchestrator turns a three-question tree loses to token-overlap recall,
most clearly on topic switches. [results-multiway.md](results-multiway.md):
one project facet, used as a hard filter or a score boost, does not beat it
on switches either, and an Opus reader does no better than Jev. The loss is
the partition structure, not the classifier: apparent wins on unfiltered labels
come from always-on memories landing in small partitions and vanish on topical
labels. Recorded as a negative result; total spend about three dollars.

Third experiment, [results-cascade.md](results-cascade.md): a frontier reader
over the memory index (Sonnet 5.5) beats token overlap by a wide margin on
continuations and switches alike, so a cascade beats the baseline on switches
at any useful call share (project-change trigger: 0.661 vs 0.390 at 27% of
turns) but trades accuracy for calls about linearly. Unlike routing, no cheap
default is right on continuations. The margin is agreement with an Opus
labeller reading a similar index, not yet checked against usage.

Fourth experiment, [results-usage.md](results-usage.md): re-scored against
what the orchestrator did with memory in its transcript, the result does not
hold. Only 33 of 170 turns name a memory, mostly as an edit; on those the
baseline leads Sonnet (0.636 vs 0.485, 4-9, p = 0.27), and usage agrees weakly
with the Opus labels (mean Jaccard 0.14). Usage is itself biased toward the
recall block the orchestrator was shown, so neither label set is ground truth;
an online arm or human labels would settle it.

What would reopen it: memories written to a schema at write time (facets
filled, not inferred from prose), or a usage signal richer than one session's
turns, so that split questions can be learned from where recall actually
switches.

## Thesis

Agent memory is small (hundreds to a few thousand items), schema-less, and
recalled on every turn. The facets that matter at recall time (which project,
which person, what kind of lesson, whether it is still true) are latent in the
text. A classifier that is strong on small structured choices can infer those
facets cheaply at write time, and the resulting tree is an index a person can
read. Because every turn is a query, the forest can be reorganised by usage:
new splits where recall switches topic, retired splits where nothing is asked.

The origin is the Repowire router study (`repowire/paper/latex`), which found
that a small classifier is reliable with a handful of structured candidates and
collapses as the candidate set grows, and that most routing decisions repeat the
previous one, so the decisions worth optimising are the switches.

## What would make it true

1. Path agreement. A memory and the queries that should recall it must take the
   same path. Measure agreement by depth on a fixed probe set.
2. Recall on switches. Against the current Repowire recall (embedding or keyword
   over the memory directory), score forest recall on real orchestrator turns,
   conditioned on whether the turn's topic continues or switches. The claim to
   earn: better recall where the topic changes, at lower cost, with a readable
   tree.
3. Question proposal. The classifier applies splits; it does not invent them. A
   frontier model proposes candidate questions from a sample of memories; keep
   those that split the corpus evenly and that queries can also answer.
4. Drift. The hosted classifier has no version pin. Store each memory's path,
   keep the index rebuildable, re-measure path agreement on the probe set after
   any model change.

## First experiment

- Corpus: the orchestrator's memory directory and MEMORY.md index (about 100
  entries), plus projects.md.
- Queries: the inbound messages of one week of orchestrator turns, with the
  memories that were actually useful marked by hand.
- Baseline: the recall block Repowire attaches to each inbound message today.
- Metric: hit@k per turn, split by continuation versus topic switch, paired
  sign test, same protocol as the router paper.
- Budget: one shallow tree, three facets, one day.

Run it (Python 3.13, uv; reads local data only, writes to the gitignored
`data/`): copy `~/.repowire/state.db` to `data/state.db`, then
`uv run python -m grove <step>` for each of `snapshot extract verify label
spotcheck propose route evaluate`, and for the second experiment
`route_areas read_areas evaluate_areas`, and for the third
`read_cascade evaluate_cascade`, and for the fourth `extract_usage
evaluate_usage` (reads the orchestrator session transcript under
`~/.claude/projects`).

## Non-goals

Not a search engine over large corpora (the classifier collapses there). Not a
graph store. Not a replacement for the files on disk: the forest is an index
over them.

## Related

mem0, Letta, Zep (embedding and graph memory); hierarchical partitioning, LSH
forests, learned indexes (the forest lineage); Repowire router paper (the
evaluation protocol and the switch-conditioned metric).
