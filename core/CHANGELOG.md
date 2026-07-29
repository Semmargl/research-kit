# Changelog — Core-Lite

Versions follow semver. A change to the managed block or to the installer contract is a minor bump;
a change that requires the user to re-answer placeholders is a major bump.

## 1.0.0 — 2026-07-18

First release.

- Managed `CLAUDE.md` block with response protocol, model routing, memory pointers and verification gate.
- Rules: `naming`, `writing_style`, `model_routing`.
- Manifest-driven installer: placeholder resolution stored once, write-on-difference,
  hash-protected local edits, `--dry-run`, `--force`.
- Uninstaller that strips the managed block and removes only unmodified files.
- Adapters: Claude plugin, Cursor sync, generic `AGENTS.md` export.
- `install_verifier` agent for an isolated post-install smoke test.

## 1.1.0 — 2026-07-18

Reconciliation pass after the P0 and P1 execution reports closed. Every change below fixes a
failure that actually happened in the reference system, not a hypothetical one.

**Hooks (Reliability Kit)**

- Both hooks now emit `{"systemMessage": ...}` on stdout. Plain printed text at exit 0 is
  transcript-only, so the previous version was invisible to the user — the same defect that left a
  reminder hook unread for eight days.
- `stop.py` reads stdin with a timeout. Running it by hand, exactly as its own docs showed, hung
  forever on an idle pipe.
- Added `hooks/settings.snippet.json` and `hooks/README.md`. The scripts were shipped but never
  registered, so a client would have had files on disk and no gate — indistinguishable from working.
- `cowork_protocol.md` corrected: Cowork is a full host that does not read `.claude/settings.json`,
  not "a chat environment without events". The old wording sent people hunting for a
  misconfiguration that does not exist.

**Secret scanner (Growth Kit)**

- `.env.example` and friends are no longer excluded from scanning. A live API key sat in one for
  weeks precisely because the file was skipped by name.
- New `test_secret_scanner.py`: 11 positive and 12 negative cases, plus a `--noise` false-positive
  counter. A placeholder filter once silently disabled every rule below it, and nobody could see it.
- New `--history` mode. A secret deleted from the working tree is still in the git history, and a
  gate that only reads the tree reports clean while the credential is one `git show` away.

**Verifier**

- `verifier_agent` reconciled with the finished design: three-state verdict, evidence ladder
  (VERIFIED / HOLLOW / ORPHANED / STUB / MISSING), overrides block, correctness-only scope with a
  stated <5% false-positive bar.
- Explicit verifier-vs-judge table in both `verifier_agent` and `install_verifier`, so nobody pays
  for two tools answering the same question.
- `install_verifier` now treats a copied-but-unregistered hook as a FAIL.

**Documentation**

- `session_digest` no longer implies an automatic session-end trigger. `SessionEnd` has no decision
  control and a shell script cannot summarise a session; promising it would promise the impossible.
- `citation_checker` requires verbatim quotes. A previous unquoted fact-check pass replaced three
  correct figures with three wrong ones, and all three were believed.
- All `DEPENDS: P1` markers removed — that work is finished.

## 1.2.0 — 2026-07-18

Reconciliation against the reference implementation after the growth loop ran a full production
cycle. Every change below replaces a design decision with a measured one.

**Growth Kit — the five `DEPENDS: P2` drafts are now production files**

- `prune_rules` **merged into `improve_retro`**. Measured reason: a prune step that lives in its
  own file never runs. The kit ships one skill instead of two; removals happen inside the weekly
  pass, with the same classification table.
- `improve_retro` now names the **three targets that need their own approval per diff** — itself,
  the verification rules, and the always-loaded router — and states that a blanket "apply all"
  does not extend to them, even when the human clicks apply-all.
- `templates/learnings.md` changed from a flat list of lines to **typed deltas with an id, a
  status, a cost and a mandatory source**. Without an id you cannot replace one entry without
  rewriting the file, and rewriting is what the delta rule forbids.
- Thresholds are now split into measured and unmeasured **everywhere they appear**. "Two
  instances make a pattern" is measured; "~40 lines", "~20 runs" are starting values and say so.
- Proposals must carry a **token cost, estimated then re-measured after applying**. Measured
  example now in the docs: an estimate of "+14 tokens" came out at +94.
- `templates/retro_rejected.md` added — rejected proposals are logged so the next pass cannot
  re-raise them, which is how batch approval degrades into rubber-stamping.

**Cost report**

- An empty window writes a `skipped` card with `_raw.no_data` instead of exiting 1 in silence. A
  producer that stops running must not be indistinguishable from a week with no spend.
- The card gained **top-3 most expensive work**, a **week-over-week delta**, and a line reporting
  the **cost of the improvement loop itself**, fed by `growth_loop_ledger.jsonl`. An empty ledger
  reports "not measured", never zero.
- The `--gate` default is now tied in the help text to `rules/model_routing.md`, so the report and
  the rule cannot drift apart unnoticed.
- `test_known_sum.py` added: a hand-computed total, plus a mutation test proving the double-count
  regression is actually detected (the broken version returns exactly 2.00x).

**Security**

- `secret_scanner` honours a self-declaring `secret-scanner: test-fixtures` marker in a file's
  first five lines, so a test file full of deliberate fixtures no longer turns the release gate
  red. Narrow on purpose: the marker must be near the top, so documentation that merely mentions
  it is still scanned.

**Versions**

- All four manifests, `VERSION` and `core/VERSION` are on 1.2.0. Previously the top-level
  `VERSION` said 1.0.0 while the manifests said 1.1.0, and `kit3_research` said 1.0.0 despite
  having changed — the installer decides by content hash so nothing was lost, but the version a
  client saw in `.claude_os/installed.json` was wrong.

## 1.3.0 — 2026-07-19 · systematic parity sweep (run, not read)

First systematic functional parity pass of every kit component against its living prototype,
after the 2026-07-19 discovery that the cost wrapper had silently fallen four fixes behind.
Method: run every script, run every test, mutation-check every gate. Verdict: two more lagging
components found and fixed; installers and judge were already at parity.

**Fixed (lagged behind the system)**

- `secret_scanner`: `SKIP_MARKER` the tests referenced but the scanner did not know; connection-string
  placeholder rule; `PLACEHOLDER_RE` now applies to all rules (was: only 3, so `your_api_key="..."`
  still flagged); K10 warning not to quote detectable literals outside the definitions block.
- `ccusage_wrapper` docs told the pre-Cowork story: coverage tables in README/FAQ/docstring/card text
  now state both sources (CLI + Cowork sandboxes, ~90-95%), that claude.ai web chats are never
  visible, and that billing is the only complete source. Two implemented behaviours (real-shape
  inheritance, >20%-unparsed gate) gained the tests they were missing; brittle cross-check with
  `install.py` no longer crashes when the folder is copied out.
- `dashboard_lite/build_digest.py`: `tz` from `registry.json` was documented but silently ignored —
  cron lateness was judged by system clock. `local_now()` added; a producer past its cron time in
  its declared timezone now reads `missed`, not `pending`.

**Ported from the system's verification layer (md)**

- `kit1/rules/verification_runner.md` + `verify_deliverable`: the two checklist items proven three
  times each this week — "re-run the exact case that produced the bug, on the file you changed" and
  "filter tests need a positive control" — plus the verifier-vs-judge table, "do not coach the
  verifier", and two explicit mandatory-verify categories.
- `kit3/agents/citation_checker.md`: source-authority rule (structured API > HTML page > tool index;
  declaring a source stale requires proof).
- `kit1` session digest: headers aligned across the skill and
  `memory_protocol.md` (Asked/Did/Decided/Learned/Open/Next); the protocol had drifted to a 3-field variant.

**Acceptance gate, same day — 13-point checklist over every manifest component**

The parity sweep asked "has the kit fallen behind the system?". This pass asked the different
question "does each component actually work?", and found four defects that parity could not see,
because the system's own copies have them too. Three were found by running things nobody had run.

- `kit1/hooks/post_tool_use.py`: **hung forever on an idle stdin.** Its sibling `stop.py` was fixed
  for exactly this on 2026-07-18 and carries a docstring explaining it; the fix was never swept
  across the class, and both hooks exit 0, so nothing pointed at it. Same guard now applied.
  Separately, `check_python` shelled out to `py_compile`, which writes a `.pyc` beside the source:
  in any directory the process cannot write to it reported `syntax error:` on a syntactically
  perfect file. Now compiled in memory — no writes, no false alarm, one less subprocess per edit.
- `kit2/python/judge/judge.py`: **silent card loss.** The `-HHMMSS` suffix that exists to stop a
  second judgement overwriting the first collided with itself when two ran inside one second, which
  is ordinary in a scripted run. Its own docstring claimed "ON DISK every judgement is kept"; that
  was false precisely in the case the suffix was written for, and the destroyed card was the
  failing one. Now probes for a free name, bounded.
- `core/adapters/agents_md_export/export_agents_md.py`: **blanked a real `AGENTS.md` to a four-line
  stub** when pointed at a project with no kit installed, reporting success. Empty result, more
  destructive than a full one — the same class as the judge card and the cost card before it. Now
  refuses with exit 2 and an explanatory message unless `--force` is passed.
- `kit3/python/embeddings_search`: `--endpoint` was accepted at build time but never recorded, while
  the query side read a `meta.json` key nothing wrote and fell through to `localhost:11434`. A
  supported flag on one side and a dead read on the other. Endpoint is now persisted, and
  `semantic_search.py` gained a matching `--endpoint` override.

**Corrected claims (each was a statement no code implemented)**

- `core/CLAUDE.core.md` told every customer that "kit-specific rules register themselves in this
  table when their kit is installed". No code ever did that, and nothing broke, because Claude Code
  loads every `.md` in `.claude/rules/` at session start regardless. The rules were fine; the
  sentence was not. Replaced with how loading actually works, plus a pointer to `/context`.
- `kit1` manifest described `hooks/hooks.json` as the file that registers the hooks, without saying
  that this is true of the plugin channel only — under the installer it lands in `.claude/hooks/`
  inert, with `${CLAUDE_PLUGIN_ROOT}` unresolved, and registration is the manual settings merge.
- `kit2` manifest's `depends_summary` still listed `prune_rules`, removed in 1.2.0, and still called
  the growth-loop files unmeasured drafts while every per-file note beneath it said the opposite.
- `tools/package.py` named archives from `core/VERSION`. With core legitimately parked at 1.2.0
  while the kits moved to 1.3.0, a 1.3.0 build would have been written as
  `claude-os-kits-all-1.2.0-*.zip`, overwriting the genuine 1.2.0 archive with different bytes and
  shipping a plugin manifest declaring a version the customer was not getting. Now takes the
  product version from the root `VERSION`. Build scratch is also cleaned in a `finally`, after a
  stale `.plugin.json.tmp` from an interrupted build was found sitting in `dist/`.

**Structural decision — retro (was deferred to this pass)**

`kit2/agents/retro_agent.md` restated ~70% of `improve_retro/SKILL.md`. Resolved by making the
skill the single owner of the procedure and reducing the agent to a delegating shell. The agent is
kept rather than deleted for one reason: its `tools: Read, Grep, Glob` frontmatter makes
"proposes, never writes" a capability the agent lacks rather than an instruction it is asked to
follow — and a kit built on the difference between those two should apply it to itself. The
measured/unmeasured threshold note moved into the skill with the rest of the substance. No
"keep in sync" comment was added: the absence of a second copy is a property of the tree, whereas
a sync note is a promise someone has to remember.

**Found by the isolated verifier, after the author had called the pass done**

Three for three: every phase this week, the verifier found something the author did not see.

- **22 of the day's components had changed content; only 8 had a version bump.** The eight were
  this session's own edits — the other fourteen came from the parity sweep earlier the same day
  and were never renumbered. `hash_manifests --check` passed throughout, because it compares a
  hash to a file and never asks whether a version matches a change; a green gate was therefore
  evidence of nothing here. This is the antipattern the kit's own lessons file already lists
  ("a version that does not reflect its contents"), recurring after being written down. All
  fourteen bumped, and the audit that found it is recorded in the acceptance report so it can be
  re-run rather than re-derived.
- **The retro split quietly narrowed an anti-drift guarantee.** The old agent named "this agent
  and the retro skill" as a single protected target; after the merge, the skill's list protected
  only itself. The agent's entire remaining purpose is its `tools: Read, Grep, Glob` line, so a
  batch approval could have added `Write` to the file whose lack of `Write` was the guarantee —
  a refactor removing a safety property while every visible check stayed green. Both files now
  name the pair, and the agent states it in its own text.
- `CLAUDE.core.md` replaced a false claim about rule loading with one that was itself slightly
  too broad ("every `.md` in `.claude/rules/`"): rules carrying a `paths:` field load on match,
  not at launch. Corrected against the vendor documentation. Fixing an overclaim with a smaller
  overclaim is its own small lesson.
- Two pointers dropped in the retro merge — `docs/safety_note.md`, and the step "read the current
  rule files" — restored to the skill.
- `package.py` staged its plugin scratch under `root/dist` while cleaning up in the `--out`
  directory, so every non-default build left a temp file behind and any cleanup test run with
  `--out` proved nothing. Both now use the output directory.

**Versions**

- `core` → 1.3.0 (the managed block changed, which its own rule makes a minor bump). All four
  manifests and the top-level `VERSION` now read 1.3.0. Per-file: 22 components carrying a
  content change this day all bumped, verified by re-running the audit to zero.

## 1.4.0 — 2026-07-29

Research Kit publication pass. Everything below was found by running the thing, not reading it.

### Fixed

- **Core block ordered a read of files it does not ship.** `CLAUDE.core.md` told every session to
  read `memory/decisions.md` and `memory/pending_buffer.md`. Those ship with the Reliability Kit,
  so a Research-Kit-only install pointed at two files that would never exist. The section now
  states the precondition instead of assuming it.
- **A rule pointed at a file that never exists in a project.** `rules/writing_style.md` sent the
  reader to `CLAUDE.core.md` for the response protocol; in an installed project that content
  lives in `CLAUDE.md`. Same class as the doc-link sweep in 1.3.0: the manifest renames the
  target, the prose does not follow.
- **`install.py` was outside the integrity gate.** `hash_manifests.py` walked `files` only, so the
  single file that writes to a customer's disk carried no hash — and the gate still printed
  "0 mismatches". It now covers `not_installed` too, excluding the manifest's self-reference.
- **Single-kit archives were named after build order.** `--kit kit3_research` produced
  `claude-os-kits-3-1.3.0-source.zip`. "3" tells a buyer nothing. Single-kit builds are now
  `research-kit-<version>-*.zip`, and the plugin manifest describes the packaged payload rather
  than the whole family.
- **`LICENSE` did not exist** while `plugin.json` declared `"license": "see LICENSE"`. Both
  archives now carry `LICENSE` and `NOTICE`; the manifest declares an SPDX identifier.

### Added

- `rules/review_policy.md` — the consumer for the install questionnaire. Without it the answers
  were written and never read.
- **Install questionnaire.** The installer now asks when the system should work: which task
  classes get the isolated verifier, which get the judge and at what sampling, which are skipped,
  and whether a weekly retro is wanted and when. Answers land in `claude_os.config.json` under
  `review` and survive re-installs. The installer prints the cron line for the retro and
  deliberately does not create it — an installer does not get to put a recurring job on someone's
  machine because they answered a question.
- `tools/platform_check.py` — build-side per-platform gate (Claude / Cursor / Codex / generic).
  Separates STRUCTURAL (provable) from RUNTIME (needs the vendor binary) and reports the latter
  as BLOCKED. It will not print PASS for something it did not prove.
- `install_verifier.md` checks 9–12: the review policy must have a consumer, the platform channel
  must be named, a plugin-only install that expects rules is a FAIL with a remedy, and a BLOCKED
  row can never be reported as PASS.

### Known limits

- The plugin archive has **not** been loaded by a real Claude Code CLI in this pass
  (`claude plugin validate --strict`, `claude --plugin-dir`). Neither has Cursor indexed the
  `.mdc` mirror, nor Codex read the generated `AGENTS.md`. No vendor binary was available.
  Structure is proven; runtime is not. Review-queue item R-004 stays open.

### Fixed in the content audit (same 1.4.0 release)

An audit of the substantive kit files — the ones no earlier pass had read — found ten defects.
None was a false marketing claim or a leak; all were instructions that could not be followed or
files disagreeing with each other.

- **The embeddings build command in the README could not be run as written.** Relative note paths
  with the script invoked from its own folder resolved under `scripts/embeddings_search/`. The
  command now names the script path and states that it runs from the project root — and the
  script's own error text no longer reprints the broken form.
- **That script's empty-result error blamed the wrong thing.** On a fresh install the vault
  skeleton holds only `_index.md` files, skipped by design, so "check the --notes paths" sent
  people to inspect paths that were correct. It now distinguishes a wrong working directory from
  a vault that simply has no notes yet.
- **`research_router` advertised behaviour that was deliberately removed.** It claimed the deep
  lane declares its own model; no shipped skill declares one, and the manifest records the removal.
- **`research_router` contradicted itself.** "Routes only; never does the research itself" against
  a quick lane instructing it to search directly, and a code lane forbidding the only network tool
  it was granted. Both lanes now hand back to the main session.
- **`source_grading` and `citation_checker` gave opposite defaults on the same conflict** —
  recency-wins versus authority-wins — and both load in the same workflow. The rule now carries
  the exception explicitly: authority decides a disagreement about one figure.
- **`report_builder`'s markdown template omitted two of the five sections `report_format`
  mandates** (TL;DR and Sources), while the HTML template in the same skill obeyed all five.
- **The plugin archive shipped an unrendered `{{VAULT_PATH}}`.** The plugin channel copies bytes
  and has no target project to resolve placeholders against. `capture_url` now uses
  project-relative paths, and the adapter README states the limitation.
- **`capture_url` defined three source types but one filename pattern**, with a hardcoded
  `article_` prefix.
- **Unmeasured thresholds were stated as fact** in the embeddings README (chunk crossover,
  score floor) — the same class the project bans on the landing page. Now labelled as starting
  points.
- **"The only network call is to `localhost`"** was absolute, while both scripts accept
  `--endpoint`. The claim is now scoped to the default.
- Every kit manifest still declared `1.3.0` while customers receive `1.4.0`.

### Still open after this release

- `INSTALL.en.md` / `INSTALL.ru.md` now document the questionnaire, but the questions themselves
  only appear on a real terminal; scripted and `--yes` installs take defaults silently.
- The kit's one real-data proof artifact, `demo/report_isolated_verification_2026-07-18.md`, cites
  internal records that a buyer cannot open. Honestly disclosed in the document, but the kit's own
  `citation_checker` would mark those sources UNREACHABLE. A second demo built on public sources
  would let a stranger re-run the proof end to end.
