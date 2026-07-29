# Quickstart — Research Kit

Fifteen minutes, three tasks. Do them in order; each one uses what the last produced.

## Before you start

Kit installed, and a fresh Claude session opened in the project folder.

## 1 · Capture a source (3 min)

Paste a link you actually care about and say:

```
Capture this: <url>
```

You get a note in `00-capture/articles/` with a TL;DR, key claims, quotes, a source tier and an
extraction deadline.

**Look at the source tier.** If it graded a marketing blog as tier C, that is the kit working.
Tier C means: fine as a lead, not something a conclusion should rest on.

## 2 · Run a small research question (7 min)

Pick a question you would otherwise google for twenty minutes. Ask:

```
Research this properly: <question>. I need it sourced.
```

The router sends it to the deep lane. Watch for these three moments:

1. It restates the question and asks what decision it feeds. Answer honestly — "no decision, just
   curious" is a valid answer and changes how much work it does.
2. It searches deliberately different angles, including the case against.
3. It attacks its own findings before writing.

The report arrives TL;DR-first, claims carrying their sources, with a confidence level and an
explicit list of what it could not verify.

## 3 · Check the citations (5 min)

In a **new** session — this matters — say:

```
Read .claude/agents/citation_checker.md and check <path to the report>.
```

You get a table: each claim, its cited source, and SUPPORTED / PARTIAL / UNSUPPORTED / MISSING.

Expect a few PARTIALs on the first run. That is the normal state of AI-written research, and seeing
it is the point of the exercise. UNSUPPORTED or MISSING means fix before sending.

## Why a new session

A checker that watched the report being written inherits its assumptions and will wave through the
same mistakes. Isolation is not ceremony — it is the whole mechanism.

## Next

- Adjust `.claude/rules/source_grading.md` — add the domains that are tier A *for your field*.
- Try `report_builder` in comparison mode: "compare X and Y for <your context>".
- Past a few hundred notes, consider `scripts/embeddings_search/` for semantic search.
