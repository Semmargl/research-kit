# Adapter — generic AGENTS.md

For any tool that reads agent instructions from a single root file and has no plugin format.

```bash
python3 .claude/adapters/agents_md_export/export_agents_md.py --target . --dry-run
python3 .claude/adapters/agents_md_export/export_agents_md.py --target .
```

## What it produces

One `AGENTS.md` at the project root containing the core instruction block, every rule inside a
collapsible `<details>` section, and a table of installed agents and skills.

## Limits worth knowing

- **Generated file.** Hand edits are lost on the next export. Change the source under `.claude/`.
- **Instructions, not execution.** A tool reading `AGENTS.md` learns the conventions; it does not
  gain the agents themselves. Subagent isolation, hooks and skills need a platform that supports them.
- **Size.** Every rule inlined means a large file. If your tool truncates context, cut the rules
  you do not need before exporting rather than shipping a file that gets silently clipped.
