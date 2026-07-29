#!/usr/bin/env python3
"""Adapter — mirror an installed Claude OS tree into Cursor's layout.

  python3 cursor_sync.py --target /path/to/project [--dry-run]

Claude reads `.claude/`; Cursor reads `.cursor/`. Same content, two locations. This script
copies one way only — Claude is the source of truth. Edit under `.claude/`, run this, never
the reverse: a two-way sync between two folders with no merge base loses edits.

Writes only when content differs, so a repeat run reports 0 changes.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RULE_HEADER = """---
description: {name}
alwaysApply: false
---

"""


def sync_file(src: Path, dst: Path, transform=None, dry_run: bool = False) -> bool:
    content = src.read_text(encoding="utf-8")
    if transform:
        content = transform(content, src)
    if dst.is_file() and dst.read_text(encoding="utf-8") == content:
        return False
    if not dry_run:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Sync .claude/ into .cursor/")
    ap.add_argument("--target", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.target).expanduser().resolve()
    claude = root / ".claude"
    if not claude.is_dir():
        sys.exit(f"ERROR: no .claude/ in {root}. Install the kit first.")

    changed = total = 0

    for src in sorted((claude / "agents").glob("*.md")):
        total += 1
        if sync_file(src, root / ".cursor" / "agents" / src.name, dry_run=args.dry_run):
            changed += 1
            print(f"  agents/{src.name}")

    def as_mdc(content: str, src: Path) -> str:
        if content.lstrip().startswith("---"):
            return content
        return RULE_HEADER.format(name=src.stem.replace("_", " ")) + content

    for src in sorted((claude / "rules").glob("*.md")):
        total += 1
        dst = root / ".cursor" / "rules" / (src.stem + ".mdc")
        if sync_file(src, dst, transform=as_mdc, dry_run=args.dry_run):
            changed += 1
            print(f"  rules/{dst.name}")

    for src in sorted((claude / "skills").glob("*/SKILL.md")):
        total += 1
        dst = root / ".cursor" / "skills" / src.parent.name / "SKILL.md"
        if sync_file(src, dst, dry_run=args.dry_run):
            changed += 1
            print(f"  skills/{src.parent.name}/SKILL.md")

    verb = "would change" if args.dry_run else "changed"
    print(f"\n{total} file(s) checked, {changed} {verb}")
    if changed == 0:
        print("Already in sync.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
