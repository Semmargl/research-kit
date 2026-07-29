<!-- BEGIN claude-os-core v1.0.0 -->
<!-- Managed block. The installer rewrites everything between these two markers.
     Keep your own instructions OUTSIDE the markers — they are never touched. -->

# Claude OS — Core

Project: `{{PROJECT_NAME}}` · Root: `{{VAULT_PATH}}` · Reply language: `{{LANG}}`
Domains in play: {{DOMAIN_LIST}}

## Response protocol

1. **TL;DR first** — 1–3 lines that answer the question. Bold the single key term.
2. Details only if needed: tight bullets, not prose. Tables for any comparison.
3. Stop when the question is answered. No preamble, no recap of what you just did.
4. Sentences ≤ ~15 words. One idea per line. Aim for half a screen.
5. Brevity means cutting filler, never facts. If detail is required, collapse it — do not delete it.
6. Never truncate code, commands, numbers, or exact names.

## Model routing

Default is **Sonnet**. Escalate only on a documented trigger and state the reason in one line.

| Tier | Use for |
|---|---|
| Haiku | Bulk or mechanical work: log sweeps, digests, simple lookups, routine bookkeeping. |
| Sonnet | Everything else. The default. |
| Top tier | Only on a trigger listed in `rules/model_routing.md`. Budget ceiling: {{OPUS_GATE_%}} of runs. |

Unguarded setups drift to the top tier by default — that is the single largest line on most API bills.

## Memory protocol

> The `memory/` files below ship with the **Reliability Kit**. Without that kit installed they
> do not exist and this section is inert — skip it, do not hand-create the files to satisfy it.

- **Session start:** read the memory store, then `memory/decisions.md`. Brief the user in one line only if something material was found.
- **Session end:** append what changed, what was decided, and the next step.
- **Store unavailable** (quota, outage, no network): do not retry and do not stop work.
  Writes go to `memory/pending_buffer.md` (append-only). Reads fall back to `memory/decisions.md`
  plus the completed-task list. Say so in one line. An empty memory response never means "task still open".
- Full rules: `rules/memory_protocol.md` (Reliability Kit) — pointer only, this block stays short.

## Verification gate

No completion claim — "done", "fixed", "passes" — without a fresh check run in the same message.
Run the command, read the full output (exit code, count, diff), then state the claim with that evidence.
A previous run, a subagent's self-report, or "should work" is not evidence.

## Rules index

| File | Governs |
|---|---|
| `rules/naming.md` | File, folder, and agent naming |
| `rules/writing_style.md` | Tone and structure of everything the agents produce |
| `rules/model_routing.md` | Tier escalation triggers and the cost gate |
| `rules/review_policy.md` | How much checking a task gets — reads `claude_os.config.json` |

This table lists the Core-Lite rules only. Kit rules are not added to it, and do not need to be:
Claude Code discovers `.md` files in `.claude/rules/` recursively, and loads every rule **without
a `paths:` frontmatter field** at session start, at the same priority as this block. A rule that
declares `paths:` loads only when Claude touches a matching file. Every rule this kit ships is
unscoped, so all of them load at launch; if you add path-scoped rules of your own, expect them
later and conditionally. To see what actually loaded in a session, run `/context`.

An earlier version of this line claimed kit rules "register themselves in this table when their
kit is installed". No code ever did that. The rules worked anyway — which is precisely why the
false sentence survived: nothing broke, so nothing pointed at it.

## How this block is maintained

This block is generated from `core/CLAUDE.core.md` by `core/install/install.py`.
Re-running the installer replaces the block in place — it never appends a second copy,
and it never touches text outside the markers. To customise, either edit outside the markers
or edit the source file and re-run the installer. To remove it, run `core/install/uninstall.py`
from the kit folder — or, if the kit folder is already gone, the copy the installer left behind:
`python3 .claude/install/uninstall.py --target .`

<!-- END claude-os-core -->
