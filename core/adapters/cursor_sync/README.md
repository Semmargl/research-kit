# Adapter — Cursor

Mirrors the installed `.claude/` tree into `.cursor/`.

```bash
python3 .claude/adapters/cursor_sync/cursor_sync.py --target . --dry-run
python3 .claude/adapters/cursor_sync/cursor_sync.py --target .
```

## Mapping

| Claude | Cursor | Note |
|---|---|---|
| `.claude/agents/*.md` | `.cursor/agents/*.md` | copied as-is |
| `.claude/rules/*.md` | `.cursor/rules/*.mdc` | frontmatter header added when missing |
| `.claude/skills/*/SKILL.md` | `.cursor/skills/*/SKILL.md` | copied as-is |

## One direction only

Claude is the source of truth. Edit under `.claude/`, then sync. Do not edit `.cursor/` directly:
the next sync silently overwrites it, and a two-way sync without a merge base loses whichever
side ran second.

## Automate it

Add to your `Makefile`:

```make
sync:
	@python3 .claude/adapters/cursor_sync/cursor_sync.py --target .
```

A pre-commit hook works too, but keep it advisory — a hook that rewrites files mid-commit
surprises people.
