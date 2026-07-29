---
name: capture_url
description: Turns an external source — URL, pasted article, paper, transcript — into a structured
  research note. Use when the user says "save this", "capture this article", "add this to the notes",
  or pastes a link to keep. Raw capture only; never synthesises into conclusions.
---

# Capture URL

One job: an external source becomes a well-formed note, ready for later extraction. You capture
what the source says. You do not decide what it means — that is `report_builder`'s job.

## Procedure

### 1 · Identify the type

| Input | Type | Destination |
|---|---|---|
| Article, blog, documentation | `article` | `00-capture/articles/` |
| Academic paper, preprint | `paper` | `00-capture/papers/` |
| Video, talk, podcast | `video` | `00-capture/videos/` |
| Pasted text, transcript | `article` | `00-capture/articles/` |

### 2 · Fetch

Fetch the page and extract: title, author, publication, published date, a 3-bullet TL;DR,
5–8 key claims, 1–3 quotes worth keeping.

If the fetch fails, ask the user to paste the text. Never write a note from the URL alone —
a note describing a page you could not read is worse than no note.

### 3 · Check for duplicates

List the target folder and compare the `url:` field of existing notes. Duplicate → tell the user
which note already exists and stop.

### 4 · Name the file

`<type>_<slug>_<source>.md` — `type` is the row you picked in the table above (`article`,
`paper` or `video`), so a paper is `paper_<slug>_<source>.md` and a video is
`video_<slug>_<source>.md`. Slug is the title in `snake_case`, max 6 words, no stop words;
source is the publication domain without the TLD.

Example: `article_context_window_overflow_patterns_substack.md`

### 5 · Fill the note

```yaml
---
title: "Article — <short title>"
type: research
status: draft
created: <today>
updated: <today>
source_type: article
url: "<url or 'pasted'>"
author: "<author or 'unknown'>"
publication: "<publication>"
published_date: <date or "unknown">
source_tier: A | B | C | D
extraction_deadline: <today + 7 days>
---
```

Body sections, in order:

- `## Source` — URL, author, publication, date, tier and why that tier.
- `## TL;DR` — 3 bullets, plain statements, no hedging.
- `## Key claims` — 5–8 bullets, each as the source states it.
- `## Evidence cited` — the concrete numbers and examples the source gives.
- `## Quotes` — 1–3, in blockquotes, verbatim.
- `## Open questions` — what the source leaves unanswered.
- `## Related` — leave empty; synthesis fills it later.

### 6 · Report back

File path, the TL;DR, the source tier, and the extraction deadline.

## Hard rules

- Only write into the capture folders. A capture note never lands in reference or reports.
- Never synthesise across sources here. One source, one note.
- Never guess a missing date or author. Write `unknown`.
- Keep the source's own framing in `## Key claims`, including claims you doubt. Record your doubt in
  `## Open questions` instead of quietly filtering the claim out.
