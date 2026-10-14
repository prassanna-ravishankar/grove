# grove fourth experiment: usage labels

170 inbound orchestrator turns (2026-10-06 to 2026-10-14: every delivered message in the 14-day window that carried a recall block), 150 memory files. Labels: first pass by claude-opus-5-5 from the turn and the memory index; 109 of 170 rows are marked low confidence. The orchestrator spot-checked 30 rows (20 low, 10 high confidence): 26 agree, 4 disagree, all four in the low-confidence pool.

Coverage, not recall: 21 of the 109 low-confidence rows give as their reason that the referent is unclear or that no memory covers it (keyword match on the labeller's reason). Three of the four spot-check disagreements were of this kind.

Always-on memories: labelled useful on more than 25% of turns, treated as format rather than topic: `memory/feedback_telegram_message_size.md` (58), `memory/peer_to_peer_review_iteration.md` (48), `memory/routing_refactor_gate.md` (53). At 15% the list grows to 7. `topical` labels drop the 25% list; 0 turns are left with no topical memory and are excluded from topical hit rates.

Question: the cascade result (results-cascade.md) was measured against labels from claude-opus-5-5 reading the memory index. Does it hold against what the orchestrator actually used, and how far did the Opus labels agree with use?

Usage labels. All 170 turns are in one orchestrator session. Each turn was matched to its inbound message in the session transcript by its text (170/170 matched, each to a distinct message; journal-to-transcript gap median 53 s, max 832 s). A memory is used on a turn when its file name (memory/*.md, comms.md, projects.md) or a [[wikilink]] to it appears in the assistant's response before the next inbound message, including messages queued mid-turn: tool inputs (Read paths, Bash commands, Edit and Write targets, heredocs), visible text, and thinking. Thinking is mostly not recorded in the transcript: 0 turns have a memory named in thinking. Tool inputs are split by what the call does to the file: `created` (Write, or a single `>` redirection), `edited` (Edit, `>>`, tee, in-place sed, Python writes), otherwise `read`. The primary view drops memories created during the turn: they did not exist when the turn arrived, so no recall could have returned them (the corpus snapshot is later and holds them, the leakage noted in the first experiment). `as briefed` keeps them. `reads only` also drops memories edited during the turn, leaving those the orchestrator only looked at or named.

Two biases to keep in view. The orchestrator saw the recorded recall block, so names it repeats from that block count as used: that favours `recorded` and, through their overlap, the baseline. And it read memory mostly by grepping the directory or by the recall block itself, so many uses leave no file name behind: coverage is partial, and only turns with at least one used memory are scored. The always-on filter is the same >25% list as before, taken from the Opus labels.

## Headline

Usage labels (topical) cover 33/170 turns. Against them, overall: `recorded` 0.576 vs baseline 0.636 (0-2, p = 0.5); `haiku` 0.303 vs baseline 0.636 (1-12, p = 0.00342); `sonnet` 0.485 vs baseline 0.636 (4-9, p = 0.267); `baseline/project/sonnet` 0.636 vs baseline 0.636 (0-0, p = 1); `baseline/sender/sonnet` 0.424 vs baseline 0.636 (1-8, p = 0.0391). On switches: `recorded` 0.625 vs 0.625 (0-0, p = 1); `haiku` 0.500 vs 0.625 (1-2, p = 1); `sonnet` 0.500 vs 0.625 (1-2, p = 1); `baseline/project/sonnet` 0.625 vs 0.625 (0-0, p = 1); `baseline/sender/sonnet` 0.375 vs 0.625 (0-2, p = 0.5). Usage against Opus topical labels: mean Jaccard 0.142, usage a subset of the labelled set on 0.303 of scored turns, 0.383 of used memories labelled.

Reading. The usage signal does not confirm the cascade result, and on the turns it covers it leans the other way. Only 33/170 turns leave a memory file name behind, 8 of them switches, so it cannot answer the switch question. On those turns the baseline is ahead of Sonnet (0.485 vs 0.636, 4-9, p = 0.267) and of the sender cascade (0.424 vs 0.636, 1-8, p = 0.0391), and well ahead of Haiku (0.303 vs 0.636, 1-12, p = 0.00342). The project cascade ties exactly: its trigger does not fire on any covered turn where Sonnet and the baseline differ. What `used` measures here: of the 57 mentions that are not file creations, 45 are edits (the orchestrator appending a recurrence or a status line), 8 are reads by name, 4 are names in visible text, and thinking is not recorded. So `used` mostly means `updated in response to the turn`. It is also biased towards whatever recall showed: 0.447 of used memories were in the recall block the orchestrator saw, against 0.111 of the Opus-labelled memories on the same turns. The baseline's lead is not corpus leakage: `recorded`, computed before any edit, scores 0.576 and still leads Sonnet (5-8, p = 0.581). Agreement between usage and the Opus topical labels is low: mean Jaccard 0.142, 0.383 of used memories labelled, usage a subset of the labelled set on 0.303 of turns. So the third experiment's margin was agreement with the labeller, not measurably agreement with use. Because usage is selected by the recall block, low agreement does not show the labels are wrong either. Neither label set is ground truth. Settling it needs an arm the orchestrator is actually shown, for example the reader's top 3 placed beside the recall block on a share of turns with what it then reads logged, or human labels on a sample.

## Coverage

| labels | turns with a used memory | continuation | switch | mean used per scored turn |
|---|---|---|---|---|
| usage, topical (primary) | 33/170 | 25 | 8 | 1.42 |
| usage, all | 33/170 | 25 | 8 | 1.45 |
| usage, topical, as briefed | 34/170 | 25 | 9 | 1.74 |
| usage, topical, reads only | 4/170 | 2 | 2 | 1.00 |

(turn, memory) mentions by source, before any filter (a memory can appear under several): read 8, edited 45, created 12, text 4, thinking 0.

## Usage against the Opus labels

Per scored turn (at least one used memory). `in recorded` is the share of memories that were in the recall block the orchestrator saw, for usage and, on the same turns, for the Opus labels.

| labels | turns | mean Jaccard | usage ⊆ labelled | any overlap | used memories labelled | used memories in recorded | labelled memories in recorded |
|---|---|---|---|---|---|---|---|
| topical | 33 | 0.142 | 0.303 | 0.424 | 0.383 | 0.447 | 0.111 |
| all | 33 | 0.127 | 0.303 | 0.455 | 0.396 | 0.438 | 0.112 |

## hit@3 against usage labels

Per turn, win = method hits and baseline misses. Exact two-sided sign test, ties dropped.

Switch = the primary definition (topical Opus label sets disjoint from the previous turn's); n per view in the coverage table.

| labels | method | overall | continuation | switch |
|---|---|---|---|---|
| usage, topical (primary) | baseline | 0.636 | 0.640 | 0.625 |
| usage, topical (primary) | recorded | 0.576 | 0.560 | 0.625 |
| usage, topical (primary) | haiku | 0.303 | 0.240 | 0.500 |
| usage, topical (primary) | sonnet | 0.485 | 0.480 | 0.500 |
| usage, topical (primary) | baseline/project/sonnet | 0.636 | 0.640 | 0.625 |
| usage, topical (primary) | baseline/sender/sonnet | 0.424 | 0.440 | 0.375 |
| usage, all | baseline | 0.636 | 0.640 | 0.625 |
| usage, all | recorded | 0.576 | 0.560 | 0.625 |
| usage, all | haiku | 0.333 | 0.240 | 0.625 |
| usage, all | sonnet | 0.485 | 0.480 | 0.500 |
| usage, all | baseline/project/sonnet | 0.636 | 0.640 | 0.625 |
| usage, all | baseline/sender/sonnet | 0.424 | 0.440 | 0.375 |
| usage, topical, as briefed | baseline | 0.706 | 0.680 | 0.778 |
| usage, topical, as briefed | recorded | 0.559 | 0.560 | 0.556 |
| usage, topical, as briefed | haiku | 0.441 | 0.400 | 0.556 |
| usage, topical, as briefed | sonnet | 0.588 | 0.600 | 0.556 |
| usage, topical, as briefed | baseline/project/sonnet | 0.706 | 0.680 | 0.778 |
| usage, topical, as briefed | baseline/sender/sonnet | 0.588 | 0.600 | 0.556 |
| usage, topical, reads only | baseline | 0.250 | 0.500 | 0.000 |
| usage, topical, reads only | recorded | 0.250 | 0.500 | 0.000 |
| usage, topical, reads only | haiku | 0.250 | 0.500 | 0.000 |
| usage, topical, reads only | sonnet | 0.500 | 0.500 | 0.500 |
| usage, topical, reads only | baseline/project/sonnet | 0.250 | 0.500 | 0.000 |
| usage, topical, reads only | baseline/sender/sonnet | 0.250 | 0.500 | 0.000 |

Paired against the baseline. `sender project differs` is the label-free switch definition, independent of Opus.

| labels | switch definition | turns | n | method | baseline hit@3 | method hit@3 | wins-losses | p |
|---|---|---|---|---|---|---|---|---|
| usage, topical (primary) | disjoint, topical (primary) | overall | 33 | recorded | 0.636 | 0.576 | 0-2 | 0.5 |
| usage, topical (primary) | disjoint, topical (primary) | switch | 8 | recorded | 0.625 | 0.625 | 0-0 | 1 |
| usage, topical (primary) | disjoint, topical (primary) | overall | 33 | haiku | 0.636 | 0.303 | 1-12 | 0.00342 |
| usage, topical (primary) | disjoint, topical (primary) | switch | 8 | haiku | 0.625 | 0.500 | 1-2 | 1 |
| usage, topical (primary) | disjoint, topical (primary) | overall | 33 | sonnet | 0.636 | 0.485 | 4-9 | 0.267 |
| usage, topical (primary) | disjoint, topical (primary) | switch | 8 | sonnet | 0.625 | 0.500 | 1-2 | 1 |
| usage, topical (primary) | disjoint, topical (primary) | overall | 33 | baseline/project/sonnet | 0.636 | 0.636 | 0-0 | 1 |
| usage, topical (primary) | disjoint, topical (primary) | switch | 8 | baseline/project/sonnet | 0.625 | 0.625 | 0-0 | 1 |
| usage, topical (primary) | disjoint, topical (primary) | overall | 33 | baseline/sender/sonnet | 0.636 | 0.424 | 1-8 | 0.0391 |
| usage, topical (primary) | disjoint, topical (primary) | switch | 8 | baseline/sender/sonnet | 0.625 | 0.375 | 0-2 | 0.5 |
| usage, topical (primary) | sender project differs (no label) | switch | 3 | recorded | 0.333 | 0.333 | 0-0 | 1 |
| usage, topical (primary) | sender project differs (no label) | switch | 3 | haiku | 0.333 | 0.333 | 0-0 | 1 |
| usage, topical (primary) | sender project differs (no label) | switch | 3 | sonnet | 0.333 | 0.333 | 0-0 | 1 |
| usage, topical (primary) | sender project differs (no label) | switch | 3 | baseline/project/sonnet | 0.333 | 0.333 | 0-0 | 1 |
| usage, topical (primary) | sender project differs (no label) | switch | 3 | baseline/sender/sonnet | 0.333 | 0.333 | 0-0 | 1 |
| usage, all | disjoint, topical (primary) | overall | 33 | recorded | 0.636 | 0.576 | 0-2 | 0.5 |
| usage, all | disjoint, topical (primary) | switch | 8 | recorded | 0.625 | 0.625 | 0-0 | 1 |
| usage, all | disjoint, topical (primary) | overall | 33 | haiku | 0.636 | 0.333 | 2-12 | 0.0129 |
| usage, all | disjoint, topical (primary) | switch | 8 | haiku | 0.625 | 0.625 | 2-2 | 1 |
| usage, all | disjoint, topical (primary) | overall | 33 | sonnet | 0.636 | 0.485 | 4-9 | 0.267 |
| usage, all | disjoint, topical (primary) | switch | 8 | sonnet | 0.625 | 0.500 | 1-2 | 1 |
| usage, all | disjoint, topical (primary) | overall | 33 | baseline/project/sonnet | 0.636 | 0.636 | 0-0 | 1 |
| usage, all | disjoint, topical (primary) | switch | 8 | baseline/project/sonnet | 0.625 | 0.625 | 0-0 | 1 |
| usage, all | disjoint, topical (primary) | overall | 33 | baseline/sender/sonnet | 0.636 | 0.424 | 1-8 | 0.0391 |
| usage, all | disjoint, topical (primary) | switch | 8 | baseline/sender/sonnet | 0.625 | 0.375 | 0-2 | 0.5 |
| usage, all | sender project differs (no label) | switch | 3 | recorded | 0.333 | 0.333 | 0-0 | 1 |
| usage, all | sender project differs (no label) | switch | 3 | haiku | 0.333 | 0.333 | 0-0 | 1 |
| usage, all | sender project differs (no label) | switch | 3 | sonnet | 0.333 | 0.333 | 0-0 | 1 |
| usage, all | sender project differs (no label) | switch | 3 | baseline/project/sonnet | 0.333 | 0.333 | 0-0 | 1 |
| usage, all | sender project differs (no label) | switch | 3 | baseline/sender/sonnet | 0.333 | 0.333 | 0-0 | 1 |
| usage, topical, as briefed | disjoint, topical (primary) | overall | 34 | recorded | 0.706 | 0.559 | 0-5 | 0.0625 |
| usage, topical, as briefed | disjoint, topical (primary) | switch | 9 | recorded | 0.778 | 0.556 | 0-2 | 0.5 |
| usage, topical, as briefed | disjoint, topical (primary) | overall | 34 | haiku | 0.706 | 0.441 | 0-9 | 0.00391 |
| usage, topical, as briefed | disjoint, topical (primary) | switch | 9 | haiku | 0.778 | 0.556 | 0-2 | 0.5 |
| usage, topical, as briefed | disjoint, topical (primary) | overall | 34 | sonnet | 0.706 | 0.588 | 2-6 | 0.289 |
| usage, topical, as briefed | disjoint, topical (primary) | switch | 9 | sonnet | 0.778 | 0.556 | 0-2 | 0.5 |
| usage, topical, as briefed | disjoint, topical (primary) | overall | 34 | baseline/project/sonnet | 0.706 | 0.706 | 0-0 | 1 |
| usage, topical, as briefed | disjoint, topical (primary) | switch | 9 | baseline/project/sonnet | 0.778 | 0.778 | 0-0 | 1 |
| usage, topical, as briefed | disjoint, topical (primary) | overall | 34 | baseline/sender/sonnet | 0.706 | 0.588 | 1-5 | 0.219 |
| usage, topical, as briefed | disjoint, topical (primary) | switch | 9 | baseline/sender/sonnet | 0.778 | 0.556 | 0-2 | 0.5 |
| usage, topical, as briefed | sender project differs (no label) | switch | 4 | recorded | 0.250 | 0.250 | 0-0 | 1 |
| usage, topical, as briefed | sender project differs (no label) | switch | 4 | haiku | 0.250 | 0.250 | 0-0 | 1 |
| usage, topical, as briefed | sender project differs (no label) | switch | 4 | sonnet | 0.250 | 0.250 | 0-0 | 1 |
| usage, topical, as briefed | sender project differs (no label) | switch | 4 | baseline/project/sonnet | 0.250 | 0.250 | 0-0 | 1 |
| usage, topical, as briefed | sender project differs (no label) | switch | 4 | baseline/sender/sonnet | 0.250 | 0.250 | 0-0 | 1 |
| usage, topical, reads only | disjoint, topical (primary) | overall | 4 | recorded | 0.250 | 0.250 | 0-0 | 1 |
| usage, topical, reads only | disjoint, topical (primary) | switch | 2 | recorded | 0.000 | 0.000 | 0-0 | 1 |
| usage, topical, reads only | disjoint, topical (primary) | overall | 4 | haiku | 0.250 | 0.250 | 0-0 | 1 |
| usage, topical, reads only | disjoint, topical (primary) | switch | 2 | haiku | 0.000 | 0.000 | 0-0 | 1 |
| usage, topical, reads only | disjoint, topical (primary) | overall | 4 | sonnet | 0.250 | 0.500 | 1-0 | 1 |
| usage, topical, reads only | disjoint, topical (primary) | switch | 2 | sonnet | 0.000 | 0.500 | 1-0 | 1 |
| usage, topical, reads only | disjoint, topical (primary) | overall | 4 | baseline/project/sonnet | 0.250 | 0.250 | 0-0 | 1 |
| usage, topical, reads only | disjoint, topical (primary) | switch | 2 | baseline/project/sonnet | 0.000 | 0.000 | 0-0 | 1 |
| usage, topical, reads only | disjoint, topical (primary) | overall | 4 | baseline/sender/sonnet | 0.250 | 0.250 | 0-0 | 1 |
| usage, topical, reads only | disjoint, topical (primary) | switch | 2 | baseline/sender/sonnet | 0.000 | 0.000 | 0-0 | 1 |
| usage, topical, reads only | sender project differs (no label) | switch | 1 | recorded | 0.000 | 0.000 | 0-0 | 1 |
| usage, topical, reads only | sender project differs (no label) | switch | 1 | haiku | 0.000 | 0.000 | 0-0 | 1 |
| usage, topical, reads only | sender project differs (no label) | switch | 1 | sonnet | 0.000 | 0.000 | 0-0 | 1 |
| usage, topical, reads only | sender project differs (no label) | switch | 1 | baseline/project/sonnet | 0.000 | 0.000 | 0-0 | 1 |
| usage, topical, reads only | sender project differs (no label) | switch | 1 | baseline/sender/sonnet | 0.000 | 0.000 | 0-0 | 1 |

Sonnet against `recorded`, primary usage labels. The recorded block was computed at delivery, before the orchestrator edited anything in response, so it carries none of the corpus leakage the ported baseline has.

| turns | n | recorded | sonnet | wins-losses | p |
|---|---|---|---|---|---|
| overall | 33 | 0.576 | 0.485 | 5-8 | 0.581 |
| continuation | 25 | 0.560 | 0.480 | 4-6 | 0.754 |
| switch | 8 | 0.625 | 0.500 | 1-2 | 1 |

## Reader cost per turn

List price. Index and message tokens from count_tokens on the stored requests (no generation); output tokens (including thinking) implied by the logged spend of the 170 reads. `warm` reads the index from the prompt cache, as in this run; `cold` pays full input price for it. A cascade pays this on the triggered share of turns only; the baseline costs no API call.

| reader | model | index tokens | mean message tokens | mean output tokens | USD per call, warm | USD per call, cold | logged USD per call |
|---|---|---|---|---|---|---|---|
| sonnet | claude-sonnet-5-5 | 13,529 | 697 | 124 | 0.00534 | 0.02970 | 0.00571 |
| haiku | claude-haiku-5-5 | 13,529 | 697 | 135 | 0.00027 | 0.00149 | 0.00029 |

Per turn at the cascade call shares, warm: `baseline/project/sonnet` 0.271 x 0.00534 = $0.00145, `baseline/sender/sonnet` 0.547 x 0.00534 = $0.00292.

## Cost of this experiment

No generation calls: the reads are those stored by the third experiment. count_tokens calls only.
