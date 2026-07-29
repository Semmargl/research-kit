# Uninstall

**From the kit folder** (the one you installed from, with `core/` inside it):

```bash
python3 core/install/uninstall.py --target /path/to/project --kit all --dry-run
python3 core/install/uninstall.py --target /path/to/project --kit all
```

**From inside the project, when the kit folder is gone.** The installer leaves a working copy
of the uninstaller in your project precisely for this case — deleting the download should not
strand you:

```bash
cd /path/to/project
python3 .claude/install/uninstall.py --target . --kit all --dry-run
python3 .claude/install/uninstall.py --target . --kit all
```

Both invocations do the same thing. Which one works depends only on where you are standing;
running the first from inside your project gives `can't open file '.../core/install/uninstall.py'`.

Remove one kit and keep the rest:

```bash
python3 core/install/uninstall.py --target /path/to/project --kit kit2_growth
```

## What gets removed

Only files recorded in `.claude_os/installed.json`, and only when the file on disk still matches
the hash recorded at install time.

| Situation | What happens |
|---|---|
| File untouched since install | Removed |
| File edited after install | **Kept**, and reported. Delete it yourself if you want it gone |
| Managed block in `CLAUDE.md` | Block stripped; everything outside the markers stays |
| Files you created yourself | Never touched — they are not in the manifest |

## Full removal

```bash
python3 core/install/uninstall.py --target /path/to/project --kit all --purge-config
```

Adds `claude_os.config.json` and `.claude_os/` to the removal. Without `--purge-config` those stay,
so a later reinstall reuses your placeholder answers.

## Data the uninstaller will not delete

`memory/` content you accumulated (decisions, learnings, buffers) is your data. The templates that
shipped with the kit are removed; the entries you wrote into them are kept, because an edited file
fails the hash check by design.
