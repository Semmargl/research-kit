# Source Grading

Not all sources carry the same weight. Grade before you cite, and show the grade when confidence matters.

## Tiers

| Tier | What | Use |
|---|---|---|
| A — primary | The thing itself: official docs, the paper, the filing, the source code, the press release, the dataset. | Cite directly. Preferred for every factual claim. |
| B — qualified secondary | Reporting or analysis with named authors and its own primary citations. | Fine, but follow the link to tier A when the claim is load-bearing. |
| C — unqualified secondary | Blog posts, summaries, aggregators, unnamed authors, content marketing. | Use for leads and orientation. Do not let a claim rest on this alone. |
| D — unreliable | AI-generated content farms, undated pages, screenshots without provenance, "someone said". | Not a source. Use it to find a real one, then cite that. |

## Rules

1. **A load-bearing claim needs tier A or B.** If only C is available, state the claim as unverified
   and say what would confirm it.
2. **Follow the chain.** If B cites A, cite A. A secondary source restating a primary one is a place
   where numbers drift.
3. **Date every source.** An undated page about a fast-moving topic is tier C at best regardless of
   who published it.
4. **Recency beats authority for changing facts.** Prices, versions, officeholders, legal status:
   the newest reliable source wins over the most prestigious old one. **One exception, and it is
   not optional:** when two sources give different values for the *same* figure, rank by
   authority first — a structured API outranks a rendered page. "Newer" is a property of the
   page, not of the number on it. See `citation_checker`, Hard rules.
5. **Two independent sources for anything surprising.** Independent means not sharing an origin —
   six outlets rewriting one wire story is one source.
6. **Name the conflict.** A vendor benchmark of its own product is usable if you say whose benchmark it is.

## Domain trust list

Maintain a short per-project list of domains that count as tier A for this work. Examples of what
belongs there: the official docs of the tools in use, the relevant regulator, the standards body,
the primary data publisher for the field.

```
# trusted_domains
# one per line, comment out rather than delete so the reasoning stays visible
```

Keep it under about 20 entries. A long trust list is one nobody reads, and it hides the judgement
call it was supposed to make explicit.

## When sources disagree

Report the disagreement rather than picking a winner silently. State: what each says, the tier of
each, the date of each, and which one you would act on and why. A research report that hides a real
disagreement is worse than one that never looked.
