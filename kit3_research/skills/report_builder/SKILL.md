---
name: report_builder
description: Turns captured notes and search results into a structured deliverable — comparison,
  gap map, or synthesis note. Use for "compare X and Y", "what do we know about Z", "what are we
  missing", "write this up as a report". Produces markdown, and an HTML view when the result is
  mostly structure.
---

# Report Builder

Turns accumulated material into something a reader can act on. Three modes — pick one by what the
user asked for.

## Mode A — Comparison

**Trigger:** "compare X and Y", "which should we use", "trade-offs between".

1. Read the relevant capture and reference notes. If coverage is thin, say so — do not fill gaps
   with plausible-sounding generalities.
2. Build a decision matrix: rows are criteria, columns are options. Always include use-case fit,
   effort or cost, and *when not to use*.
3. Write the recommendation as one paragraph: "For <context>, prefer X because <reason>.
   Choose Y when <condition>."
4. State confidence and what is missing.

Every mode below obeys `rules/report_format.md`: TL;DR first, each claim carrying its source,
confidence stated, and a full source list at the end. The blocks here show the mode-specific
middle — they do not replace those four requirements.

```markdown
## X vs Y

**TL;DR:** <the answer in 1-3 lines, before any table>

| Criterion | X | Y |
|---|---|---|
| Use-case fit | | |
| Effort / cost | | |
| Failure modes | | |
| When NOT to use | | |

**Recommendation:** …
**Confidence:** High / Medium / Low — <what is missing>

## Sources
| # | Source | Publisher | Date | Tier |
|---|---|---|---|---|
```

## Mode B — Gap map

**Trigger:** "what are we missing", "where are the blind spots".

1. Read the index files for the scope given.
2. Cross-check claimed coverage against actual notes: a topic listed in an index with no note behind
   it is a gap, not coverage.
3. Produce three buckets — covered well, covered partially, missing entirely — and a priority list
   of what to write next, with a one-line reason each.

## Mode C — Synthesis note

**Trigger:** "write this up", "distil what we know about X".

1. Search the notes for the topic, then read only the matches. Do not read the whole corpus.
2. Separate established knowledge from open hypotheses. Label which is which.
3. Draft the note, show it to the user, and write the file only after they confirm.

## Output as HTML

When the result is mostly structure — a matrix, a layered stack, a flow — render it as a single-file
HTML view alongside the markdown. Rules: light theme, system font stack, no external assets, no
build step, collapsible `<details>` for the detail layer so the top level stays scannable.

**Start from `templates/report_html_template.html`.** It already encodes every rule above — a
TL;DR box, an established-vs-open split, a comparison table with a "not covered" cell, a worked
`<details>` block and a sources list — with the design tokens inline. Copy it, replace the
`[[ ... ]]` markers, delete the sections you do not need. Do not hand-roll the CSS each time.

Markdown is the source of truth; the HTML is a view. If they disagree, the markdown is right.

## Hard rules

- Never invent a fact to complete a table. An empty cell reading "not covered" is the correct output.
- Never write into the knowledge base without showing the draft first.
- Never modify existing notes as a side effect. Propose the change; let the user apply it.
- Cap the scope at about 20 source notes per run. More than that, ask the user to narrow it —
  a synthesis that skims 60 notes is a summary of nothing.
- Always close with confidence level and what would raise it.
