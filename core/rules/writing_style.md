# Writing Style

Everything the agents produce follows these rules. This governs output, not chat replies —
chat replies follow the response protocol in the Claude OS Core block of `CLAUDE.md`.

## Tone

- Direct and declarative. "Do X", not "You should consider doing X".
- No filler: drop "in summary", "it is worth noting", "as we can see".
- Active voice.

## Structure

- One idea per paragraph.
- Headings only when they aid navigation. No heading for a section under two paragraphs.
- Lists only for genuinely enumerable items (3+).
- Tables for any comparison of 2+ items across 2+ attributes.

## Code and references

- Fence code blocks with a language tag.
- External references go at the bottom under `## Sources`, with the URL.
- Never present a generated claim as sourced. If it is unsourced, say so.

## Document layers

Three layers, three format budgets. Put a file in the layer that matches what it *is*.

| Layer | Answers | Budget |
|---|---|---|
| Reference | "What is X? What are the tradeoffs?" | Detail is correct here: failure modes, security notes, config options. |
| Method | "I know what I want — show me how." | Max ~40 rendered lines. Config snippet over prose. No "Why" section. |
| Record | "What actually happened?" | Written as records: "We found X", not "You should X". |

A method file that starts explaining *why* belongs in reference. Move it, do not grow it.
