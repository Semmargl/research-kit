# Claude Code / Cowork

The primary target. Two channels, and they carry different things.

## Channel 1 — `install.py` (complete)

```bash
python3 core/install/install.py --target /path/to/project --kit kit3_research
```

Writes:

| Goes to | What |
|---|---|
| `CLAUDE.md` | the Core block, merged between markers — your own text outside them is never touched |
| `.claude/rules/` | 6 rules, all unscoped, so all load at session start |
| `.claude/agents/` | `research_router`, `citation_checker`, `install_verifier` |
| `.claude/skills/*/SKILL.md` | `deep_research`, `capture_url`, `report_builder` |
| `.claude/adapters/`, `.claude/install/` | platform adapters and the uninstaller |
| project root | `templates/`, `00-capture/`, `10-reference/`, `30-reports/`, `scripts/`, `docs/research_kit/` |

Re-running is a no-op: files you edited are detected by hash and skipped, not clobbered.

## Channel 2 — the plugin archive (partial, by design)

```bash
unzip research-kit-<version>-plugin.zip -d /tmp/research-kit-plugin
claude plugin validate /tmp/research-kit-plugin --strict   # 1. schema
claude --plugin-dir /tmp/research-kit-plugin               # 2. live load
```

**Step 2 is the one that matters.** A validator reports what is declared wrongly; it never
reports what was forgotten entirely. This product once shipped hook scripts with no `hooks.json`
and step 1 was green for all of it — the hooks would simply never have fired.

### What the plugin cannot carry

| Component | In the plugin? | Why |
|---|---|---|
| `agents/`, `skills/` | yes | supported plugin components |
| **`rules/`** | **no** | not a plugin component. Claude Code loads `.claude/rules/*.md` from the project, but a plugin has no way to deliver them |
| `templates/`, `scripts/`, docs | no | not plugin components |

So the plugin is a convenience channel, not the whole kit. If you install only the plugin and
expect `source_grading` or `report_format` to apply, they will not — run `install.py`.

## Verify

```
Read .claude/agents/install_verifier.md and verify this install.
```

Fresh session. A verifier that watched the install inherits its blind spots.

## Status of these instructions

Structure verified by `tools/platform_check.py` (build side). The **live load** — steps 1 and 2
above — was last run on 2026-07-19 against v1.3.0 and has **not** been re-run against v1.4.0: no
Claude Code CLI was available in the build environment. Treat step 2 as your own acceptance test.
