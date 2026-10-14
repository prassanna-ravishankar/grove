# grove third experiment: cascades for memory recall

170 inbound orchestrator turns (2026-10-06 to 2026-10-14: every delivered message in the 14-day window that carried a recall block), 150 memory files. Labels: first pass by claude-opus-5-5 from the turn and the memory index; 109 of 170 rows are marked low confidence. The orchestrator spot-checked 30 rows (20 low, 10 high confidence): 26 agree, 4 disagree, all four in the low-confidence pool.

Coverage, not recall: 21 of the 109 low-confidence rows give as their reason that the referent is unclear or that no memory covers it (keyword match on the labeller's reason). Three of the four spot-check disagreements were of this kind.

Always-on memories: labelled useful on more than 25% of turns, treated as format rather than topic: `memory/feedback_telegram_message_size.md` (58), `memory/peer_to_peer_review_iteration.md` (48), `memory/routing_refactor_gate.md` (53). At 15% the list grows to 7. `topical` labels drop the 25% list; 0 turns are left with no topical memory and are excluded from topical hit rates.

Question: does a cascade, a cheap default plus a frontier reader invoked on an observable trigger, beat the token-overlap baseline on topic switches, and at what call share? The design is the router paper's cascade section applied to memory.

Methods. Defaults: `baseline` is the ported Repowire scorer; `previous` is the baseline's top 3 for the previous turn (the baseline on the first turn). Readers: `sonnet` (claude-sonnet-5-5) and `haiku` (claude-haiku-5-5), each given the turn (sender, target, first 6000 characters) and the memory index, returning three files, effort low; a reader alone is the always-escalate ceiling. Triggers, each observable before the decision: `sender` (sender differs from the previous turn's), `project` (sender's project differs), `score<Q` (baseline top-1 score below its Q quantile over the 170 turns), `always-on` (the baseline's top 3 are all always-on memories). `oracle` fires on the labelled switch itself; it is not observable and is reported only as a reference. A cascade `D/T/R` returns default D unless trigger T fires, then reader R's answer. `best-of baseline, R` counts a turn as a hit when either the baseline or R hits: the ceiling for any trigger over the baseline default. `random trigger` columns give the expected hit@3 of the same default and reader with the reader called on the same share of turns at random: a trigger earns its place only above that line. `index-overlap` is a control: the baseline scorer run over the reader's index lines (file name and one-line description) instead of file contents.

claude-opus-5-5 is not used as a reader: the labels came from it, so an Opus reader would be scored against its own judgement. The Sonnet and Haiku readers are still not independent of the labeller in one respect: the labeller saw a similar index (file names and frontmatter descriptions) and no file contents, so labels and readers share a view of the corpus that the token-overlap baseline does not. That favours the readers.

Index: 148 memory files, 111 described by their MEMORY.md line (matched on link target, link text, or frontmatter name; MEMORY.md copied from the live directory at the start of this experiment), the rest by their frontmatter description; projects.md by its headings and top-level entry names; comms.md by its first lines. About 8,790 tokens.

Score thresholds (baseline top-1 score): `score<10%` = 10, `score<25%` = 23, `score<50%` = 119, `score<75%` = 208. The always-on trigger uses the label-derived >25% list, which a deployed system would have to learn from usage.

## Headline

Switch turns, topical labels, against the baseline: `sonnet` 0.864 vs 0.390 (wins-losses 29-1, p = 5.77e-08, call share 1.000); `haiku` 0.678 vs 0.390 (wins-losses 21-4, p = 0.000911, call share 1.000); `baseline/project/sonnet` 0.661 vs 0.390 (wins-losses 17-1, p = 0.000145, call share 0.271); `baseline/sender/sonnet` 0.763 vs 0.390 (wins-losses 23-1, p = 2.98e-06, call share 0.547). `baseline/sender/sonnet` is the best observable cascade on the switch column, chosen on it, so its p is optimistic; `baseline/project/sonnet` was fixed in advance.

Reading. Yes, a cascade beats the baseline on switches, and the project trigger does it with a reader call on about a quarter of turns. But the reader is not a switch specialist: alone it scores 0.873 on continuations against the baseline's 0.300, as large a gain as on switches. The router paper's cascade works because the cheap default (repeat the last recipient) is right on continuations; here neither cheap default is. `previous` is worse than the baseline even on continuations (0.273), so what a turn needs from memory does not persist the way its recipient does. So every cascade trades accuracy for calls roughly linearly. The sender and project triggers move the reader's calls onto switches (precision 0.49 and 0.80 against a 0.35 base rate) and beat a random trigger at the same share on switches, but overall they stay within 0.02 of it. The score triggers do no better than random on switches and worse overall, and the always-on trigger never fires: the baseline's top 3 always includes a topical file.

Caveat on the size of the effect. The labels are Opus reading an index of descriptions; the readers are Sonnet and Haiku reading a near-identical index. The `index-overlap` control (0.329 overall, at the baseline) rules out surface token overlap between the labels and the index as the source. It does not rule out models of one family agreeing on what a description means. The 30-row spot-check (26 agree) is the only human evidence that the labels track usefulness. The direction (reader over token overlap) is robust across every switch definition; the margin should be read as agreement with the labeller until it is checked against human labels or usage.

## hit@3 and call share

Topical labels (primary). Switch = topical useful set shares nothing with the previous turn's (n: overall 170, continuation 110, switch 59). Call share = share of turns on which the reader is called. W-L = wins-losses against the baseline on the same turns, exact two-sided sign test, ties dropped. The last two columns are the all-labels sensitivity on switch turns.

| method | call share | call share on switches | overall | continuation | switch | random trigger, overall | random trigger, switch | switch W-L vs baseline | overall W-L vs baseline | switch, all labels | switch W-L, all labels |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 0.000 | 0.000 | 0.335 | 0.300 | 0.390 | - | - | 0-0 (p 1) | 0-0 (p 1) | 0.424 | 0-0 (p 1) |
| previous | 0.000 | 0.000 | 0.224 | 0.273 | 0.119 | - | - | 2-18 (p 0.000402) | 9-28 (p 0.00256) | 0.186 | 4-18 (p 0.00434) |
| index-overlap | 0.000 | 0.000 | 0.329 | 0.309 | 0.356 | - | - | 7-9 (p 0.804) | 21-22 (p 1) | 0.356 | 6-10 (p 0.454) |
| sonnet | 1.000 | 1.000 | 0.871 | 0.873 | 0.864 | - | - | 29-1 (p 5.77e-08) | 93-2 (p 2.3e-25) | 0.983 | 33-0 (p 2.33e-10) |
| haiku | 1.000 | 1.000 | 0.618 | 0.582 | 0.678 | - | - | 21-4 (p 0.000911) | 58-10 (p 2.36e-09) | 0.831 | 26-2 (p 3.03e-06) |
| previous/sender/sonnet | 0.547 | 0.780 | 0.612 | 0.564 | 0.695 | 0.578 | 0.527 | 23-5 (p 0.000912) | 60-13 (p 2.31e-08) | 0.847 | 28-3 (p 4.65e-06) |
| previous/sender/haiku | 0.547 | 0.780 | 0.465 | 0.427 | 0.525 | 0.439 | 0.425 | 16-8 (p 0.152) | 40-18 (p 0.00535) | 0.712 | 22-5 (p 0.00151) |
| previous/project/sonnet | 0.271 | 0.627 | 0.429 | 0.345 | 0.576 | 0.399 | 0.320 | 17-6 (p 0.0347) | 31-15 (p 0.0259) | 0.712 | 21-4 (p 0.000911) |
| previous/project/haiku | 0.271 | 0.627 | 0.371 | 0.327 | 0.441 | 0.330 | 0.270 | 12-9 (p 0.664) | 24-18 (p 0.441) | 0.593 | 16-6 (p 0.0525) |
| previous/score<10%/sonnet | 0.100 | 0.169 | 0.288 | 0.291 | 0.271 | 0.288 | 0.193 | 6-13 (p 0.167) | 13-21 (p 0.229) | 0.339 | 8-13 (p 0.383) |
| previous/score<10%/haiku | 0.100 | 0.169 | 0.282 | 0.291 | 0.254 | 0.263 | 0.175 | 6-14 (p 0.115) | 13-22 (p 0.175) | 0.339 | 8-13 (p 0.383) |
| previous/score<25%/sonnet | 0.241 | 0.271 | 0.365 | 0.364 | 0.356 | 0.380 | 0.299 | 7-9 (p 0.804) | 19-14 (p 0.487) | 0.424 | 8-8 (p 1) |
| previous/score<25%/haiku | 0.241 | 0.271 | 0.335 | 0.336 | 0.322 | 0.319 | 0.254 | 7-11 (p 0.481) | 16-16 (p 1) | 0.407 | 8-9 (p 1) |
| previous/score<50%/sonnet | 0.494 | 0.559 | 0.524 | 0.500 | 0.559 | 0.543 | 0.487 | 14-4 (p 0.0309) | 37-5 (p 4.43e-07) | 0.627 | 15-3 (p 0.00754) |
| previous/score<50%/haiku | 0.494 | 0.559 | 0.453 | 0.418 | 0.508 | 0.418 | 0.395 | 13-6 (p 0.167) | 27-7 (p 0.000821) | 0.610 | 15-4 (p 0.0192) |
| previous/score<75%/sonnet | 0.747 | 0.746 | 0.735 | 0.736 | 0.729 | 0.707 | 0.676 | 23-3 (p 8.8e-05) | 71-3 (p 7.16e-18) | 0.797 | 24-2 (p 1.05e-05) |
| previous/score<75%/haiku | 0.747 | 0.746 | 0.553 | 0.518 | 0.610 | 0.518 | 0.536 | 18-5 (p 0.0106) | 45-8 (p 2.37e-07) | 0.729 | 21-3 (p 0.000277) |
| previous/always-on/sonnet | 0.000 | 0.000 | 0.224 | 0.273 | 0.119 | 0.224 | 0.119 | 2-18 (p 0.000402) | 9-28 (p 0.00256) | 0.186 | 4-18 (p 0.00434) |
| previous/always-on/haiku | 0.000 | 0.000 | 0.224 | 0.273 | 0.119 | 0.224 | 0.119 | 2-18 (p 0.000402) | 9-28 (p 0.00256) | 0.186 | 4-18 (p 0.00434) |
| previous/oracle/sonnet | 0.347 | 1.000 | 0.482 | 0.273 | 0.864 | 0.448 | 0.377 | 29-1 (p 5.77e-08) | 36-11 (p 0.000346) | 0.983 | 33-0 (p 2.33e-10) |
| previous/oracle/haiku | 0.347 | 1.000 | 0.418 | 0.273 | 0.678 | 0.360 | 0.313 | 21-4 (p 0.000911) | 28-14 (p 0.0436) | 0.831 | 26-2 (p 3.03e-06) |
| baseline/sender/sonnet | 0.547 | 0.780 | 0.647 | 0.582 | 0.763 | 0.628 | 0.649 | 23-1 (p 2.98e-06) | 55-2 (p 2.3e-14) | 0.881 | 27-0 (p 1.49e-08) |
| baseline/sender/haiku | 0.547 | 0.780 | 0.500 | 0.445 | 0.593 | 0.490 | 0.547 | 16-4 (p 0.0118) | 35-7 (p 1.51e-05) | 0.746 | 21-2 (p 6.6e-05) |
| baseline/project/sonnet | 0.271 | 0.627 | 0.476 | 0.373 | 0.661 | 0.480 | 0.518 | 17-1 (p 0.000145) | 25-1 (p 8.05e-07) | 0.763 | 20-0 (p 1.91e-06) |
| baseline/project/haiku | 0.271 | 0.627 | 0.418 | 0.355 | 0.525 | 0.412 | 0.468 | 12-4 (p 0.0768) | 18-4 (p 0.00434) | 0.644 | 15-2 (p 0.00235) |
| baseline/score<10%/sonnet | 0.100 | 0.169 | 0.376 | 0.318 | 0.475 | 0.389 | 0.437 | 5-0 (p 0.0625) | 7-0 (p 0.0156) | 0.508 | 5-0 (p 0.0625) |
| baseline/score<10%/haiku | 0.100 | 0.169 | 0.371 | 0.318 | 0.458 | 0.364 | 0.419 | 5-1 (p 0.219) | 7-1 (p 0.0703) | 0.508 | 5-0 (p 0.0625) |
| baseline/score<25%/sonnet | 0.241 | 0.271 | 0.418 | 0.382 | 0.475 | 0.464 | 0.504 | 6-1 (p 0.125) | 15-1 (p 0.000519) | 0.525 | 6-0 (p 0.0312) |
| baseline/score<25%/haiku | 0.241 | 0.271 | 0.388 | 0.355 | 0.441 | 0.403 | 0.459 | 6-3 (p 0.508) | 12-3 (p 0.0352) | 0.508 | 6-1 (p 0.125) |
| baseline/score<50%/sonnet | 0.494 | 0.559 | 0.541 | 0.500 | 0.610 | 0.600 | 0.624 | 14-1 (p 0.000977) | 36-1 (p 5.53e-10) | 0.661 | 14-0 (p 0.000122) |
| baseline/score<50%/haiku | 0.494 | 0.559 | 0.471 | 0.418 | 0.559 | 0.475 | 0.532 | 13-3 (p 0.0213) | 26-3 (p 1.52e-05) | 0.644 | 14-1 (p 0.000977) |
| baseline/score<75%/sonnet | 0.747 | 0.746 | 0.741 | 0.727 | 0.763 | 0.735 | 0.744 | 23-1 (p 2.98e-06) | 70-1 (p 6.1e-20) | 0.814 | 23-0 (p 2.38e-07) |
| baseline/score<75%/haiku | 0.747 | 0.746 | 0.559 | 0.509 | 0.644 | 0.546 | 0.605 | 18-3 (p 0.00149) | 44-6 (p 3.24e-08) | 0.746 | 20-1 (p 2.1e-05) |
| baseline/always-on/sonnet | 0.000 | 0.000 | 0.335 | 0.300 | 0.390 | 0.335 | 0.390 | 0-0 (p 1) | 0-0 (p 1) | 0.424 | 0-0 (p 1) |
| baseline/always-on/haiku | 0.000 | 0.000 | 0.335 | 0.300 | 0.390 | 0.335 | 0.390 | 0-0 (p 1) | 0-0 (p 1) | 0.424 | 0-0 (p 1) |
| baseline/oracle/sonnet | 0.347 | 1.000 | 0.500 | 0.300 | 0.864 | 0.521 | 0.555 | 29-1 (p 5.77e-08) | 29-1 (p 5.77e-08) | 0.983 | 33-0 (p 2.33e-10) |
| baseline/oracle/haiku | 0.347 | 1.000 | 0.435 | 0.300 | 0.678 | 0.433 | 0.490 | 21-4 (p 0.000911) | 21-4 (p 0.000911) | 0.831 | 26-2 (p 3.03e-06) |
| best-of baseline, sonnet | 0.000 | 0.000 | 0.882 | 0.882 | 0.881 | - | - | 29-0 (p 3.73e-09) | 93-0 (p 2.02e-28) | 0.983 | 33-0 (p 2.33e-10) |
| best-of baseline, haiku | 0.000 | 0.000 | 0.676 | 0.636 | 0.746 | - | - | 21-0 (p 9.54e-07) | 58-0 (p 6.94e-18) | 0.864 | 26-0 (p 2.98e-08) |

High-confidence rows only, topical labels (61 turns): baseline 0.377, sonnet 0.852, haiku 0.590

## Triggers against the labelled switch

How well each observable trigger finds the primary switch turns (turns with a topical label and a previous turn).

| trigger | fires on | precision (switches among fired) | recall (fired among switches) |
|---|---|---|---|
| sender | 0.550 | 46/93 | 46/59 |
| project | 0.272 | 37/46 | 37/59 |
| score<10% | 0.101 | 10/17 | 10/59 |
| score<25% | 0.243 | 16/41 | 16/59 |
| score<50% | 0.491 | 33/83 | 33/59 |
| score<75% | 0.746 | 44/126 | 44/59 |
| always-on | 0.000 | 0/0 | 0/59 |
| oracle | 0.349 | 59/59 | 59/59 |

## Readers against each other

Topical labels, paired on the same turns; win = Sonnet hits and Haiku misses.

| turns | n | haiku | sonnet | wins-losses | p |
|---|---|---|---|---|---|
| overall | 170 | 0.618 | 0.871 | 44-1 | 2.61e-12 |
| continuation | 110 | 0.582 | 0.873 | 33-1 | 4.07e-09 |
| switch | 59 | 0.678 | 0.864 | 11-0 | 0.000977 |

Sonnet and Haiku return the same set on 6/170 turns. Sonnet's top 3 shares 0.51 files with the baseline's on average.

## Switch-definition sensitivity

Topical labels, against the baseline, for `sonnet`, `haiku`, `baseline/project/sonnet` (fixed before the reads).

| switch definition | labels | turns | n | method | baseline hit@3 | method hit@3 | wins-losses | p |
|---|---|---|---|---|---|---|---|---|
| disjoint, topical (primary) | topical | continuation | 110 | sonnet | 0.300 | 0.873 | 64-1 | 3.58e-18 |
| disjoint, topical (primary) | topical | continuation | 110 | haiku | 0.300 | 0.582 | 37-6 | 1.64e-06 |
| disjoint, topical (primary) | topical | continuation | 110 | baseline/project/sonnet | 0.300 | 0.373 | 8-0 | 0.00781 |
| disjoint, topical (primary) | topical | switch | 59 | sonnet | 0.390 | 0.864 | 29-1 | 5.77e-08 |
| disjoint, topical (primary) | topical | switch | 59 | haiku | 0.390 | 0.678 | 21-4 | 0.000911 |
| disjoint, topical (primary) | topical | switch | 59 | baseline/project/sonnet | 0.390 | 0.661 | 17-1 | 0.000145 |
| disjoint, all labels | topical | continuation | 127 | sonnet | 0.299 | 0.874 | 74-1 | 4.02e-21 |
| disjoint, all labels | topical | continuation | 127 | haiku | 0.299 | 0.606 | 45-6 | 1.83e-08 |
| disjoint, all labels | topical | continuation | 127 | baseline/project/sonnet | 0.299 | 0.378 | 10-0 | 0.00195 |
| disjoint, all labels | topical | switch | 42 | sonnet | 0.429 | 0.857 | 19-1 | 4.01e-05 |
| disjoint, all labels | topical | switch | 42 | haiku | 0.429 | 0.643 | 13-4 | 0.049 |
| disjoint, all labels | topical | switch | 42 | baseline/project/sonnet | 0.429 | 0.762 | 15-1 | 0.000519 |
| disjoint, topical at 15% | topical | continuation | 91 | sonnet | 0.319 | 0.923 | 55-0 | 5.55e-17 |
| disjoint, topical at 15% | topical | continuation | 91 | haiku | 0.319 | 0.626 | 34-6 | 8.36e-06 |
| disjoint, topical at 15% | topical | continuation | 91 | baseline/project/sonnet | 0.319 | 0.363 | 4-0 | 0.125 |
| disjoint, topical at 15% | topical | switch | 78 | sonnet | 0.346 | 0.808 | 38-2 | 1.49e-09 |
| disjoint, topical at 15% | topical | switch | 78 | haiku | 0.346 | 0.603 | 24-4 | 0.00018 |
| disjoint, topical at 15% | topical | switch | 78 | baseline/project/sonnet | 0.346 | 0.603 | 21-1 | 1.1e-05 |
| top-1 differs, topical | topical | continuation | 39 | sonnet | 0.333 | 0.897 | 22-0 | 4.77e-07 |
| top-1 differs, topical | topical | continuation | 39 | haiku | 0.333 | 0.487 | 10-4 | 0.18 |
| top-1 differs, topical | topical | continuation | 39 | baseline/project/sonnet | 0.333 | 0.333 | 0-0 | 1 |
| top-1 differs, topical | topical | switch | 130 | sonnet | 0.331 | 0.862 | 71-2 | 5.72e-19 |
| top-1 differs, topical | topical | switch | 130 | haiku | 0.331 | 0.654 | 48-6 | 3.26e-09 |
| top-1 differs, topical | topical | switch | 130 | baseline/project/sonnet | 0.331 | 0.515 | 25-1 | 8.05e-07 |
| set differs, all labels | topical | continuation | 3 | sonnet | 0.667 | 1.000 | 1-0 | 1 |
| set differs, all labels | topical | continuation | 3 | haiku | 0.667 | 1.000 | 1-0 | 1 |
| set differs, all labels | topical | continuation | 3 | baseline/project/sonnet | 0.667 | 0.667 | 0-0 | 1 |
| set differs, all labels | topical | switch | 166 | sonnet | 0.325 | 0.867 | 92-2 | 4.51e-25 |
| set differs, all labels | topical | switch | 166 | haiku | 0.325 | 0.608 | 57-10 | 4.04e-09 |
| set differs, all labels | topical | switch | 166 | baseline/project/sonnet | 0.325 | 0.470 | 25-1 | 8.05e-07 |
| sender project differs (no label) | topical | continuation | 123 | sonnet | 0.317 | 0.862 | 68-1 | 2.37e-19 |
| sender project differs (no label) | topical | continuation | 123 | haiku | 0.317 | 0.593 | 40-6 | 3.1e-07 |
| sender project differs (no label) | topical | continuation | 123 | baseline/project/sonnet | 0.317 | 0.317 | 0-0 | 1 |
| sender project differs (no label) | topical | switch | 46 | sonnet | 0.370 | 0.891 | 25-1 | 8.05e-07 |
| sender project differs (no label) | topical | switch | 46 | haiku | 0.370 | 0.674 | 18-4 | 0.00434 |
| sender project differs (no label) | topical | switch | 46 | baseline/project/sonnet | 0.370 | 0.891 | 25-1 | 8.05e-07 |

## Cost

Cumulative across all experiments.

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
| claude-sonnet-5-5: read sonnet | 2 requests | 0.049 |
| claude-haiku-5-5: read haiku | 2 requests | 0.002 |
| claude-sonnet-5-5: read sonnet cache probe | 1 requests | 0.006 |
| claude-sonnet-5-5: read sonnet | 168 requests | 0.922 |
| claude-haiku-5-5: read haiku | 168 requests | 0.047 |
| frontier total |  | 3.951 |

Jev USD is estimated at the router paper's rate ($1.21 per 28.8M input tokens). This experiment: claude-sonnet-5-5 $0.977 + claude-haiku-5-5 $0.049 = $1.026, about $0.0057, $0.0003 per turn for Sonnet and Haiku with the index as a cached prefix. A cascade pays that on the triggered share of turns only.
