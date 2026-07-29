#!/usr/bin/env python3
"""Adapter — export an installed Claude OS tree to a single AGENTS.md.

  python3 export_agents_md.py --target /path/to/project [--out AGENTS.md] [--dry-run]

`AGENTS.md` is the lowest common denominator: one file at the repo root that any tool
supporting agent instructions can read. Use it for tools with no native plugin format.

Content is assembled from the managed block in CLAUDE.md, the rule files, and the frontmatter
of each installed agent. Writes only on difference, so repeat runs report no change.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

BEGIN_RE = re.compile(r"<!--\s*BEGIN claude-os-core.*?-->", re.DOTALL)
END_MARK = "<!-- END claude-os-core -->"
FM_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def managed_block(claude_md: Path) -> str:
    if not claude_md.is_file():
        return ""
    text = claude_md.read_text(encoding="utf-8")
    begin = BEGIN_RE.search(text)
    end = text.find(END_MARK)
    if not begin or end == -1:
        return ""
    body = text[begin.end():end]
    return "\n".join(line for line in body.splitlines()
                     if not line.strip().startswith("<!--")).strip()


def field(frontmatter: str, key: str) -> str:
    match = re.search(rf"^{key}:\s*(.+)$", frontmatter, re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip().strip("'\"")


STUB_LINE_LIMIT = 6          # header only: title, blank, two provenance lines, blank


def would_erase_real_export(out: Path) -> bool:
    """True when `out` holds real content that an empty export is about to overwrite.

    The rule this enforces: an empty result must never be more destructive than a full one.
    Data -> anything is fine. no-data -> no-data is fine. no-data -> data is forbidden.

    Without this, pointing the adapter at the wrong directory, or running it after the kit was
    uninstalled, silently replaces a complete AGENTS.md with a four-line stub and reports
    success. Nothing errors, the exit code is 0, and the loss is only visible to whoever opens
    the file next. Three separate components in the reference system failed exactly this way
    before it was recognised as a class rather than three accidents.
    """
    if not out.is_file():
        return False
    existing = [line for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
    return len(existing) > STUB_LINE_LIMIT


def main() -> int:
    ap = argparse.ArgumentParser(description="Export AGENTS.md from an installed kit tree.")
    ap.add_argument("--target", required=True)
    ap.add_argument("--out", default="AGENTS.md")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true",
                    help="write even when the export found nothing and would blank an "
                         "existing AGENTS.md")
    args = ap.parse_args()

    root = Path(args.target).expanduser().resolve()
    claude = root / ".claude"
    if not claude.is_dir():
        sys.exit(f"ERROR: no .claude/ in {root}. Install the kit first.")

    parts = ["# AGENTS.md",
             "",
             "Generated from the Claude OS Kits install by "
             "`.claude/adapters/agents_md_export/export_agents_md.py`.",
             "Regenerate after changing rules or agents; do not hand-edit this file.",
             ""]

    block = managed_block(root / "CLAUDE.md")
    if block:
        parts += ["## Core instructions", "", block, ""]

    rules = sorted((claude / "rules").glob("*.md"))
    if rules:
        parts += ["## Rules", ""]
        for rule in rules:
            text = rule.read_text(encoding="utf-8")
            text = FM_RE.sub("", text).strip()
            parts += [f"<details><summary>{rule.stem}</summary>", "", text, "", "</details>", ""]

    agents = sorted((claude / "agents").glob("*.md"))
    if agents:
        parts += ["## Agents", "",
                  "| Agent | Model | Use for |", "|---|---|---|"]
        for agent in agents:
            fm_match = FM_RE.search(agent.read_text(encoding="utf-8"))
            fm = fm_match.group(1) if fm_match else ""
            name = field(fm, "name") or agent.stem
            model = field(fm, "model") or "sonnet"
            desc = " ".join(field(fm, "description").split())[:160] or "—"
            parts.append(f"| `{name}` | {model} | {desc} |")
        parts.append("")

    skills = sorted((claude / "skills").glob("*/SKILL.md"))
    if skills:
        parts += ["## Skills", ""]
        for skill in skills:
            fm_match = FM_RE.search(skill.read_text(encoding="utf-8"))
            fm = fm_match.group(1) if fm_match else ""
            desc = " ".join(field(fm, "description").split())[:160] or "—"
            parts.append(f"- **{skill.parent.name}** — {desc}")
        parts.append("")

    content = "\n".join(parts).rstrip() + "\n"
    out = root / args.out
    found_anything = bool(block or rules or agents or skills)

    if out.is_file() and out.read_text(encoding="utf-8") == content:
        print(f"{out.name} already current — no change.")
        return 0

    if not found_anything and not args.force and would_erase_real_export(out):
        print(f"x REFUSING to write {out}.\n"
              "  This run found no managed block, no rules, no agents and no skills, so the "
              "export is an empty stub —\n"
              f"  but {out.name} on disk has real content. Writing would destroy it.\n"
              "  An empty result must never be more destructive than a full one.\n"
              "  Likely cause: wrong --target, or the kit is not installed in this project.\n"
              "  If the blank file is genuinely what you want, re-run with --force.")
        return 2

    if args.dry_run:
        print(f"Would write {out} ({len(content.splitlines())} lines)")
        return 0
    out.write_text(content, encoding="utf-8")
    print(f"Wrote {out} ({len(content.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
