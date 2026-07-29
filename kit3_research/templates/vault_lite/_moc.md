---
title: "{{PROJECT_NAME}} — Research Map"
type: moc
status: active
updated: <date>
---

# Research Map

Top-level entry point. Three tiers, one rule: a file goes where it belongs by **what it is**,
not by what it is about.

| Tier | Holds | Test |
|---|---|---|
| `00-capture/` | Raw sources, one note per source, unprocessed | "Someone else wrote this" |
| `10-reference/` | Entities you keep returning to: tools, concepts, organisations | "What is X, and what are its trade-offs?" |
| `30-reports/` | Finished deliverables: research reports, comparisons, gap maps | "This was produced, on a date, for a reader" |

Anything that does not fit these three is probably a working file. Keep it out of the tree.

## Tiers

- [[00-capture/_index]] — raw material awaiting extraction
- [[10-reference/_index]] — the entity layer
- [[30-reports/_index]] — finished work

## Conventions

- Filenames `snake_case`, no spaces or hyphens.
- Every folder carries an `_index.md`.
- Every note carries frontmatter with at least `title`, `type`, `status`, `created`, `updated`.
- Captures carry `url`, `published_date` and `source_tier` as well.
