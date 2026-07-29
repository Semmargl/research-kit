#!/usr/bin/env python3
"""Claude OS Kits — uninstaller.

  python3 core/install/uninstall.py --target ~/my-project --kit all

Removes only what the installer recorded in `.claude_os/installed.json`, and only
when the file on disk still matches the hash recorded at install time. A file you
edited afterwards is left alone and reported — the uninstaller does not decide
that your edits were disposable.

The managed block is stripped from CLAUDE.md; everything outside the markers stays.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

BEGIN_RE = re.compile(r"<!--\s*BEGIN claude-os-core.*?-->", re.DOTALL)
END_MARK = "<!-- END claude-os-core -->"
STATE_FILE = ".claude_os/installed.json"
CONFIG_FILE = "claude_os.config.json"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def strip_block(current: str) -> str:
    begin = BEGIN_RE.search(current)
    end = current.find(END_MARK)
    if begin and end != -1 and end > begin.start():
        head = current[: begin.start()].rstrip()
        tail = current[end + len(END_MARK):].lstrip()
        joined = (head + "\n\n" + tail).strip()
        return joined + "\n" if joined else ""
    return current


def main() -> int:
    ap = argparse.ArgumentParser(description="Remove Claude OS Kits from a project.")
    ap.add_argument("--target", required=True)
    ap.add_argument("--kit", action="append", default=[], help="kit name or 'all'")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--purge-config", action="store_true",
                    help="also delete claude_os.config.json and .claude_os/")
    args = ap.parse_args()

    target = Path(args.target).expanduser().resolve()
    state_path = target / STATE_FILE
    if not state_path.is_file():
        print(f"Nothing to do: no install state at {state_path}")
        return 0

    state = json.loads(state_path.read_text(encoding="utf-8"))
    kits = args.kit or ["all"]
    if "all" in kits:
        kits = list(state.get("kits", {}))

    removed = kept = missing = 0
    for kit in kits:
        entry = state.get("kits", {}).get(kit)
        if not entry:
            print(f"[{kit}] not installed, skipping")
            continue
        print(f"[{kit}]")
        for rec in entry["files"]:
            path = target / rec["target"]
            if not path.is_file():
                missing += 1
                continue
            current = path.read_text(encoding="utf-8")

            if rec.get("mode") == "merge_block":
                stripped = strip_block(current)
                if stripped == current:
                    print(f"  no block  {rec['target']}")
                    missing += 1
                    continue
                if not args.dry_run:
                    if stripped.strip():
                        path.write_text(stripped, encoding="utf-8")
                    else:
                        path.unlink()
                print(f"  {'would strip' if args.dry_run else 'stripped'}  {rec['target']}")
                removed += 1
                continue

            if sha256(current) != rec["sha256"]:
                print(f"  KEPT      {rec['target']} (edited since install)")
                kept += 1
                continue
            if not args.dry_run:
                path.unlink()
                for parent in path.parents:
                    if parent == target:
                        break
                    if parent.is_dir() and not any(parent.iterdir()):
                        parent.rmdir()
            print(f"  {'would remove' if args.dry_run else 'removed'} {rec['target']}")
            removed += 1
        if not args.dry_run:
            state["kits"].pop(kit, None)

    if not args.dry_run:
        if state.get("kits"):
            state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                                  encoding="utf-8")
        elif args.purge_config:
            state_path.unlink()
            (target / CONFIG_FILE).unlink(missing_ok=True)
            if state_path.parent.is_dir() and not any(state_path.parent.iterdir()):
                state_path.parent.rmdir()
        else:
            state_path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n",
                                  encoding="utf-8")

    print(f"\nTOTAL: {removed} removed, {kept} kept (locally edited), {missing} already gone")
    if kept:
        print("Files you edited were left in place on purpose. Delete them by hand if you want them gone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
