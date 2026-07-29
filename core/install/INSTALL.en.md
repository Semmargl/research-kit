# Install — Claude OS Kits

Every kit sits on **Core-Lite**. Core-Lite installs once; installing a second kit adds a module,
it does not reinstall anything.

## Requirements

- Python 3.8 or newer (`python3 --version`). No third-party packages.
- A project folder to install into. It may be empty or an existing repo.
- Claude Code or Cowork for the primary platform. Cursor and generic `AGENTS.md` are supported via adapters.

## 0 · Unpack, then work from the kit folder

```bash
unzip claude-os-kits-all-1.3.0-source.zip
cd claude_os_kits
```

**Every command below is run from inside `claude_os_kits/`, not from where you unzipped.** The
installer resolves the kit root from its own location, so `python3 core/install/install.py` only
finds itself when that path exists relative to your shell. Skipping the `cd` gives you
`can't open file '.../core/install/install.py'` — the most common first-minute failure, and the
reason this step is now written down.

## 1 · Preflight

Run through `preflight_check.md` first. It takes two minutes and catches the three
failures that account for most broken installs.

## 2 · Dry run

Never install blind. Ask what would happen:

```bash
python3 core/install/install.py --target /path/to/your/project --kit all --dry-run
```

Read the list. Every line is a file that will appear in your project.

## 3 · Install

```bash
python3 core/install/install.py --target /path/to/your/project --kit all
```

You will be asked for placeholder values. Enter accepts the default.

| Placeholder | Meaning | Example |
|---|---|---|
| `PROJECT_NAME` | Name Claude uses for the project | `Acme Docs` |
| `VAULT_PATH` | Absolute path to the project root | `/Users/you/acme` |
| `LANG` | Language for chat replies | `en`, `ru`, `ua` |
| `DOMAIN_LIST` | Work areas in play | `research, support, engineering` |
| `OPUS_GATE_%` | Ceiling for top-tier model runs | `10%` |

Answers are stored in `claude_os.config.json` at the project root. Later runs read that file,
so re-running never asks twice and never renders different output.

Install one kit only:

```bash
python3 core/install/install.py --target /path/to/project --kit kit3_research
```

Core-Lite is added automatically — it is a hard dependency.

## 3.5 · Answer the questions — when should the system work?

The installer asks this once, interactively, and stores your answers in `claude_os.config.json`
under `review`. `.claude/rules/review_policy.md` reads them; nothing in the kit hard-codes a
policy, because the right depth of checking depends on what you actually do all day.

What it asks:

| Question | Why it matters |
|---|---|
| Which work gets the **isolated verifier** before delivery? | It is the expensive check. Run it on client deliverables, edits to always-load rules and agents, irreversible work, and conclusions that will be cited. Run it on everything and people learn to ignore it. |
| Which work gets **neither** check? | Quick facts, routine bookkeeping, throwaway drafts, plain chat. Proving nothing costs nothing. |
| Score finished work with the **judge**, on every run or a sample? | Cheap, runs after delivery. `all` while actively building, `sample` in quiet periods. |
| Weekly **retro**, and on which day and time? | Batches improvement proposals for you to accept or reject. |

Two things worth knowing:

- **The installer never creates a scheduled job.** If you ask for a weekly retro it prints the
  cron line and records `scheduled_task_created: false`. Setting it up is your call, not an
  installer's.
- **The questions only appear on a real terminal.** Piped, scripted or CI installs, and any run
  with `--yes`, silently take the defaults. If you install from a script, edit
  `claude_os.config.json` afterwards or re-run the installer interactively.

Your answers survive re-installs — a second run does not reset them.

## 4 · What lands where

Installing all three kits writes 83 files. The full top level:

```
your-project/
  CLAUDE.md                  # managed block merged in; your own text untouched
  claude_os.config.json      # your placeholder answers
  .claude/
    rules/                   # naming, writing_style, model_routing + every kit rule (12 total)
    agents/                  # install_verifier + kit agents (7 total)
    skills/                  # kit skills, one folder each (8 total)
    hooks/                   # Reliability Kit: hook scripts + the snippet you merge yourself
    adapters/                # claude_plugin, cursor_sync, agents_md_export
    install/                 # uninstall.py, so removal works after the kit folder is gone
  memory/                    # Reliability + Growth: decisions, learnings, buffers, change log
  scripts/                   # Growth Kit: judge, dashboard_lite, cost, security
                             # Research Kit: embeddings_search (optional)
  docs/
    reliability_kit/         # README, QUICKSTART ru+en, FAQ, demo_scenarios
    growth_kit/              # README, QUICKSTART ru+en, FAQ, safety_note
    research_kit/            # README, QUICKSTART ru+en, FAQ
  templates/                 # cost_card, report_exec_summary
  _moc.md                    # Research Kit only: vault-lite entry point
  00-capture/  10-reference/  30-reports/     # Research Kit only: vault-lite skeleton
  .claude_os/installed.json  # what the installer put there, with hashes
```

Install a single kit and you get Core-Lite plus that kit's rows only — nothing else appears.

## 5 · Register the hooks — Reliability Kit only, and only for Claude Code CLI

**Skip this and the next step reports FAIL.** The installer copies the hook scripts but never
edits your `.claude/settings.json`, because silently rewriting a settings file you own is not
something an installer should do. Registration is therefore one manual step:

1. Open `.claude/hooks/settings.snippet.json`.
2. Merge its `hooks` block into `.claude/settings.json`. If that file does not exist yet, create
   it with the snippet's contents — the installer deliberately does not create it for you.
3. Restart your Claude Code session and edit any file. A deliberately broken `.py` should produce
   a message. Until you have seen a hook fire, assume it is not running.

Full explanation, plus two copy-paste tests: `.claude/hooks/README.md`.

**Hooks only fire in Claude Code CLI.** Cowork and Cursor do not read `.claude/settings.json`, so
in those environments this step does nothing and the protocol rules carry the same guarantees —
see `.claude/hooks/cowork_protocol.md`. That is by design, not a broken install.

## 6 · Verify

Start a fresh Claude session in the project and paste:

```
Read .claude/agents/install_verifier.md and follow it.
```

It runs a smoke test against the manifest and reports PASS/FAIL per item. Do this before
you trust the install — a file that silently failed to copy looks exactly like a working setup
until the day you need it.

## 7 · Re-running is safe

```bash
python3 core/install/install.py --target /path/to/project --kit all
```

A second run prints `TOTAL: 0 written` and changes nothing. Files you edited after installing
are detected by hash and skipped, not overwritten. Use `--force` only when you want your edits gone.

## Updating

Pull a newer kit version and re-run the installer. Only genuinely changed files are rewritten,
and your local edits are still protected by the same hash check.

## Removing

See `uninstall.md`.

## Official Anthropic skills

The kits do not repackage Anthropic's own skills (`docx`, `pdf`, `pptx`, `xlsx`, `deep-research`).
Where a kit expects one, its README links to the official install. Install those separately.
