# Install by asking your IDE agent

An alternative to running `install.py` yourself. Copy the prompt below into Cursor, Claude Code,
Windsurf, Codex, Copilot Chat or any other agent that can read files and run commands, and it
will plan the install against your project, ask you the questions the installer would have asked,
apply it, and verify the result.

## Read this before you use it

The installer is a deterministic script: it hashes every file, writes only what changed, and
refuses to clobber your edits. An agent copying thirty-five files by hand is **less reliable than
that**, not more — it can drop a file, mangle a placeholder, or summarise a rule instead of
copying it, and be entirely confident while doing so.

So the prompt below tells the agent to **run `install.py` when it can**, and to fall back to
manual copying only when it genuinely cannot — no Python, no shell, or a sandbox that will not
clone the repo. The value the agent adds is at the edges: working out which platform you are on,
picking the right adapter, and answering "where does this go in *my* project".

The last step of the prompt is a verifier pass, and it is not decoration. It is how you find out
whether the agent actually did what it said.

## The prompt

Paste everything inside the block. Replace nothing except the last line if you want a different
kit selection.

```text
Install the Claude OS Research Kit into this project.

SOURCE
  https://github.com/Semmargl/research-kit  (CC BY-NC-SA 4.0)

Work in three phases. Stop after phase 1 and wait for my approval.

── PHASE 1 · PLAN ──────────────────────────────────────────────────────────
1. Get the kit: clone the repo to a scratch directory outside this project, or
   read it in place if it is already on disk. Do NOT clone it inside my project.
2. Read, in this order:
     README.md
     core/manifest.json
     kit3_research/manifest.json
     core/install/INSTALL.en.md
   The manifests are the source of truth for what gets installed. Every file has
   a `path` (in the kit), a `target` (in my project), an `install` mode, and a
   sha256. Nothing outside the manifests is part of an install.
3. Inspect my project: language, layout, whether .claude/ or CLAUDE.md or
   AGENTS.md already exist, and which agent tool I am using (you are it — say
   which).
4. Report back, and stop:
     - the exact file list you will write, kit-path -> my-project-path
     - any target that already exists and would be touched
     - which install route you will take (script or manual) and why
     - which adapter my platform needs, if any
     - anything you cannot determine — say so, do not guess
   Do not write anything during this phase.

── PHASE 2 · APPLY (only after I approve) ──────────────────────────────────
Preferred route — run the installer. It is stdlib-only Python 3.8+, no pip
install required:

    python3 <kit>/core/install/install.py --target <my project root> --kit kit3_research

Run it from the kit folder, not from my project: it resolves the kit root from
its own location. `core` installs automatically as a hard dependency of every
kit. Let it ask me its questions interactively — do not pass --yes unless I tell
you to, and do not answer them on my behalf.

Fallback route — only if you cannot run Python here. Then reproduce the
installer's contract exactly, and say clearly that you are doing this by hand:
  a. For each manifest entry, copy `path` to `target`. Copy the file verbatim.
     Never summarise, reformat, translate or "improve" a rule or skill.
  b. Substitute placeholders — {{PROJECT_NAME}}, {{VAULT_PATH}}, {{LANG}},
     {{DOMAIN_LIST}}, {{OPUS_GATE_%}} — EXCEPT in any entry marked
     "render": false. Two entries carry that flag and both break if rendered:
     the install verifier quotes the placeholder tokens as the very things it
     tells you to hunt for, and the HTML report template uses the same brace
     syntax for its own fields. Check the flag per entry; do not judge by eye.
  c. `"install": "merge_block"` means merge, not overwrite. CLAUDE.md is the
     one that matters: insert or replace only the block between the
     <!-- BEGIN claude-os-core --> and <!-- END claude-os-core --> markers and
     leave everything else in that file untouched.
  d. Write my answers and the resolved placeholders to claude_os.config.json in
     my project root, and the installed file list with sha256 per file to
     .claude_os/installed.json. Without those two files a second install cannot
     tell my edits from its own output, and will overwrite my work.
  e. If a target already exists and differs from what you are about to write,
     stop and ask. Do not overwrite.

Then, whichever route you took:
  - Ask me the review-policy questions from core/install/install.py if the
    script did not: which kinds of work get the isolated verifier before
    delivery, which get the cheap judge after, which get neither, and whether I
    want a weekly retro. Write the answers under "review" in
    claude_os.config.json. These decide when the system does its checking; the
    defaults are a guess about my work, not a recommendation.
  - Run the adapter my platform needs, if any:
      Cursor            .claude/adapters/cursor_sync/cursor_sync.py
      Codex / AGENTS.md .claude/adapters/agents_md_export/export_agents_md.py
      Claude Code       nothing — .claude/ is native
    Read that adapter's README before running it.
  - Do NOT create any scheduled job, cron entry or recurring task, even if I
    asked for a weekly retro. Print the schedule line and let me decide.

Dependencies, in full: Python 3.8+ and nothing else. The kit is stdlib-only and
there is no requirements.txt. The one optional extra is local semantic search
(scripts/embeddings_search/), which is off by default and needs Ollama plus a
pulled embedding model — do not set it up unless I ask.

── PHASE 3 · VERIFY ────────────────────────────────────────────────────────
Open a FRESH session or clear your context first — this is the point, a checker
that watched itself work will wave through its own mistakes. Then:

    Read .claude/agents/install_verifier.md and verify this install.

Report PASS / FAIL / BLOCKED per item, verbatim. BLOCKED means it could not be
proved in this environment; never upgrade it to PASS because it looks fine.

Finally, tell me plainly: what you installed, what you skipped, and anything you
are unsure actually works.
```

## If you want a different kit selection

The last argument controls it. `--kit kit3_research` installs Research plus Core-Lite.
`--kit core` installs Core-Lite alone. `--kit all` installs everything present in the repo you
cloned. Change the line in phase 2 and the manifest list in phase 1 to match.

## When this route is the wrong one

- **You are installing this for other people, or more than once.** Use the script. Determinism is
  the entire point of it, and you get an audit trail in `.claude_os/installed.json`.
- **You are upgrading an existing install.** The script's delta-merge and edited-file detection
  are load-bearing; an agent redoing it by hand will either clobber your changes or skip files it
  should have updated.
- **Your agent cannot run shell commands.** Then it also cannot run the verifier meaningfully, and
  you are trusting a file copy you have no way to check. Clone the repo and run the script.
