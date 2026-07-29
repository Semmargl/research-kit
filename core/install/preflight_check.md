# Preflight Check

Two minutes before install. Paste this into a Claude session opened in the target project,
or walk it yourself.

## Checklist

```
- [ ] python3 --version prints 3.8 or newer
- [ ] I know the absolute path of the project root
- [ ] If CLAUDE.md already exists: I have read it and know what is in it
- [ ] The project is under version control, or I have a copy — so I can diff what changed
- [ ] I decided which kits I need (core is automatic)
- [ ] I know my model-cost ceiling for OPUS_GATE_% (10% is a sane default)
```

## Three failures this catches

| Failure | Symptom later | Prevention |
|---|---|---|
| No version control | Cannot tell what the installer changed vs. what you changed | `git init` first, commit, then install |
| Existing `CLAUDE.md` with conflicting instructions | Two response protocols disagree; the model follows the wrong one | Read your file first; the managed block is merged, not merged-and-reconciled |
| Installing into the wrong folder | A `.claude/` tree appears somewhere unexpected and does nothing | Use an absolute path, and dry-run first |

## Existing CLAUDE.md

The installer inserts a block between markers and never touches text outside them. It does **not**
resolve contradictions. If your file already says "always answer in long prose" and the block says
"TL;DR first", the model gets two orders. Read your own file, remove what now conflicts, then install.

## Dry run is the real preflight

```bash
python3 core/install/install.py --target /path/to/project --kit all --dry-run
```

Nothing is written. If the printed list surprises you, stop and find out why.
