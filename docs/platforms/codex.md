# Codex

Codex reads `AGENTS.md` at the repository root. Install, then export.

```bash
python3 core/install/install.py --target /path/to/project --kit kit3_research
cd /path/to/project
python3 .claude/adapters/agents_md_export/export_agents_md.py --target . --dry-run
python3 .claude/adapters/agents_md_export/export_agents_md.py --target .
```

The export assembles one root `AGENTS.md`: the Core instruction block, every rule inlined in a
collapsible `<details>` section, and a table of the installed agents and skills. Roughly 330
lines for this kit.

## Regenerate, never hand-edit

`AGENTS.md` is generated. Edits are lost on the next export — change the source under `.claude/`
and re-run.

## The guard worth knowing about

Point the exporter at the wrong directory, or run it after uninstalling, and the export finds
nothing. It **refuses to write** rather than replacing a real `AGENTS.md` with a four-line stub,
and exits 2 with the likely cause. An empty result must never be more destructive than a full
one. Override with `--force` only if a blank file is genuinely what you want.

## What this channel does not give you

Instructions, not execution. A tool reading `AGENTS.md` learns the conventions; it does not gain
subagent isolation, hooks, or skill dispatch. For this kit that means:

- `source_grading`, `report_format`, `review_policy` — carry over fully, they are rules.
- `deep_research`, `report_builder`, `capture_url` — carry over as procedures Codex can follow.
- `citation_checker` — carries over as a procedure, but its value comes from **fresh context**.
  Run it in a separate session against the finished report, or you get an author grading itself.

## Size

Every rule is inlined, so the file is large. If your tool truncates context, delete the rules you
do not need from `.claude/rules/` before exporting rather than shipping a file that gets silently
clipped.

## Status of these instructions

Structure verified by `tools/platform_check.py`: `AGENTS.md` written at the root, all four
sections present, all 6 rule bodies inlined, second run idempotent, and the empty-export guard
confirmed to refuse (exit 2, file intact). **Not verified:** that Codex itself picks the file up —
no `codex` binary was available in the build environment.
