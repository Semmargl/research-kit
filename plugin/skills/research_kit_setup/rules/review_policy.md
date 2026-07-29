# Review Policy — when this system checks its own work

The answers given at install live in `claude_os.config.json`, key `review`. **Read that file
before deciding how much checking a task gets.** Do not apply the defaults from memory: the
whole point of asking was that the right depth depends on what this person actually does.

## The triage step (start of any substantial task, ~0 tokens)

Rate the task on three axes — **stake** (cost if the result is wrong), **reversibility** (how
hard to undo), **audience** (stays here / goes out / changes the system itself). Then:

| Config field | Meaning |
|---|---|
| `verifier_tiers` | Task classes that get the isolated verifier BEFORE delivery |
| `judge_on_internal_deliverables` + `judge_mode` | Whether finished work is scored after delivery, and on every run or a sample |
| `skip_classes` | Task classes that get neither check |

Class names map to work like this:

- `client_facing` — deliverables, sellable output, anything leaving your hands.
- `rule_or_agent_edits` — edits to always-load rules or agents; they change every later session.
- `irreversible` — migrations, deploys, mass edits, anything hard to roll back.
- `cited_reports` — research or audit conclusions that will be referenced later.
- `quick_facts`, `routine_bookkeeping`, `throwaway_drafts`, `pure_chat` — skip candidates.

A class listed in `verifier_tiers` gets `.claude/agents/` verification in a **fresh session**
before you call it done. A class in `skip_classes` gets neither check — proving nothing costs
nothing, and a verifier fired at trivia teaches people to ignore it.

## Not in the config? Ask, once

If a task does not obviously fall into a listed class and the stake is real, say so in one
line and ask which way to treat it. Guessing silently is how a policy becomes decoration.

## Weekly retro

`weekly_retro`, `retro_day`, `retro_time` record what was asked for. `scheduled_task_created`
records whether it exists yet — the installer deliberately does **not** create a recurring job
on someone's machine. If `weekly_retro` is true and `scheduled_task_created` is false, mention
it once and offer the command; do not schedule it unprompted.

## Model tier

`placeholders.OPUS_GATE_%` is the ceiling for top-tier runs. It is a budget, not a target.
