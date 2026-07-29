# Claude Code plugin adapter

Packages the kits' **agents, skills and hooks** as a Claude Code plugin.

## What this adapter can and cannot carry

| Component | In the plugin? | Why |
|---|---|---|
| `agents/` | yes | Supported plugin component |
| `skills/` | yes | Supported plugin component |
| `hooks/` | yes | Supported plugin component |
| **`rules/`** | **no** | **Not a plugin component.** Claude Code loads `CLAUDE.md` and `.claude/rules/*.md` from the project, but a plugin has no way to deliver them. `install.py` writes them to `.claude/rules/`, where they work |
| `scripts/`, `templates/`, `memory/` | no | Not plugin components; delivered by `install.py` |

**Placeholders are not rendered in this channel.** `install.py` substitutes `{{VAULT_PATH}}`
and friends; the packager copies component files byte-for-byte, because a plugin has no target
project to resolve them against. Any component shipped through the plugin must therefore use
project-relative paths and no placeholders. `capture_url` shipped a raw `{{VAULT_PATH}}` this
way once — valid archive, unusable instruction.

**So the plugin is a convenience channel, not the whole kit.** The complete install is
`install.py`. Say this to a client rather than letting them assume the plugin is everything.

## Layout produced

```
claude-os-kits-all-<version>-plugin.zip
├── .claude-plugin/
│   └── plugin.json      <- manifest goes here and nowhere else
├── agents/
├── skills/
└── hooks/
```

## Two corrections made 2026-07-18

Both found by checking `code.claude.com/docs/en/plugins-reference` instead of assuming:

1. **The manifest was at the archive root.** Claude Code looks for `.claude-plugin/plugin.json`.
   At the root it is not seen at all — the plugin loads with no manifest and takes its name from
   the directory.
2. **The extension was `.plugin`.** No such format exists in the docs. Distribution is a
   directory, a `.zip`, or a URL to one. The old artefact could not be installed by anyone, and
   nothing in our build would ever have told us — we had no validation step.

Also removed: a `components` object (not a field in the schema — components are auto-discovered
by folder, or declared as separate `skills` / `agents` / `hooks` keys) and an invented `includes`
field, so that `claude plugin validate` returns clean rather than warning about unknown keys.

## Validate before shipping

Two steps, and the second is the one that matters. **Both need the Claude Code CLI**, so they run
on a real machine, not in a sandbox.

```bash
unzip -q dist/claude-os-kits-all-<version>-plugin.zip -d /tmp/plugin-check
claude plugin validate /tmp/plugin-check               # 1. schema
claude --plugin-dir /tmp/plugin-check                  # 2. live load
```

Step 1 checks the manifest against the schema. Step 2 loads the plugin for real and is the only
step that catches a component the runtime never picks up: a validator reports what is declared
wrongly, never what was forgotten entirely. This kit shipped hook scripts with no `hooks.json`
once, and step 1 was green for all of it — the hooks simply would never have fired.

Until step 2 reports the plugin loaded, the plugin channel is unverified and should not go to a
client. Valid is not the same as connected.
