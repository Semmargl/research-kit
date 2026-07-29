# Model Routing

Cost discipline. Default **Sonnet** everywhere; escalation is an exception that must be named out loud.

## Tiers

| Tier | Use for | Notes |
|---|---|---|
| Haiku | Bulk and mechanical steps: log sweeps, digest builds, simple lookups, routine bookkeeping. | Cheapest per token — worth routing to explicitly. |
| Sonnet | Everything else. | The default. No justification needed. |
| Top tier (Opus-class) | Only the triggers below. | State the trigger in one line before starting. |

## Escalation triggers

Escalate only when one of these is true. Customise the list per project — keep it short and testable.

- A refactor or migration crossing more than ~30 files, or a component tree over ~25 units.
- A system-design or architecture task where a wrong structural call is expensive to reverse.
- A deliverable with more than ~6 interdependent generated artifacts in one pass.
- An explicit user request for the top tier.

"This feels hard" is not a trigger. "This is long" is not a trigger — long and mechanical means Haiku.

## Cost gate

- Target ceiling: **{{OPUS_GATE_%}}** of billable tokens on the top tier. Above that, either the
  routing rules are being ignored or the ceiling describes a way of working nobody actually has.
- Measure before you tune. The Growth Kit's `cost_report` skill reads real usage; guessing at spend
  is how a bill quietly becomes top-tier-dominated.
- Reference data point: in one measured month, an unguarded setup put roughly 83% of spend on the
  top tier while the routing table on paper said "Sonnet by default".

### The ceiling encodes a decision, and there are two honest ones

The default assumes **automation-first**: agents and scheduled jobs do most of the work, a human
occasionally drives, and the top tier is reserved for the escalation triggers above. A ceiling
around 10% fits that shape.

A team whose work is **conversation-first** — a person reasoning with the top tier all day while
scheduled and mechanical jobs run on the cheaper tiers — will exceed 10% permanently and correctly.
For them the meaningful ceiling is much higher, and the number worth watching is not the top-tier
share at all but whether the *scheduled and mechanical* work has leaked upward.

Pick one deliberately and write down which. What must not happen is the third case: keeping a
ceiling you breach every week. A gate that fires constantly stops being read, and then the one week
it means something looks like all the others.

Raising the ceiling **because it was breached** is only legitimate if you can say what changed about
how the team works. "We keep going over" is not that reason.

## Downgrade triggers

Actively route *down*, not just avoid routing up:

- Repetitive edits across many files with one known pattern → Haiku.
- Reading logs, counting, reformatting, renaming → Haiku.
- Any step whose output is checked by a script rather than judged by a human → Haiku.
