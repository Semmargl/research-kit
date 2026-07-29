---
name: deep_research
description: Multi-angle research with adversarial verification. Use when the answer has to hold up
  in front of a client, a manager or a decision — not a quick fact. Fans a question out into
  sub-questions, searches each, then attacks its own findings before writing anything.
---

# Deep Research

For questions where being wrong is expensive. A quick fact does not belong here — route it to a
direct search and answer in two lines.

## Official skill

Anthropic ships its own `deep-research` skill. This kit does not repackage it. If you have it
installed, use it for the search fan-out in step 2 and keep steps 3–5 below, which are the parts
that decide whether the output is trustworthy. Install it from Anthropic's own distribution —
do not copy it out of another project.

## Procedure

### 1 · Frame the question

Write the question in one sentence, then write what a *complete* answer would contain. If you cannot
describe the shape of a complete answer, the question is underspecified — ask before searching.

Record explicitly:

- What decision this feeds. Research with no decision behind it has no stopping rule.
- What would change the answer.
- Scope: which market, which version, which time window.

### 2 · Fan out

Break the question into 3–6 sub-questions that can be searched independently. Cover deliberately
different angles:

- The direct question.
- The opposite case: who says this does not work, and why.
- The base rate: what usually happens with things like this.
- The primary record: docs, filings, source, dataset.
- The recency check: what changed most recently.

Search each. Collect sources with publisher and date. Grade each source per `.claude/rules/source_grading.md`.

### 3 · Attack your own findings

This is the step that separates research from a summary. Before writing, run each finding through:

| Attack | Question |
|---|---|
| Source quality | Is this tier A/B, or am I leaning on a blog restating someone else? |
| Independence | Do my "multiple sources" trace back to one origin? |
| Recency | Is this still true, or true as of two years ago? |
| Selection | Did I search terms that could only confirm what I expected? |
| Number integrity | Do the units, scope and date survive from source to my sentence? |
| Missing counter-case | Have I searched for the strongest argument against this? |

A finding that fails an attack is either re-searched or reported with its weakness stated.

### 4 · Write

Follow `.claude/rules/report_format.md`: TL;DR, key findings with source tiers, detail, confidence and gaps,
sources. Answer first, evidence attached at the point of the claim.

### 5 · Verify

Run the `citation_checker` agent against the draft, in a fresh context. Fix what it flags.
Do not skip this because the draft "feels" solid — feeling solid is exactly the state in which
citation drift goes unnoticed.

## Stopping rules

Stop when new searches stop changing the answer, or when you can state the answer, its confidence
and what would change it. Stop and say so when the question cannot be answered from available
sources — that is a finding, not a failure.

## Hard rules

- Never present an unsourced claim as sourced.
- Never let a number cross from source to draft without its units, scope and date.
- Never resolve a genuine disagreement between good sources by picking one silently.
- If you did not search, do not imply that you did.
