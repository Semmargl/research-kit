---
title: "Report — Does isolated verification catch what self-review misses?"
type: report
status: final
created: 2026-07-18
updated: 2026-07-18
question: "When an AI agent reviews its own work versus a separate agent reviewing it with fresh context, does the isolated reviewer find defects the author missed?"
decision: "Whether to make isolated verification a mandatory step or an optional one."
confidence: Medium
---

# Does isolated verification catch what self-review misses?

> **Demo report — real data.** The findings below come from instrumented runs on the reference
> system this kit was extracted from. Source paths are internal, so they are described rather than
> linked. This report shows both the format and the evidence standard the kit holds itself to.

## TL;DR

**Yes, and the margin was not marginal.** Across three isolated verification runs on one code change,
the separate reviewer found three defects the author had already declared fixed — including one that
broke the exact feature the change was written to repair. Self-review found zero of the three.
Sample is small: one change, one codebase, three runs.

## Key findings

| # | Finding | Source | Tier |
|---|---|---|---|
| 1 | Three isolated runs surfaced three defects after the author reported the work complete | Reference system execution log, 2026-07-18 | A |
| 2 | One defect broke the primary feature of the change itself, intermittently | Same, run 1 | A |
| 3 | One defect was a "fix" that reproduced the original bug by a different mechanism | Same, run 2 | A |
| 4 | The author's own pre-check passed all items before each run | Same, checklist a–f | A |

## Detail

### 1 · The author's checklist passed; the isolated reviewer's did not

The change had a six-item checklist (a–f). The author ran it and recorded a pass. The first isolated
run — fresh context, given only the diff and the checklist, with none of the author's reasoning —
returned FAIL on item (f), metadata conventions, and then went further than the checklist asked.

### 2 · A defect in the feature the change existed to fix

The change added a mode that writes an evaluation record without an API key. The isolated reviewer
found that the code decided "is this argument a literal or a file path?" by calling a filesystem
existence check on the raw string. A long JSON literal exceeds the maximum filename length, so the
call raised `OSError: File name too long` instead of returning false.

It failed intermittently — the outcome depended on whether the input text happened to contain a `/`.
The feature worked in testing and broke on real data. Fixed by dispatching on the shape of the string
before touching the filesystem.

### 3 · A fix that reproduced the original bug

The original defect: scores were truncated by `int()`, losing half a point. The author replaced it
with `round()`. The second isolated run pointed out that Python's `round()` is half-to-even —
`round(4.5)` is `4`. The "fix" lost the same half point in the same direction for exactly the values
that motivated the fix. Corrected to explicit half-up.

This one is worth dwelling on: the author knew about the bug, chose the obvious repair, and verified
it by reading the code rather than by running the boundary case.

### 4 · The third run still found two more

A third run, again fresh, found an unhandled `IndexError` on a flag passed without a value, and one
limitation the team accepted and documented rather than fixed. Yield was declining but had not
reached zero by run three.

## What I could not verify

- **Generality.** One change, one codebase, one author. Whether the effect holds across teams and
  languages is untested here.
- **Attribution.** The isolated runs also had more attempts. Some of the yield may come from
  repetition rather than from isolation itself. A controlled comparison — three self-review passes
  against three isolated passes — was not run.
- **Cost.** Each isolated run costs a model call plus author time reading the report. Not measured.

## Confidence

**Medium** — the defects are documented facts with exact mechanisms, not impressions. But the sample
is one change and the isolation-versus-repetition confound is unresolved.

What would raise it: the controlled comparison above, across at least ten changes.

## Conclusions

*Mine, not the data's.*

Make isolated verification mandatory for changes to anything that verifies other work. The failure
mode observed twice here was not carelessness — it was an author checking work against the same
mental model that produced it. Repetition alone does not fix that; fresh context does.

The cheapest version is one isolated pass on anything that would be embarrassing to get wrong. Three
passes showed declining yield, so three is a ceiling, not a target.

## Sources

| # | Source | Type | Date | Tier |
|---|---|---|---|---|
| 1 | Execution report of the instrumented change, reference system | Primary record | 2026-07-18 | A |
| 2 | Evaluation record written by the repaired feature | Primary artifact | 2026-07-18 | A |
| 3 | Python documentation, `round()` banker's rounding behaviour | Primary docs | — | A |
