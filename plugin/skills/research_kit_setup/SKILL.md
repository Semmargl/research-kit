---
name: research-kit-setup
description: Finish installing the Research Kit into this project. Writes the research rules that a
  Claude Code plugin cannot carry, and asks the four questions that decide when the kit does its
  checking. Use right after installing the research-kit plugin, or when the kit's rules are missing
  from a project. Also use when the user says the research kit "isn't working" or "isn't following
  its rules" — a plugin-only install is the usual cause.
---

# Finish the Research Kit install

The plugin brought the agents and the skills. It could not bring the rules: Claude Code plugins have
no rules component, and the rules are where source grading, report shape and the review policy live.
Without them the kit routes and searches but grades nothing.

This skill closes that gap. It takes about ninety seconds and it is a conversation, not a form.

## Before you start

Establish the project root — the directory the user wants this installed into. If the session is
already in a project, confirm it rather than assuming. Never install into a home directory.

Check what is already there:

- `.claude/rules/` — does the project already have rules with these names?
- `claude_os.config.json` — a previous install's answers.

If `claude_os.config.json` exists and has a `review` block, say so and offer to keep the existing
answers instead of asking again. Re-asking a returning user is the fastest way to look broken.

## Step 1 — Ask four questions

Ask them **conversationally, one at a time**, in the user's language. Do not paste all four at once
and do not present them as a form. Each has a default; a user who answers "just use the defaults" is
answered immediately, without being walked through the rest.

Explain *why* before asking, in one line. The point of these questions is that the defaults are a
guess about someone else's work.

1. **Which work gets the isolated verifier before it goes out?**
   Options: client-facing or sellable output · edits to rules and agents · hard-to-undo work
   (migrations, deploys, mass edits) · research or audit conclusions that will be cited later.
   Default: all four. This is the expensive check, so it belongs on work where being wrong costs
   something.

2. **Which work skips checking entirely?**
   Options: quick factual lookups · routine bookkeeping · one-off drafts · plain conversation.
   Default: all four. An expensive verifier on trivia trains people to ignore it.

3. **Should the cheap judge score finished internal work afterwards?**
   Default: yes, on a sample rather than every run.

4. **What share of runs may use the top model tier?**
   Default: 10%. This becomes the budget ceiling in `model_routing.md`. Unguarded setups drift to
   the top tier, and that is the largest line on most bills.

## Step 2 — Write the rules

Copy every file from this skill's `rules/` directory into `<project>/.claude/rules/`, preserving
filenames. Six files: `naming.md`, `writing_style.md`, `model_routing.md`, `review_policy.md`,
`source_grading.md`, `report_format.md`.

Copy them **verbatim**. Do not summarise, translate, reformat or improve them. They are the
specification, not a draft of one.

Two things to handle while copying:

- **`model_routing.md` contains `{{OPUS_GATE_%}}`.** Replace it with the answer to question 4,
  written as a percentage — `10%`. It is the only placeholder in the six files. If you find any
  other `{{TOKEN}}`, stop and report it rather than guessing a value.
- **A file that already exists and differs** is the user's, not yours. Show the difference and ask
  before overwriting. Never clobber silently.

## Step 3 — Write the answers where the rules can read them

Create or update `<project>/claude_os.config.json`. Merge into an existing file; never replace it.

```json
{
  "placeholders": { "OPUS_GATE_%": "10%" },
  "review": {
    "verifier_tiers": ["client_facing", "rule_or_agent_edits", "irreversible", "cited_reports"],
    "skip_classes": ["quick_facts", "routine_bookkeeping", "throwaway_drafts", "pure_chat"],
    "judge_on_internal_deliverables": true,
    "judge_mode": "sample",
    "weekly_retro": false,
    "scheduled_task_created": false
  }
}
```

Use the keys exactly as written — `review_policy.md` reads them by name, and a renamed key is a
policy that silently never applies.

**Create no scheduled task, cron entry or recurring job.** If the user asks for a weekly retro, set
`weekly_retro` to true, tell them the schedule, and leave the scheduling to them. Writing a recurring
job into someone's machine because they answered a question is not a decision this skill gets to
make. `scheduled_task_created` stays `false` until they do it themselves.

## Step 4 — Tell them what actually happened

Report, in plain language:

- which rules were written, and which were left alone because they already existed;
- the four answers, so they can see what the system will now do;
- that the agents and skills came from the plugin and are already active;
- that `.claude/rules/` loads at the start of a session, so **the rules take effect in the next
  session, not this one**. This is the single most common "it isn't working" report, and it is not
  a fault.

Then offer the verification step rather than performing it:

> To check the install, start a fresh session and run:
> `Read .claude/agents/install_verifier.md and verify this install.`

It must be a fresh session. A verifier that watched itself install inherits the assumptions it is
supposed to be testing.

## What this skill does not do

- It does not install the vault templates, the report templates or the optional semantic search.
  Those come with the full installer, `python3 core/install/install.py`, from the repository at
  https://github.com/Semmargl/research-kit.
- It does not touch `CLAUDE.md`. The plugin's agents and skills are discovered without it.
- It does not verify its own work. That is `install_verifier`, in a fresh context.

If the user needs the complete kit — templates, capture vault, adapters for Cursor or Codex — point
them at the installer. Say plainly that the plugin route is the fast one, not the complete one.
