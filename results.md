# grove first experiment: results

170 inbound orchestrator turns (2026-10-06 to 2026-10-14: every delivered message in the 14-day window that carried a recall block), 150 memory files. Labels: first pass by claude-opus-5-5 from the turn and the memory index; 109 of 170 rows are marked low confidence. The orchestrator spot-checked 30 rows (20 low, 10 high confidence): 26 agree, 4 disagree, all four in the low-confidence pool.

Coverage, not recall: 21 of the 109 low-confidence rows give as their reason that the referent is unclear or that no memory covers it (keyword match on the labeller's reason). Three of the four spot-check disagreements were of this kind.

Always-on memories: labelled useful on more than 25% of turns, treated as format rather than topic: `memory/feedback_telegram_message_size.md` (58), `memory/peer_to_peer_review_iteration.md` (48), `memory/routing_refactor_gate.md` (53). At 15% the list grows to 7. `topical` labels drop the 25% list; 0 turns are left with no topical memory and are excluded from topical hit rates.

Methods: `recorded` is the recall block the daemon attached at delivery. `baseline` is the Go scorer ported to Python and run on today's corpus (the corpus the forest and the labeller see). `forest-dN` is the baseline scorer restricted to memories that share the turn's path to depth N. hit@3 = at least one labelled-useful memory in the top 3.

## Headline

Path agreement for (turn, useful memory) pairs, topical labels: 0.722 / 0.420 / 0.326 at depth 1 / 2 / 3 against chance 0.500 / 0.232 / 0.157. hit@3, topical labels: baseline 0.335 vs forest-d3 0.235 overall (wins-losses 14-31, p = 0.0161); on switch turns baseline 0.390 vs forest-d3 0.220 (3-13, p = 0.0213). The forest agrees with the labels well above chance but not enough: by depth 3 two thirds of useful memories sit off the turn's path, and the token-overlap baseline beats it, most clearly on switches. The depth-1 forest ties the baseline.

## Tree

| depth | facet | question | memories yes | turns yes | balance | decisiveness |
|---|---|---|---|---|---|---|
| 1 | project | Does this item involve source code, CI, PRs, or releases of a repository? | 75/150 | 103/170 | 1.00 | 0.84 |
| 2 | kind | Is this item describing a failure, bug, or surprising gotcha in how a system behaves? | 85/150 | 68/170 | 0.99 | 0.69 |
| 3 | who or when | Is this item relevant at a session or process lifecycle moment, such as spawning, restarting, resuming, or authentication expiry? | 44/150 | 30/170 | 0.87 | 0.69 |

Leaves (path: memories / turns): `000` 23 / 53, `001` 5 / 8, `010` 22 / 4, `011` 25 / 2, `100` 36 / 35, `101` 1 / 6, `110` 25 / 48, `111` 13 / 14

Candidates proposed by claude-opus-5-5 from a 60-file sample. Selection uses no labels: balance (entropy of the yes share on memories) times decisiveness (mean 2|p-0.5| on turns), best per facet.

| key | facet | question | balance | decisiveness | score |
|---|---|---|---|---|---|
| q0 | project | Is this item about the internals of the Repowire mesh/daemon itself (peers, circles, hooks, routing, daemon code, releases)? | 0.96 | 0.72 | 0.69 |
| q1 | project | Does this item concern a specific product or repository other than the orchestration mesh (e.g., a web app, infra repo, paper, or email/calendar tooling)? | 0.97 | 0.53 | 0.51 |
| q2 | project | Is this item about the orchestrator's own role, persona, or session (as opposed to the workers or projects it coordinates)? | 0.88 | 0.75 | 0.66 |
| q3 | project | Does this item involve source code, CI, PRs, or releases of a repository? | 1.00 | 0.84 | 0.84 |
| q4 | kind | Is this item describing a failure, bug, or surprising gotcha in how a system behaves? | 0.99 | 0.69 | 0.68 |
| q5 | kind | Is this item a rule or preference about how the orchestrator should behave or communicate? | 0.82 | 0.76 | 0.62 |
| q6 | kind | Does this item contain a concrete operational procedure or fix (specific commands, flags, or steps)? | 0.68 | 0.66 | 0.45 |
| q7 | kind | Is this item about a pending task, commitment, or request for work to be done? | 0.30 | 0.46 | 0.14 |
| q8 | who or when | Does this item originate from or directly quote an explicit instruction or correction by the user? | 0.99 | 0.59 | 0.58 |
| q9 | who or when | Does this item mainly concern the behavior of worker peers/agents rather than the user or orchestrator? | 0.99 | 0.40 | 0.39 |
| q10 | who or when | Is this item tied to a temporary period or situation (such as holiday mode, a launch, or a current incident)? | 0.71 | 0.34 | 0.24 |
| q11 | who or when | Is this item relevant at a session or process lifecycle moment, such as spawning, restarting, resuming, or authentication expiry? | 0.87 | 0.69 | 0.60 |

## Path agreement by depth

Over (turn, labelled-useful memory) pairs: the share where the memory's path matches the turn's to depth N. Chance is the agreement expected for a memory drawn at random from the corpus.

| pairs | n | depth | agreement | chance |
|---|---|---|---|---|
| all labels | 785 | 1 | 0.703 | 0.500 |
| all labels | 785 | 2 | 0.378 | 0.232 |
| all labels | 785 | 3 | 0.299 | 0.159 |
| topical labels | 626 | 1 | 0.722 | 0.500 |
| topical labels | 626 | 2 | 0.420 | 0.232 |
| topical labels | 626 | 3 | 0.326 | 0.157 |
| topical, high confidence | 225 | 1 | 0.787 | 0.500 |
| topical, high confidence | 225 | 2 | 0.462 | 0.235 |
| topical, high confidence | 225 | 3 | 0.342 | 0.150 |
| topical, switch turns | 216 | 1 | 0.648 | 0.500 |
| topical, switch turns | 216 | 2 | 0.370 | 0.226 |
| topical, switch turns | 216 | 3 | 0.310 | 0.162 |

Share of turns whose path reaches at least one useful memory at depth N (the ceiling on forest hit@k):

| depth | all labels | topical |
|---|---|---|
| 1 | 0.982 | 0.982 |
| 2 | 0.829 | 0.788 |
| 3 | 0.759 | 0.712 |

## hit@3

Topical labels (primary), switch = topical useful set shares nothing with the previous turn's (n: overall 170, continuation 110, switch 59):

| method | overall | continuation | switch |
|---|---|---|---|
| recorded | 0.265 | 0.245 | 0.288 |
| baseline | 0.335 | 0.300 | 0.390 |
| forest-d1 | 0.335 | 0.327 | 0.339 |
| forest-d2 | 0.282 | 0.300 | 0.237 |
| forest-d3 | 0.235 | 0.236 | 0.220 |

All labels, switch = topical useful set shares nothing with the previous turn's (n: overall 170, continuation 110, switch 59):

| method | overall | continuation | switch |
|---|---|---|---|
| recorded | 0.347 | 0.345 | 0.339 |
| baseline | 0.400 | 0.382 | 0.424 |
| forest-d1 | 0.341 | 0.336 | 0.339 |
| forest-d2 | 0.376 | 0.400 | 0.322 |
| forest-d3 | 0.318 | 0.318 | 0.305 |

High-confidence rows only, topical labels (61 turns): recorded 0.230, baseline 0.377, forest-d1 0.328, forest-d2 0.311, forest-d3 0.246

Mean memories returned per turn (a leaf can hold fewer than 3 scoring memories): recorded 3.00, baseline 3.00, forest-d1 3.00, forest-d2 2.96, forest-d3 2.89

## Paired comparison against baseline

Per turn, win = method hits and baseline misses. Exact two-sided sign test, ties dropped.

| switch definition | labels | turns | n | method | baseline hit@3 | method hit@3 | wins-losses | p |
|---|---|---|---|---|---|---|---|---|
| disjoint, topical (primary) | topical | overall | 170 | forest-d1 | 0.335 | 0.335 | 9-9 | 1 |
| disjoint, topical (primary) | topical | overall | 170 | forest-d2 | 0.335 | 0.282 | 15-24 | 0.2 |
| disjoint, topical (primary) | topical | overall | 170 | forest-d3 | 0.335 | 0.235 | 14-31 | 0.0161 |
| disjoint, topical (primary) | topical | overall | 170 | recorded | 0.335 | 0.265 | 3-15 | 0.00754 |
| disjoint, topical (primary) | topical | continuation | 110 | forest-d1 | 0.300 | 0.327 | 7-4 | 0.549 |
| disjoint, topical (primary) | topical | continuation | 110 | forest-d2 | 0.300 | 0.300 | 13-13 | 1 |
| disjoint, topical (primary) | topical | continuation | 110 | forest-d3 | 0.300 | 0.236 | 11-18 | 0.265 |
| disjoint, topical (primary) | topical | continuation | 110 | recorded | 0.300 | 0.245 | 3-9 | 0.146 |
| disjoint, topical (primary) | topical | switch | 59 | forest-d1 | 0.390 | 0.339 | 2-5 | 0.453 |
| disjoint, topical (primary) | topical | switch | 59 | forest-d2 | 0.390 | 0.237 | 2-11 | 0.0225 |
| disjoint, topical (primary) | topical | switch | 59 | forest-d3 | 0.390 | 0.220 | 3-13 | 0.0213 |
| disjoint, topical (primary) | topical | switch | 59 | recorded | 0.390 | 0.288 | 0-6 | 0.0312 |
| disjoint, topical (primary) | all | overall | 170 | forest-d1 | 0.400 | 0.341 | 3-13 | 0.0213 |
| disjoint, topical (primary) | all | overall | 170 | forest-d2 | 0.400 | 0.376 | 26-30 | 0.689 |
| disjoint, topical (primary) | all | overall | 170 | forest-d3 | 0.400 | 0.318 | 24-38 | 0.098 |
| disjoint, topical (primary) | all | overall | 170 | recorded | 0.400 | 0.347 | 3-12 | 0.0352 |
| disjoint, topical (primary) | all | continuation | 110 | forest-d1 | 0.382 | 0.336 | 2-7 | 0.18 |
| disjoint, topical (primary) | all | continuation | 110 | forest-d2 | 0.382 | 0.400 | 19-17 | 0.868 |
| disjoint, topical (primary) | all | continuation | 110 | forest-d3 | 0.382 | 0.318 | 16-23 | 0.337 |
| disjoint, topical (primary) | all | continuation | 110 | recorded | 0.382 | 0.345 | 3-7 | 0.344 |
| disjoint, topical (primary) | all | switch | 59 | forest-d1 | 0.424 | 0.339 | 1-6 | 0.125 |
| disjoint, topical (primary) | all | switch | 59 | forest-d2 | 0.424 | 0.322 | 7-13 | 0.263 |
| disjoint, topical (primary) | all | switch | 59 | forest-d3 | 0.424 | 0.305 | 8-15 | 0.21 |
| disjoint, topical (primary) | all | switch | 59 | recorded | 0.424 | 0.339 | 0-5 | 0.0625 |
| disjoint, all labels | topical | continuation | 127 | forest-d3 | 0.299 | 0.244 | 13-20 | 0.296 |
| disjoint, all labels | topical | switch | 42 | forest-d3 | 0.429 | 0.190 | 1-11 | 0.00635 |
| disjoint, topical at 15% | topical | continuation | 91 | forest-d3 | 0.319 | 0.253 | 9-15 | 0.307 |
| disjoint, topical at 15% | topical | switch | 78 | forest-d3 | 0.346 | 0.205 | 5-16 | 0.0266 |
| top-1 differs, topical | topical | continuation | 39 | forest-d3 | 0.333 | 0.308 | 6-7 | 1 |
| top-1 differs, topical | topical | switch | 130 | forest-d3 | 0.331 | 0.208 | 8-24 | 0.007 |
| set differs, all labels | topical | continuation | 3 | forest-d3 | 0.667 | 0.333 | 0-1 | 1 |
| set differs, all labels | topical | switch | 166 | forest-d3 | 0.325 | 0.229 | 14-30 | 0.0226 |
| sender project differs (no label) | topical | continuation | 123 | forest-d3 | 0.317 | 0.244 | 11-20 | 0.15 |
| sender project differs (no label) | topical | switch | 46 | forest-d3 | 0.370 | 0.196 | 3-11 | 0.0574 |

Sensitivity rows (below the primary block) compare forest-d3 only. `sender project differs` uses no label: it is the only switch signal a deployed index could act on.

## Classifier stability

20 items (10 memories, 10 turns) routed twice: identical depth-3 path for 20/20; mean |Δp| across all candidate questions 0.010.

## Baseline port and corpus drift

The port reproduces the recorded recall block exactly (same files, same order) on 105 of 170 turns. Each of the other 65 involves a file modified after the turn, or written within five minutes before it was logged (the daemon computes recall at delivery, before the client logs the turn); none is unexplained. The turns span 1 orchestrator session(s); in 59 of the 65 drift rows a file involved was edited between five minutes before the turn and the end of that session, that is by the orchestrator while handling the turn or after it.

Leakage direction: the corpus is today's, so memories the orchestrator wrote in response to a turn are visible to every method and to the labeller. That helps the baseline and the forest alike wherever both rank the new file, and it inflates hit rates relative to the recorded block, which saw the older corpus.

## Cost

| item | usage | USD |
|---|---|---|
| Jev: every candidate question on 320 items, plus probes | 813,917 input tokens | 0.034 |
| claude-opus-5-5: label-probe | 1 requests | 0.098 |
| claude-opus-5-5: label | 170 requests | 1.730 |
| claude-opus-5-5: propose | 1 requests | 0.049 |

Jev USD is estimated at the router paper's rate ($1.21 per 28.8M input tokens). At index time a memory costs one Jev call; at recall time a turn costs one Jev call with the three chosen questions.
