# FAQ — Research Kit

**It answered from memory instead of searching. Why?**
Ask again with "search for this". Then check `.claude/rules/` is being loaded — the router only
fires if the core block is in your `CLAUDE.md`. Facts about the present world (prices, versions,
who holds a role) should always be searched; if that is not happening, the rules are not loading.

**The citation checker marks things PARTIAL that look fine to me.**
Read its "Source says" column. PARTIAL usually means a hedge got dropped ("may reduce" → "reduces")
or a number lost its scope. Those are real defects, and they are the ones that get noticed by the
person you send the report to.

**Can I run the checker in the same session?**
You can, and it will be worth much less. It has already read the reasoning that produced the claims
and will accept them. Use a fresh session.

**It says confidence Low. Is that a failure?**
No. Low confidence honestly reported is a working result — it tells you the question needs better
sources, not that the tool broke. Confident phrasing over thin evidence is the failure mode.

**Do I need the official Anthropic deep-research skill?**
No. `.claude/skills/deep_research/SKILL.md` works standalone. If the official skill is installed, the fan-out
step uses it. This kit deliberately does not repackage Anthropic's skills.

**Why is semantic search off by default?**
It needs a local model server and a rebuild step. Most projects do not need it until they pass a few
hundred notes. See `scripts/embeddings_search/README.md`.

**Where do reports go?**
`30-reports/`, named `report_<topic>_<date>.md`. Reports are records: do not silently rewrite an old
one when facts change — write a new one and link back.

**Can I change the source tiers?**
Yes, edit `.claude/rules/source_grading.md`. Add the tier-A domains for your field; keep the list
under about twenty entries or nobody will read it.

**It refuses to fill a cell in a comparison table.**
By design. An empty cell reading "not covered" is correct output; a plausible guess in that cell is
the exact failure the kit exists to prevent.

**Does anything leave my machine?**
Web searches and page fetches do, like any research. The optional embeddings module talks only to
localhost — notes are not uploaded.
