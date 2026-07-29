# Research Kit

**Analyst-grade research: multi-angle search, verified sources, ready reports.**

The problem this solves: an ordinary AI answer has no sources, so you cannot put it in front of a
client or a manager. You end up re-checking it yourself, which costs more than doing the research
by hand would have.

## What you get

| Piece | Does |
|---|---|
| `research_router` agent | Recognises the request type and picks one lane. Quick facts stay quick. |
| `citation_checker` agent | Isolated pass: does each source actually say what the draft claims? |
| `deep_research` skill | Fan out into sub-questions, search each, then attack your own findings. |
| `capture_url` skill | A URL becomes a structured note, deduplicated, with a source tier. |
| `report_builder` skill | Comparisons, gap maps and synthesis notes, plus an HTML view. |
| `source_grading` rule | A/B/C/D tiers, chain-following, the rule for surprising claims. |
| `report_format` rule | TL;DR first, claims carry their sources, confidence stated. |
| `vault_lite` templates | Three-tier note skeleton: capture, reference, reports. |
| `embeddings_search` | Optional local semantic search. Off by default. |

## The part that matters

Two mechanisms do the real work:

1. **Adversarial verification.** Before writing, every finding is attacked: is the source primary,
   are my "multiple sources" independent, is this still current, did I only search for confirmation?
2. **Isolated citation checking.** A separate pass with fresh context reads the sources and marks
   each claim SUPPORTED / PARTIAL / UNSUPPORTED / MISSING. The author never grades their own work.

Most AI research failures are not invented facts. They are hedges quietly dropped, numbers arriving
without their scope, and three citations stacked after four claims. Those are the failures these
two mechanisms are built to catch.

## Install

See `core/install/INSTALL.en.md` (or `.ru.md`) **in the kit archive** — the install docs stay in the kit folder and are deliberately not copied into your project.

```bash
python3 core/install/install.py --target /path/to/project --kit kit3_research
```

Core-Lite is installed automatically as a dependency.

## Official Anthropic skills

This kit does not repackage Anthropic's `deep-research` skill. `.claude/skills/deep_research/SKILL.md` is
our own procedure and works standalone; if you have the official skill installed it uses it for the
search fan-out. Install official skills from Anthropic's own distribution.

## Start here

`docs/research_kit/QUICKSTART.en.md` — three tasks, about fifteen minutes.
