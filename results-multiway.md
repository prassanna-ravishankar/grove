# grove second experiment: one multi-way facet, soft routing

170 inbound orchestrator turns (2026-10-06 to 2026-10-14: every delivered message in the 14-day window that carried a recall block), 150 memory files. Labels: first pass by claude-opus-5-5 from the turn and the memory index; 109 of 170 rows are marked low confidence. The orchestrator spot-checked 30 rows (20 low, 10 high confidence): 26 agree, 4 disagree, all four in the low-confidence pool.

Coverage, not recall: 21 of the 109 low-confidence rows give as their reason that the referent is unclear or that no memory covers it (keyword match on the labeller's reason). Three of the four spot-check disagreements were of this kind.

Always-on memories: labelled useful on more than 25% of turns, treated as format rather than topic: `memory/feedback_telegram_message_size.md` (58), `memory/peer_to_peer_review_iteration.md` (48), `memory/routing_refactor_gate.md` (53). At 15% the list grows to 7. `topical` labels drop the 25% list; 0 turns are left with no topical memory and are excluded from topical hit rates.

Methods: `baseline` is the ported Repowire scorer over the whole corpus. `hard-R` keeps only memories in the turn's area. `soft-R-bN` ranks the whole corpus with the baseline score plus N for memories in the turn's area; `soft-R-rP` adds P% of the turn's top baseline score instead (added after the fixed boosts, see the facet section). A boost applies only to memories the baseline already scores; it never adds a zero-overlap memory. R is the reader that assigns the turn's area: `jev`, or `opus` (claude-opus-5-5). Memories are always routed by Jev. hit@3 = at least one labelled-useful memory in the top 3.

The corpus is a snapshot taken at the start of this experiment. It differs from the first experiment's in two files the orchestrator edited after that run, which moves one all-labels forest row there; baseline numbers are unchanged.

## Headline

Agreement at depth 1 (topical labels): Jev-routed turns 0.361, Opus-routed turns 0.345, chance 0.231. Soft routing on switch turns, topical labels (best boost chosen on this table, so p is optimistic): soft-jev-b1 0.390 vs baseline 0.390 (wins-losses 0-0, p = 1). Hard routing on switch turns: hard-jev 0.356 vs 0.390 (6-8, p = 0.791); hard-opus 0.407 vs 0.390 (6-5, p = 1). Opus-routed vs Jev-routed turns on switches, by boost: b1 0.373 vs 0.390 (0-1, p = 1); b2 0.373 vs 0.390 (0-1, p = 1); b4 0.373 vs 0.356 (1-0, p = 1); r10 0.373 vs 0.390 (0-1, p = 1); r25 0.356 vs 0.356 (1-1, p = 1); r50 0.322 vs 0.322 (3-3, p = 1).

Reading: with topical labels no routing variant beats the baseline on switch turns, and Opus-routed turns do no better than Jev-routed ones, so by the brief's test the loss is in the structure, not the reader. The facet is coarse where the traffic is: the mesh area alone holds 59 of 150 memories and over a third of turns, Jev sends 61 turns to `other`, and the two readers agree on a turn's area on 105 of 170 turns. The large all-labels gains of hard routing and of the bigger relative boosts are mostly always-on memories reached for free in small partitions (see the gains table), and topical hit rates stay flat.

## Facet

Which project or area is this item about. Leaf sizes:

| area | memories | turns (Jev) | turns (Opus) |
|---|---|---|---|
| orchestrator | 28 | 5 | 10 |
| mesh | 59 | 59 | 66 |
| routing | 3 | 31 | 63 |
| grove | 1 | 1 | 2 |
| torale | 5 | 0 | 0 |
| a2a-registry | 1 | 4 | 4 |
| common-obligations | 1 | 7 | 7 |
| personal-site | 1 | 2 | 3 |
| clusterkit | 3 | 0 | 0 |
| moltbook | 4 | 0 | 0 |
| daily-life | 6 | 0 | 0 |
| experiments | 3 | 0 | 1 |
| other | 35 | 61 | 14 |

Jev and Opus give a turn the same area on 105/170 turns.

Baseline top-1 score per turn, quartiles 23 / 119 / 208: a fixed boost of 1 to 4 rarely reorders the top 3, which is why relative boosts were added.

## Agreement at depth 1

Over (turn, labelled-useful memory) pairs: the share where the memory's area equals the turn's. Chance is the share for a memory drawn at random from the corpus.

| pairs | turn reader | n | agreement | chance |
|---|---|---|---|---|
| all labels | jev | 785 | 0.326 | 0.228 |
| all labels | opus | 785 | 0.345 | 0.186 |
| topical labels | jev | 626 | 0.361 | 0.231 |
| topical labels | opus | 626 | 0.345 | 0.196 |
| topical, high confidence | jev | 225 | 0.396 | 0.235 |
| topical, high confidence | opus | 225 | 0.307 | 0.155 |
| topical, switch turns | jev | 216 | 0.347 | 0.187 |
| topical, switch turns | opus | 216 | 0.338 | 0.162 |

Share of turns whose area holds at least one useful memory (the ceiling on hard routing):

| turn reader | all labels | topical |
|---|---|---|
| jev | 0.824 | 0.718 |
| opus | 0.871 | 0.682 |

## hit@3

Topical labels (primary), switch = topical useful set shares nothing with the previous turn's (n: overall 170, continuation 110, switch 59):

| method | overall | continuation | switch |
|---|---|---|---|
| recorded | 0.265 | 0.245 | 0.288 |
| baseline | 0.335 | 0.300 | 0.390 |
| hard-jev | 0.371 | 0.373 | 0.356 |
| hard-opus | 0.371 | 0.345 | 0.407 |
| soft-jev-b1 | 0.335 | 0.300 | 0.390 |
| soft-jev-b2 | 0.335 | 0.300 | 0.390 |
| soft-jev-b4 | 0.312 | 0.282 | 0.356 |
| soft-jev-r10 | 0.335 | 0.300 | 0.390 |
| soft-jev-r25 | 0.359 | 0.355 | 0.356 |
| soft-jev-r50 | 0.353 | 0.364 | 0.322 |
| soft-opus-b1 | 0.341 | 0.318 | 0.373 |
| soft-opus-b2 | 0.335 | 0.309 | 0.373 |
| soft-opus-b4 | 0.329 | 0.300 | 0.373 |
| soft-opus-r10 | 0.347 | 0.327 | 0.373 |
| soft-opus-r25 | 0.335 | 0.318 | 0.356 |
| soft-opus-r50 | 0.341 | 0.345 | 0.322 |

All labels, switch = topical useful set shares nothing with the previous turn's (n: overall 170, continuation 110, switch 59):

| method | overall | continuation | switch |
|---|---|---|---|
| recorded | 0.347 | 0.345 | 0.339 |
| baseline | 0.400 | 0.382 | 0.424 |
| hard-jev | 0.476 | 0.455 | 0.508 |
| hard-opus | 0.565 | 0.545 | 0.593 |
| soft-jev-b1 | 0.400 | 0.382 | 0.424 |
| soft-jev-b2 | 0.400 | 0.382 | 0.424 |
| soft-jev-b4 | 0.376 | 0.355 | 0.407 |
| soft-jev-r10 | 0.394 | 0.373 | 0.424 |
| soft-jev-r25 | 0.512 | 0.482 | 0.559 |
| soft-jev-r50 | 0.500 | 0.482 | 0.525 |
| soft-opus-b1 | 0.400 | 0.391 | 0.407 |
| soft-opus-b2 | 0.394 | 0.382 | 0.407 |
| soft-opus-b4 | 0.376 | 0.373 | 0.373 |
| soft-opus-r10 | 0.400 | 0.391 | 0.407 |
| soft-opus-r25 | 0.518 | 0.482 | 0.576 |
| soft-opus-r50 | 0.565 | 0.555 | 0.576 |

High-confidence rows only, topical labels (61 turns): recorded 0.230, baseline 0.377, hard-jev 0.426, hard-opus 0.393, soft-jev-b1 0.377, soft-jev-b2 0.377, soft-jev-b4 0.393, soft-jev-r10 0.377, soft-jev-r25 0.410, soft-jev-r50 0.410, soft-opus-b1 0.377, soft-opus-b2 0.377, soft-opus-b4 0.393, soft-opus-r10 0.377, soft-opus-r25 0.361, soft-opus-r50 0.344

Mean memories returned per turn (hard routing can return fewer than 3): recorded 3.00, baseline 3.00, hard-jev 2.80, hard-opus 2.79, soft-jev-b1 3.00, soft-jev-b2 3.00, soft-jev-b4 3.00, soft-jev-r10 3.00, soft-jev-r25 3.00, soft-jev-r50 3.00, soft-opus-b1 3.00, soft-opus-b2 3.00, soft-opus-b4 3.00, soft-opus-r10 3.00, soft-opus-r25 3.00, soft-opus-r50 3.00

## Paired comparison against baseline

Per turn, win = method hits and baseline misses. Exact two-sided sign test, ties dropped.

| switch definition | labels | turns | n | method | baseline hit@3 | method hit@3 | wins-losses | p |
|---|---|---|---|---|---|---|---|---|
| disjoint, topical (primary) | topical | overall | 170 | hard-jev | 0.335 | 0.371 | 24-18 | 0.441 |
| disjoint, topical (primary) | topical | overall | 170 | hard-opus | 0.335 | 0.371 | 26-20 | 0.461 |
| disjoint, topical (primary) | topical | overall | 170 | soft-jev-b1 | 0.335 | 0.335 | 0-0 | 1 |
| disjoint, topical (primary) | topical | overall | 170 | soft-jev-b2 | 0.335 | 0.335 | 0-0 | 1 |
| disjoint, topical (primary) | topical | overall | 170 | soft-jev-b4 | 0.335 | 0.312 | 1-5 | 0.219 |
| disjoint, topical (primary) | topical | overall | 170 | soft-jev-r10 | 0.335 | 0.335 | 0-0 | 1 |
| disjoint, topical (primary) | topical | overall | 170 | soft-jev-r25 | 0.335 | 0.359 | 9-5 | 0.424 |
| disjoint, topical (primary) | topical | overall | 170 | soft-jev-r50 | 0.335 | 0.353 | 19-16 | 0.736 |
| disjoint, topical (primary) | topical | overall | 170 | soft-opus-b1 | 0.335 | 0.341 | 2-1 | 1 |
| disjoint, topical (primary) | topical | overall | 170 | soft-opus-b2 | 0.335 | 0.335 | 3-3 | 1 |
| disjoint, topical (primary) | topical | overall | 170 | soft-opus-b4 | 0.335 | 0.329 | 4-5 | 1 |
| disjoint, topical (primary) | topical | overall | 170 | soft-opus-r10 | 0.335 | 0.347 | 3-1 | 0.625 |
| disjoint, topical (primary) | topical | overall | 170 | soft-opus-r25 | 0.335 | 0.335 | 9-9 | 1 |
| disjoint, topical (primary) | topical | overall | 170 | soft-opus-r50 | 0.335 | 0.341 | 19-18 | 1 |
| disjoint, topical (primary) | topical | continuation | 110 | hard-jev | 0.300 | 0.373 | 18-10 | 0.185 |
| disjoint, topical (primary) | topical | continuation | 110 | hard-opus | 0.300 | 0.345 | 20-15 | 0.5 |
| disjoint, topical (primary) | topical | continuation | 110 | soft-jev-b1 | 0.300 | 0.300 | 0-0 | 1 |
| disjoint, topical (primary) | topical | continuation | 110 | soft-jev-b2 | 0.300 | 0.300 | 0-0 | 1 |
| disjoint, topical (primary) | topical | continuation | 110 | soft-jev-b4 | 0.300 | 0.282 | 1-3 | 0.625 |
| disjoint, topical (primary) | topical | continuation | 110 | soft-jev-r10 | 0.300 | 0.300 | 0-0 | 1 |
| disjoint, topical (primary) | topical | continuation | 110 | soft-jev-r25 | 0.300 | 0.355 | 8-2 | 0.109 |
| disjoint, topical (primary) | topical | continuation | 110 | soft-jev-r50 | 0.300 | 0.364 | 15-8 | 0.21 |
| disjoint, topical (primary) | topical | continuation | 110 | soft-opus-b1 | 0.300 | 0.318 | 2-0 | 0.5 |
| disjoint, topical (primary) | topical | continuation | 110 | soft-opus-b2 | 0.300 | 0.309 | 3-2 | 1 |
| disjoint, topical (primary) | topical | continuation | 110 | soft-opus-b4 | 0.300 | 0.300 | 4-4 | 1 |
| disjoint, topical (primary) | topical | continuation | 110 | soft-opus-r10 | 0.300 | 0.327 | 3-0 | 0.25 |
| disjoint, topical (primary) | topical | continuation | 110 | soft-opus-r25 | 0.300 | 0.318 | 9-7 | 0.804 |
| disjoint, topical (primary) | topical | continuation | 110 | soft-opus-r50 | 0.300 | 0.345 | 17-12 | 0.458 |
| disjoint, topical (primary) | topical | switch | 59 | hard-jev | 0.390 | 0.356 | 6-8 | 0.791 |
| disjoint, topical (primary) | topical | switch | 59 | hard-opus | 0.390 | 0.407 | 6-5 | 1 |
| disjoint, topical (primary) | topical | switch | 59 | soft-jev-b1 | 0.390 | 0.390 | 0-0 | 1 |
| disjoint, topical (primary) | topical | switch | 59 | soft-jev-b2 | 0.390 | 0.390 | 0-0 | 1 |
| disjoint, topical (primary) | topical | switch | 59 | soft-jev-b4 | 0.390 | 0.356 | 0-2 | 0.5 |
| disjoint, topical (primary) | topical | switch | 59 | soft-jev-r10 | 0.390 | 0.390 | 0-0 | 1 |
| disjoint, topical (primary) | topical | switch | 59 | soft-jev-r25 | 0.390 | 0.356 | 1-3 | 0.625 |
| disjoint, topical (primary) | topical | switch | 59 | soft-jev-r50 | 0.390 | 0.322 | 4-8 | 0.388 |
| disjoint, topical (primary) | topical | switch | 59 | soft-opus-b1 | 0.390 | 0.373 | 0-1 | 1 |
| disjoint, topical (primary) | topical | switch | 59 | soft-opus-b2 | 0.390 | 0.373 | 0-1 | 1 |
| disjoint, topical (primary) | topical | switch | 59 | soft-opus-b4 | 0.390 | 0.373 | 0-1 | 1 |
| disjoint, topical (primary) | topical | switch | 59 | soft-opus-r10 | 0.390 | 0.373 | 0-1 | 1 |
| disjoint, topical (primary) | topical | switch | 59 | soft-opus-r25 | 0.390 | 0.356 | 0-2 | 0.5 |
| disjoint, topical (primary) | topical | switch | 59 | soft-opus-r50 | 0.390 | 0.322 | 2-6 | 0.289 |
| disjoint, topical (primary) | all | overall | 170 | hard-jev | 0.400 | 0.476 | 41-28 | 0.148 |
| disjoint, topical (primary) | all | overall | 170 | hard-opus | 0.400 | 0.565 | 50-22 | 0.00129 |
| disjoint, topical (primary) | all | overall | 170 | soft-jev-b1 | 0.400 | 0.400 | 0-0 | 1 |
| disjoint, topical (primary) | all | overall | 170 | soft-jev-b2 | 0.400 | 0.400 | 1-1 | 1 |
| disjoint, topical (primary) | all | overall | 170 | soft-jev-b4 | 0.400 | 0.376 | 2-6 | 0.289 |
| disjoint, topical (primary) | all | overall | 170 | soft-jev-r10 | 0.400 | 0.394 | 0-1 | 1 |
| disjoint, topical (primary) | all | overall | 170 | soft-jev-r25 | 0.400 | 0.512 | 26-7 | 0.00132 |
| disjoint, topical (primary) | all | overall | 170 | soft-jev-r50 | 0.400 | 0.500 | 40-23 | 0.043 |
| disjoint, topical (primary) | all | overall | 170 | soft-opus-b1 | 0.400 | 0.400 | 1-1 | 1 |
| disjoint, topical (primary) | all | overall | 170 | soft-opus-b2 | 0.400 | 0.394 | 2-3 | 1 |
| disjoint, topical (primary) | all | overall | 170 | soft-opus-b4 | 0.400 | 0.376 | 3-7 | 0.344 |
| disjoint, topical (primary) | all | overall | 170 | soft-opus-r10 | 0.400 | 0.400 | 2-2 | 1 |
| disjoint, topical (primary) | all | overall | 170 | soft-opus-r25 | 0.400 | 0.518 | 29-9 | 0.00166 |
| disjoint, topical (primary) | all | overall | 170 | soft-opus-r50 | 0.400 | 0.565 | 48-20 | 0.000914 |
| disjoint, topical (primary) | all | continuation | 110 | hard-jev | 0.382 | 0.455 | 27-19 | 0.302 |
| disjoint, topical (primary) | all | continuation | 110 | hard-opus | 0.382 | 0.545 | 34-16 | 0.0153 |
| disjoint, topical (primary) | all | continuation | 110 | soft-jev-b1 | 0.382 | 0.382 | 0-0 | 1 |
| disjoint, topical (primary) | all | continuation | 110 | soft-jev-b2 | 0.382 | 0.382 | 1-1 | 1 |
| disjoint, topical (primary) | all | continuation | 110 | soft-jev-b4 | 0.382 | 0.355 | 2-5 | 0.453 |
| disjoint, topical (primary) | all | continuation | 110 | soft-jev-r10 | 0.382 | 0.373 | 0-1 | 1 |
| disjoint, topical (primary) | all | continuation | 110 | soft-jev-r25 | 0.382 | 0.482 | 16-5 | 0.0266 |
| disjoint, topical (primary) | all | continuation | 110 | soft-jev-r50 | 0.382 | 0.482 | 27-16 | 0.126 |
| disjoint, topical (primary) | all | continuation | 110 | soft-opus-b1 | 0.382 | 0.391 | 1-0 | 1 |
| disjoint, topical (primary) | all | continuation | 110 | soft-opus-b2 | 0.382 | 0.382 | 2-2 | 1 |
| disjoint, topical (primary) | all | continuation | 110 | soft-opus-b4 | 0.382 | 0.373 | 3-4 | 1 |
| disjoint, topical (primary) | all | continuation | 110 | soft-opus-r10 | 0.382 | 0.391 | 2-1 | 1 |
| disjoint, topical (primary) | all | continuation | 110 | soft-opus-r25 | 0.382 | 0.482 | 17-6 | 0.0347 |
| disjoint, topical (primary) | all | continuation | 110 | soft-opus-r50 | 0.382 | 0.555 | 33-14 | 0.00794 |
| disjoint, topical (primary) | all | switch | 59 | hard-jev | 0.424 | 0.508 | 14-9 | 0.405 |
| disjoint, topical (primary) | all | switch | 59 | hard-opus | 0.424 | 0.593 | 16-6 | 0.0525 |
| disjoint, topical (primary) | all | switch | 59 | soft-jev-b1 | 0.424 | 0.424 | 0-0 | 1 |
| disjoint, topical (primary) | all | switch | 59 | soft-jev-b2 | 0.424 | 0.424 | 0-0 | 1 |
| disjoint, topical (primary) | all | switch | 59 | soft-jev-b4 | 0.424 | 0.407 | 0-1 | 1 |
| disjoint, topical (primary) | all | switch | 59 | soft-jev-r10 | 0.424 | 0.424 | 0-0 | 1 |
| disjoint, topical (primary) | all | switch | 59 | soft-jev-r25 | 0.424 | 0.559 | 10-2 | 0.0386 |
| disjoint, topical (primary) | all | switch | 59 | soft-jev-r50 | 0.424 | 0.525 | 13-7 | 0.263 |
| disjoint, topical (primary) | all | switch | 59 | soft-opus-b1 | 0.424 | 0.407 | 0-1 | 1 |
| disjoint, topical (primary) | all | switch | 59 | soft-opus-b2 | 0.424 | 0.407 | 0-1 | 1 |
| disjoint, topical (primary) | all | switch | 59 | soft-opus-b4 | 0.424 | 0.373 | 0-3 | 0.25 |
| disjoint, topical (primary) | all | switch | 59 | soft-opus-r10 | 0.424 | 0.407 | 0-1 | 1 |
| disjoint, topical (primary) | all | switch | 59 | soft-opus-r25 | 0.424 | 0.576 | 12-3 | 0.0352 |
| disjoint, topical (primary) | all | switch | 59 | soft-opus-r50 | 0.424 | 0.576 | 15-6 | 0.0784 |
| disjoint, all labels | topical | continuation | 127 | soft-jev-b2 | 0.299 | 0.299 | 0-0 | 1 |
| disjoint, all labels | topical | continuation | 127 | soft-opus-b2 | 0.299 | 0.307 | 3-2 | 1 |
| disjoint, all labels | topical | switch | 42 | soft-jev-b2 | 0.429 | 0.429 | 0-0 | 1 |
| disjoint, all labels | topical | switch | 42 | soft-opus-b2 | 0.429 | 0.405 | 0-1 | 1 |
| disjoint, topical at 15% | topical | continuation | 91 | soft-jev-b2 | 0.319 | 0.319 | 0-0 | 1 |
| disjoint, topical at 15% | topical | continuation | 91 | soft-opus-b2 | 0.319 | 0.319 | 2-2 | 1 |
| disjoint, topical at 15% | topical | switch | 78 | soft-jev-b2 | 0.346 | 0.346 | 0-0 | 1 |
| disjoint, topical at 15% | topical | switch | 78 | soft-opus-b2 | 0.346 | 0.346 | 1-1 | 1 |
| top-1 differs, topical | topical | continuation | 39 | soft-jev-b2 | 0.333 | 0.333 | 0-0 | 1 |
| top-1 differs, topical | topical | continuation | 39 | soft-opus-b2 | 0.333 | 0.359 | 1-0 | 1 |
| top-1 differs, topical | topical | switch | 130 | soft-jev-b2 | 0.331 | 0.331 | 0-0 | 1 |
| top-1 differs, topical | topical | switch | 130 | soft-opus-b2 | 0.331 | 0.323 | 2-3 | 1 |
| set differs, all labels | topical | continuation | 3 | soft-jev-b2 | 0.667 | 0.667 | 0-0 | 1 |
| set differs, all labels | topical | continuation | 3 | soft-opus-b2 | 0.667 | 0.667 | 0-0 | 1 |
| set differs, all labels | topical | switch | 166 | soft-jev-b2 | 0.325 | 0.325 | 0-0 | 1 |
| set differs, all labels | topical | switch | 166 | soft-opus-b2 | 0.325 | 0.325 | 3-3 | 1 |
| sender project differs (no label) | topical | continuation | 123 | soft-jev-b2 | 0.317 | 0.317 | 0-0 | 1 |
| sender project differs (no label) | topical | continuation | 123 | soft-opus-b2 | 0.317 | 0.317 | 2-2 | 1 |
| sender project differs (no label) | topical | switch | 46 | soft-jev-b2 | 0.370 | 0.370 | 0-0 | 1 |
| sender project differs (no label) | topical | switch | 46 | soft-opus-b2 | 0.370 | 0.370 | 1-1 | 1 |

Sensitivity rows (below the primary block) compare soft-jev-b2, soft-opus-b2 only. `sender project differs` uses no label: it is the only switch signal a deployed index could act on.

## Where the all-labels gains come from

Overall wins over the baseline on all labels, and how many of them hit only an always-on memory (no topical memory in the method's top 3):

| method | all-label wins | of which always-on only |
|---|---|---|
| hard-jev | 41 | 17 |
| hard-opus | 50 | 25 |
| soft-jev-b1 | 0 | 0 |
| soft-jev-b2 | 1 | 1 |
| soft-jev-b4 | 2 | 1 |
| soft-jev-r10 | 0 | 0 |
| soft-jev-r25 | 26 | 17 |
| soft-jev-r50 | 40 | 21 |
| soft-opus-b1 | 1 | 0 |
| soft-opus-b2 | 2 | 0 |
| soft-opus-b4 | 3 | 0 |
| soft-opus-r10 | 2 | 0 |
| soft-opus-r25 | 29 | 21 |
| soft-opus-r50 | 48 | 30 |

## Reader: Opus-routed against Jev-routed turns

Paired on the same turns and boost; win = Opus-routed hits and Jev-routed misses.

| labels | turns | n | boost | Jev-routed hit@3 | Opus-routed hit@3 | wins-losses | p |
|---|---|---|---|---|---|---|---|
| topical | overall | 170 | b1 | 0.335 | 0.341 | 2-1 | 1 |
| topical | overall | 170 | b2 | 0.335 | 0.335 | 3-3 | 1 |
| topical | overall | 170 | b4 | 0.312 | 0.329 | 5-2 | 0.453 |
| topical | overall | 170 | r10 | 0.335 | 0.347 | 3-1 | 0.625 |
| topical | overall | 170 | r25 | 0.359 | 0.335 | 4-8 | 0.388 |
| topical | overall | 170 | r50 | 0.353 | 0.341 | 12-14 | 0.845 |
| topical | continuation | 110 | b1 | 0.300 | 0.318 | 2-0 | 0.5 |
| topical | continuation | 110 | b2 | 0.300 | 0.309 | 3-2 | 1 |
| topical | continuation | 110 | b4 | 0.282 | 0.300 | 4-2 | 0.688 |
| topical | continuation | 110 | r10 | 0.300 | 0.327 | 3-0 | 0.25 |
| topical | continuation | 110 | r25 | 0.355 | 0.318 | 3-7 | 0.344 |
| topical | continuation | 110 | r50 | 0.364 | 0.345 | 9-11 | 0.824 |
| topical | switch | 59 | b1 | 0.390 | 0.373 | 0-1 | 1 |
| topical | switch | 59 | b2 | 0.390 | 0.373 | 0-1 | 1 |
| topical | switch | 59 | b4 | 0.356 | 0.373 | 1-0 | 1 |
| topical | switch | 59 | r10 | 0.390 | 0.373 | 0-1 | 1 |
| topical | switch | 59 | r25 | 0.356 | 0.356 | 1-1 | 1 |
| topical | switch | 59 | r50 | 0.322 | 0.322 | 3-3 | 1 |
| all | overall | 170 | b1 | 0.400 | 0.400 | 1-1 | 1 |
| all | overall | 170 | b2 | 0.400 | 0.394 | 2-3 | 1 |
| all | overall | 170 | b4 | 0.376 | 0.376 | 3-3 | 1 |
| all | overall | 170 | r10 | 0.394 | 0.400 | 3-2 | 1 |
| all | overall | 170 | r25 | 0.512 | 0.518 | 7-6 | 1 |
| all | overall | 170 | r50 | 0.500 | 0.565 | 19-8 | 0.0522 |
| all | continuation | 110 | b1 | 0.382 | 0.391 | 1-0 | 1 |
| all | continuation | 110 | b2 | 0.382 | 0.382 | 2-2 | 1 |
| all | continuation | 110 | b4 | 0.355 | 0.373 | 3-1 | 0.625 |
| all | continuation | 110 | r10 | 0.373 | 0.391 | 3-1 | 0.625 |
| all | continuation | 110 | r25 | 0.482 | 0.482 | 4-4 | 1 |
| all | continuation | 110 | r50 | 0.482 | 0.555 | 14-6 | 0.115 |
| all | switch | 59 | b1 | 0.424 | 0.407 | 0-1 | 1 |
| all | switch | 59 | b2 | 0.424 | 0.407 | 0-1 | 1 |
| all | switch | 59 | b4 | 0.407 | 0.373 | 0-2 | 0.5 |
| all | switch | 59 | r10 | 0.424 | 0.407 | 0-1 | 1 |
| all | switch | 59 | r25 | 0.559 | 0.576 | 3-2 | 1 |
| all | switch | 59 | r50 | 0.525 | 0.576 | 5-2 | 0.453 |

## Cost

Cumulative across both experiments.

| item | usage | USD |
|---|---|---|
| Jev: probe | 49,485 input tokens | 0.002 |
| Jev: route | 764,432 input tokens | 0.032 |
| Jev: areas | 850,295 input tokens | 0.036 |
| Jev total | 1,664,212 input tokens | 0.070 |
| claude-opus-5-5: label-probe | 1 requests | 0.098 |
| claude-opus-5-5: label | 170 requests | 1.730 |
| claude-opus-5-5: propose | 1 requests | 0.049 |
| claude-opus-5-5: read areas | 170 requests | 1.048 |
| claude-opus-5-5 total |  | 2.925 |

Jev USD is estimated at the router paper's rate ($1.21 per 28.8M input tokens). Index time: one Jev call per memory with the 13 area questions. Recall time: one Jev call per turn with the same questions.
