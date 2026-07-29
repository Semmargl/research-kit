# Any other agent tool

If your tool reads agent instructions from a single file at the repository root, use the same
`AGENTS.md` export as Codex:

```bash
python3 core/install/install.py --target /path/to/project --kit kit3_research
cd /path/to/project
python3 .claude/adapters/agents_md_export/export_agents_md.py --target .
```

Full detail, including the anti-clobber guard: [codex.md](codex.md).

## What survives the lowest common denominator

| Mechanism | Survives? | Why |
|---|---|---|
| Source tiers (A/B/C/D) | yes | a rule, read as text |
| Report format, TL;DR-first, confidence | yes | a rule |
| Review policy (when to check) | yes | a rule; it reads `claude_os.config.json` |
| Research procedures | yes | steps the model can follow |
| **Isolated citation checking** | **partly** | needs a genuinely fresh context; see below |
| Subagents, hooks, skill dispatch | no | need a platform that implements them |

## Getting the isolation without subagents

The one mechanism worth protecting is isolation. A checker that watched the report being written
inherits its assumptions and waves through the same mistakes.

Without subagent support, do it by hand:

1. Finish the report. Close the session.
2. Open a **new** session with no history.
3. Paste only the report and the sources — not the reasoning that produced them.
4. Ask it to mark each claim SUPPORTED / PARTIAL / UNSUPPORTED / MISSING against the sources.

That is the whole mechanism. The subagent is convenience; the fresh context is the point.

## If your tool has no root-instruction file

There is no adapter for that, and pretending otherwise would be the failure this kit exists to
prevent. Paste the rules you need from `.claude/rules/` into whatever system prompt or project
instruction field the tool offers, and accept that nothing enforces them.
