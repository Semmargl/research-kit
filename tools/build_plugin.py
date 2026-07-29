#!/usr/bin/env python3
"""Assemble the Claude Code plugin channel from the kit sources.

    python3 tools/build_plugin.py           # build plugin/ from the kit
    python3 tools/build_plugin.py --check   # fail if plugin/ has drifted

The plugin directory is committed so a marketplace can clone it, but it is
generated, never hand-edited. `--check` runs in CI to catch the drift that
made the old plugin channel unshippable: a manifest nobody rebuilt.

One authored file lives inside the generated tree and is never touched here:
skills/research_kit_setup/SKILL.md. It installs what a plugin cannot carry.

Stdlib only. Python 3.8+.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugin"

MARKETPLACE_NAME = "semmargl"
PLUGIN_NAME = "research-kit"

# kit source -> path inside the plugin
AGENTS = {
    "kit3_research/agents/research_router.md": "agents/research_router.md",
    "kit3_research/agents/citation_checker.md": "agents/citation_checker.md",
    "core/agents/install_verifier.md": "agents/install_verifier.md",
}
SKILLS = {
    "kit3_research/skills/deep_research/SKILL.md": "skills/deep_research/SKILL.md",
    "kit3_research/skills/capture_url/SKILL.md": "skills/capture_url/SKILL.md",
    "kit3_research/skills/report_builder/SKILL.md": "skills/report_builder/SKILL.md",
}
# Rules cannot be a plugin component. They ride as supporting files of the
# setup skill, which writes them into the project's .claude/rules/ on request.
RULES = {
    f"{src}/rules/{name}.md": f"skills/research_kit_setup/rules/{name}.md"
    for src, names in (
        ("core", ["naming", "writing_style", "model_routing", "review_policy"]),
        ("kit3_research", ["source_grading", "report_format"]),
    )
    for name in names
}

AUTHORED = {"skills/research_kit_setup/SKILL.md"}


def manifest() -> dict:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    return {
        "name": PLUGIN_NAME,
        "version": version,
        "description": (
            "Analyst-grade research for Claude Code: a router that picks one lane, "
            "multi-angle search with adversarial verification, and an isolated citation "
            "checker that grades claims against the sources rather than the author."
        ),
        "author": {"name": "Vladyslav", "email": "decebel1995@gmail.com"},
        "license": "CC-BY-NC-SA-4.0",
        "keywords": ["research", "verification", "citations", "sources"],
    }


def marketplace() -> dict:
    return {
        "name": MARKETPLACE_NAME,
        "owner": {"name": "Vladyslav", "email": "decebel1995@gmail.com"},
        "metadata": {
            "description": (
                "Research tooling for Claude Code by Vladyslav. Sourced, verifiable "
                "research: one-lane routing, adversarial verification, isolated citation "
                "checking. CC BY-NC-SA 4.0 — noncommercial use is free."
            )
        },
        "plugins": [
            {
                "name": PLUGIN_NAME,
                "source": "./plugin",
                "description": (
                    "Research with sources that hold up: one-lane routing, adversarial "
                    "verification, isolated citation checking. Run /research-kit-setup "
                    "after install to add the rules a plugin cannot carry."
                ),
            }
        ],
    }


def planned() -> dict:
    """Every generated file: plugin-relative path -> content."""
    out = {}
    for src, dst in {**AGENTS, **SKILLS, **RULES}.items():
        p = ROOT / src
        if not p.is_file():
            sys.exit(f"ERROR: kit source missing: {src}")
        out[dst] = p.read_text(encoding="utf-8")
    out[".claude-plugin/plugin.json"] = json.dumps(manifest(), indent=2) + "\n"
    return out


def build(check: bool) -> int:
    files = planned()
    drift = []

    for rel, content in files.items():
        dst = PLUGIN / rel
        current = dst.read_text(encoding="utf-8") if dst.is_file() else None
        if current == content:
            continue
        drift.append(rel)
        if not check:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(content, encoding="utf-8")

    # anything generated that is no longer planned is stale and must go
    known = set(files) | AUTHORED
    for f in sorted(PLUGIN.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(PLUGIN).as_posix()
        if rel not in known:
            drift.append(f"{rel} (stale)")
            if not check:
                f.unlink()

    mkt = ROOT / ".claude-plugin" / "marketplace.json"
    content = json.dumps(marketplace(), indent=2) + "\n"
    if not mkt.is_file() or mkt.read_text(encoding="utf-8") != content:
        drift.append(".claude-plugin/marketplace.json")
        if not check:
            mkt.parent.mkdir(parents=True, exist_ok=True)
            mkt.write_text(content, encoding="utf-8")

    missing = [a for a in AUTHORED if not (PLUGIN / a).is_file()]
    if missing:
        print("ERROR: authored file(s) absent — the plugin is incomplete:")
        for m in missing:
            print(f"  {m}")
        return 1

    if check:
        if drift:
            print(f"DRIFT: {len(drift)} file(s) differ from the kit sources:")
            for d in drift:
                print(f"  {d}")
            print("\nRun: python3 tools/build_plugin.py")
            return 1
        print(f"in sync — {len(files)} generated files match the kit")
        return 0

    print(f"built {PLUGIN.relative_to(ROOT)}/ — {len(files)} generated, "
          f"{len(AUTHORED)} authored, {len(drift)} changed this run")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true",
                    help="report drift and exit non-zero; change nothing")
    sys.exit(build(ap.parse_args().check))
