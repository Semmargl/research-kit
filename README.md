# Claude OS — Research Kit

**Analyst-grade research: multi-angle search, verified sources, ready reports.**

An ordinary AI answer carries no sources, so you cannot put it in front of a client or a
manager. You end up re-checking it yourself, which costs more than doing the research by hand
would have. This kit fixes that with two mechanisms, not with better prompts:

1. **Adversarial verification** — before writing, every finding is attacked: is the source
   primary, are my "multiple sources" actually independent, is this still current, did I only
   search for confirmation?
2. **Isolated citation checking** — a separate pass, with fresh context, reads the sources and
   marks each claim SUPPORTED / PARTIAL / UNSUPPORTED / MISSING. The author never grades their
   own work.

Most AI research failures are not invented facts. They are hedges quietly dropped, numbers
arriving without their scope, and three citations stacked after four claims.

## Install

Three steps. The third is the one people skip, and it is the one that makes the kit yours.

```bash
git clone <this repo> research-kit
cd research-kit
python3 core/install/install.py --target /path/to/your/project --kit kit3_research
```

Core-Lite installs automatically as a dependency. **Run the installer from this folder**, not
from your project — it resolves the kit root from its own location.

### Step 3 — answer the questions

The installer asks *when this system should work*: which kinds of task get an isolated verifier
before delivery, which get the cheap judge afterwards, which get neither, and whether you want a
weekly retro. Answers are written to `claude_os.config.json` in your project and read by
`.claude/rules/review_policy.md`.

Defaults exist, but the defaults are a guess about your work. Ninety seconds here is the
difference between a system that checks the right things and one that checks everything or
nothing. To accept the defaults anyway: add `--yes`.

The installer **never creates a scheduled job**. If you ask for a weekly retro it prints the
cron line and leaves it to you.

### Or have your IDE agent do it

If you would rather not run anything by hand, paste one prompt into Cursor, Claude Code, Windsurf,
Codex or Copilot Chat and let the agent plan the install against your project, apply it, and
verify it: [docs/install-via-agent.md](docs/install-via-agent.md).

That prompt still tells the agent to run `install.py` whenever it can. An agent copying
thirty-five files by hand is less reliable than a script that hashes each one — it can drop a
file or paraphrase a rule and be confident while doing so. What the agent adds is the part a
script cannot do: reading your project, working out which platform adapter you need, and
answering "where does this go in *my* layout".

### Verify the install

In a **fresh session** — this matters:

```
Read .claude/agents/install_verifier.md and verify this install.
```

It reports PASS / FAIL / BLOCKED per item. `BLOCKED` means something could not be proved in
that environment; it is never silently upgraded to PASS.

## Your platform

| Platform | Guide |
|---|---|
| Claude Code / Cowork | [docs/platforms/claude.md](docs/platforms/claude.md) |
| Cursor | [docs/platforms/cursor.md](docs/platforms/cursor.md) |
| Codex | [docs/platforms/codex.md](docs/platforms/codex.md) |
| Any other agent tool | [docs/platforms/generic.md](docs/platforms/generic.md) |

## Start here

- `kit3_research/docs/QUICKSTART.en.md` — three tasks, about fifteen minutes. Russian:
  `QUICKSTART.ru.md`.
- `kit3_research/docs/FAQ.md` (Russian: `FAQ.ru.md`).
- `kit3_research/demo/` — two example reports, including one with deliberately fictional sources
  that is never installed into a project, so it can never be mistaken for a real report.

## What is in it

| Piece | Does |
|---|---|
| `research_router` agent | Recognises the request type and picks one lane. Quick facts stay quick. |
| `citation_checker` agent | Isolated pass: does each source actually say what the draft claims? |
| `deep_research` skill | Fan out into sub-questions, search each, then attack your own findings. |
| `capture_url` skill | A URL becomes a structured note, deduplicated, with a source tier. |
| `report_builder` skill | Comparisons, gap maps and synthesis notes, plus a self-contained HTML view. |
| `source_grading` rule | A/B/C/D tiers, chain-following, the rule for surprising claims. |
| `report_format` rule | TL;DR first, claims carry their sources, confidence stated. |
| `review_policy` rule | How much checking a task gets — reads your install answers. |
| `vault_lite` templates | Three-tier note skeleton: capture, reference, reports. |
| `embeddings_search` | Optional local semantic search. Off by default, talks only to localhost. |

## Official Anthropic skills

This kit does not repackage Anthropic's `deep-research` skill.
`.claude/skills/deep_research/SKILL.md` is an independent procedure and works standalone; if you
have the official skill installed, the search fan-out delegates to it. Install official skills
from Anthropic's own distribution.

## Honest limits

- **It does not make research cheaper.** Verification costs tokens rather than saving them. What
  it changes is whether the output is checkable.
- **Low confidence is a result, not a failure.** Honestly reported thin evidence tells you the
  question needs better sources.
- **The plugin archive cannot carry rules.** Claude Code plugins have no rules component;
  `install.py` writes them to `.claude/rules/`, where they load. Installing only the plugin gives
  you agents and skills without the rules.
- Web searches and page fetches leave your machine, as in any research. The optional embeddings
  module does not.

## Licence

**CC BY-NC-SA 4.0.** Free for personal, research, educational and any other noncommercial use —
copy it, adapt it, share your version. Three conditions: credit the author, do not use it
commercially, and license any modified version under the same terms. Commercial use, including
reselling it or delivering paid client work with it, needs a separate licence — write to
decebel1995@gmail.com. Full terms in `LICENSE`, attribution wording in `NOTICE`.
