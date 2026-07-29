# Cursor

Cursor reads `.cursor/`; Claude reads `.claude/`. Same content, two locations. Install first,
then mirror.

```bash
python3 core/install/install.py --target /path/to/project --kit kit3_research
cd /path/to/project
python3 .claude/adapters/cursor_sync/cursor_sync.py --target . --dry-run
python3 .claude/adapters/cursor_sync/cursor_sync.py --target .
```

## Mapping

| Claude | Cursor | Note |
|---|---|---|
| `.claude/agents/*.md` | `.cursor/agents/*.md` | copied as-is |
| `.claude/rules/*.md` | `.cursor/rules/*.mdc` | frontmatter header added when missing |
| `.claude/skills/*/SKILL.md` | `.cursor/skills/*/SKILL.md` | copied as-is |

Repeat runs report `Already in sync` and write nothing.

## One direction only

Claude is the source of truth. Edit under `.claude/`, then sync. Do not edit `.cursor/`
directly: the next sync overwrites it, and a two-way sync with no merge base loses whichever
side ran second.

## Automate

```make
sync:
	@python3 .claude/adapters/cursor_sync/cursor_sync.py --target .
```

A pre-commit hook works too, but keep it advisory — a hook that rewrites files mid-commit
surprises people.

## What this channel does not give you

The `.mdc` files carry the *instructions*. Isolated subagent runs — the mechanism behind
`citation_checker` — depend on your tool actually supporting subagents with separate context. If
it does not, run the citation check as a deliberate second pass in a new chat instead. The
isolation is the mechanism; the subagent is only one way to get it.

## Status of these instructions

Structure verified by `tools/platform_check.py`: rule count preserved through translation, every
`.mdc` carries frontmatter, second run idempotent. **Not verified:** that Cursor itself indexes
the mirrored files — no `cursor` binary was available in the build environment. Confirm it once
under Settings → Rules and you have your own proof.
