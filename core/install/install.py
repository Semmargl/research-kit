#!/usr/bin/env python3
"""Claude OS Kits — installer.

Manifest-driven, idempotent, delta-merging.

  python3 core/install/install.py --target ~/my-project --kit all

Design contract (this is what makes a second run a no-op):

1. Every file the installer touches is listed in a kit `manifest.json`.
2. Placeholder values are resolved once and written to `claude_os.config.json`
   in the target. Later runs read that file, so they render identical output.
3. The installer writes a file only when the rendered bytes differ from what is
   on disk. Unchanged files are counted, not rewritten.
4. Files the user edited after install are detected by hash and skipped, not
   clobbered. `--force` overrides.
5. `CLAUDE.md` is never overwritten — a marked block is merged into it.

Stdlib only. Python 3.8+.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

KITS = ["core", "kit1_reliability", "kit2_growth", "kit3_research"]

BEGIN_RE = re.compile(r"<!--\s*BEGIN claude-os-core.*?-->", re.DOTALL)
END_MARK = "<!-- END claude-os-core -->"

STATE_FILE = ".claude_os/installed.json"
CONFIG_FILE = "claude_os.config.json"

DEFAULT_PLACEHOLDERS = {
    "PROJECT_NAME": "My Project",
    "VAULT_PATH": ".",
    "LANG": "en",
    "DOMAIN_LIST": "research, engineering",
    "OPUS_GATE_%": "10%",
}


# ---------------------------------------------------------------- helpers


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def render(text: str, placeholders: dict) -> str:
    for key, value in placeholders.items():
        text = text.replace("{{" + key + "}}", str(value))
    return text


def read_json(path: Path, default=None):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"ERROR: {path} is not valid JSON: {exc}")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def merge_block(current: str, block: str) -> str:
    """Insert or replace the managed block. Text outside the markers survives."""
    begin = BEGIN_RE.search(current)
    end = current.find(END_MARK)
    if begin and end != -1 and end > begin.start():
        head = current[: begin.start()]
        tail = current[end + len(END_MARK):]
        return head + block.strip() + tail
    if current.strip():
        return current.rstrip() + "\n\n" + block.strip() + "\n"
    return block.strip() + "\n"


DEFAULT_REVIEW = {
    "verifier_tiers": ["client_facing", "rule_or_agent_edits", "irreversible", "cited_reports"],
    "judge_mode": "sample",
    "judge_on_internal_deliverables": True,
    "skip_classes": ["quick_facts", "routine_bookkeeping", "throwaway_drafts", "pure_chat"],
    "weekly_retro": False,
    "retro_day": "sun",
    "retro_time": "11:00",
    "scheduled_task_created": False,
}

RETRO_DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]

# The questionnaire below decides WHEN the system works. Without it every install gets the
# same depth of checking on every task, which is the failure the triage rule exists to stop:
# an expensive verifier on trivia trains people to ignore it, and no verifier on a client
# deliverable is how "done" ships broken.
REVIEW_QUESTIONS = [
    ("verifier_tiers",
     "Tier 1 — run the isolated verifier BEFORE delivery on which kinds of work?",
     [("client_facing", "anything that leaves your hands: client deliverables, sellable output"),
      ("rule_or_agent_edits", "edits to always-load rules or agents (changes every later session)"),
      ("irreversible", "hard-to-undo work: migrations, deploys, mass edits"),
      ("cited_reports", "research or audit conclusions that will be cited later")]),
    ("skip_classes",
     "Tier 3 — skip both checks entirely on which kinds of work?",
     [("quick_facts", "quick factual lookups"),
      ("routine_bookkeeping", "routine bookkeeping, CRM, sourcing, briefings"),
      ("throwaway_drafts", "one-off drafts for yourself"),
      ("pure_chat", "plain conversation")]),
]


def ask_yes_no(prompt: str, default: bool) -> bool:
    suffix = "Y/n" if default else "y/N"
    answer = input(f"  {prompt} [{suffix}]: ").strip().lower()
    if not answer:
        return default
    return answer.startswith("y")


def resolve_review(target: Path, non_interactive: bool) -> dict:
    """When should this system do its checking? Asked once, stored, reused forever after.

    Stored in claude_os.config.json under "review". Rules and agents read it from there;
    nothing in the kit hard-codes a policy, because the right answer depends on what the
    person actually does all day.
    """
    stored = read_json(target / CONFIG_FILE, default={}) or {}
    if "review" in stored:
        policy = dict(DEFAULT_REVIEW)
        policy.update(stored["review"])
        return policy

    policy = dict(DEFAULT_REVIEW)
    if non_interactive or not sys.stdin.isatty():
        return policy

    print("When should this system check its own work?")
    print("Enter keeps the default. You can change any of it later in "
          f"{CONFIG_FILE}.\n")

    for key, question, options in REVIEW_QUESTIONS:
        print(f"{question}")
        chosen = []
        for value, label in options:
            if ask_yes_no(f"{label}?", value in DEFAULT_REVIEW[key]):
                chosen.append(value)
        policy[key] = chosen
        print()

    print("Tier 2 — the cheap judge scores finished work after delivery.")
    policy["judge_on_internal_deliverables"] = ask_yes_no(
        "Score internal deliverables with the judge?", True)
    if policy["judge_on_internal_deliverables"]:
        mode = input("  Score every run or a sample? [sample/all]: ").strip().lower()
        policy["judge_mode"] = "all" if mode == "all" else "sample"
    print()

    print("Weekly retro — batches proposals for you to accept or reject.")
    policy["weekly_retro"] = ask_yes_no("Enable a weekly retro?", False)
    if policy["weekly_retro"]:
        day = input(f"  Day [{policy['retro_day']}] ({'/'.join(RETRO_DAYS)}): ").strip().lower()
        if day in RETRO_DAYS:
            policy["retro_day"] = day
        when = input(f"  Time, 24h [{policy['retro_time']}]: ").strip()
        if re.fullmatch(r"\d{1,2}:\d{2}", when or ""):
            policy["retro_time"] = when
    print()
    return policy


def report_retro_schedule(policy: dict) -> None:
    """Print the schedule the user asked for. Deliberately does NOT create it.

    Writing a recurring job into someone's machine because they answered a question during an
    install is not a decision an installer gets to make. The command is printed; running it is
    the user's call, and the config records that it has not been run.
    """
    if not policy.get("weekly_retro"):
        return
    day = policy.get("retro_day", "sun")
    hh, mm = (policy.get("retro_time", "11:00").split(":") + ["00"])[:2]
    dow = RETRO_DAYS.index(day) + 1 if day != "sun" else 0
    print("\nWeekly retro requested — NOT scheduled for you. To schedule it yourself:")
    print(f"  cron:  {int(mm)} {int(hh)} * * {dow}    "
          "(runs the improve_retro skill; it proposes, you accept or reject)")
    print("  The config records scheduled_task_created=false until you set it up.")


# ---------------------------------------------------------------- config


def resolve_config(target: Path, overrides: dict, non_interactive: bool) -> dict:
    """Placeholder values, resolved once and reused forever after."""
    stored = read_json(target / CONFIG_FILE, default=None)
    if stored is not None:
        values = dict(DEFAULT_PLACEHOLDERS)
        values.update(stored.get("placeholders", {}))
        values.update(overrides)
        return values

    values = dict(DEFAULT_PLACEHOLDERS)
    values["VAULT_PATH"] = str(target)
    values["PROJECT_NAME"] = target.name
    if not non_interactive and sys.stdin.isatty():
        print("Configure placeholders (Enter keeps the default):\n")
        for key, default in values.items():
            answer = input(f"  {key} [{default}]: ").strip()
            if answer:
                values[key] = answer
        print()
    values.update(overrides)
    return values


# ---------------------------------------------------------------- install


def install_kit(kit: str, src_root: Path, target: Path, cfg: dict,
                state: dict, dry_run: bool, force: bool) -> dict:
    kit_dir = src_root / kit
    manifest = read_json(kit_dir / "manifest.json")
    if manifest is None:
        sys.exit(f"ERROR: no manifest.json in {kit_dir}")

    prev = {f["target"]: f for f in state.get("kits", {}).get(kit, {}).get("files", [])}
    stats = {"written": 0, "unchanged": 0, "skipped": 0, "missing": 0}
    recorded = []

    for entry in manifest["files"]:
        src = kit_dir / entry["path"]
        if not src.is_file():
            print(f"  MISSING  {entry['path']} (declared in manifest, absent on disk)")
            stats["missing"] += 1
            continue

        raw = src.read_text(encoding="utf-8")
        mode = entry.get("install", "copy")
        dst = target / entry["target"]

        if mode == "merge_block":
            block = render(raw, cfg)
            current = dst.read_text(encoding="utf-8") if dst.is_file() else ""
            merged = merge_block(current, block)
            if current == merged:
                stats["unchanged"] += 1
            else:
                if not dry_run:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    dst.write_text(merged, encoding="utf-8")
                stats["written"] += 1
                print(f"  {'would merge' if dry_run else 'merged'}   {entry['target']}")
            recorded.append({"target": entry["target"], "mode": mode,
                             "sha256": sha256(block), "path": entry["path"]})
            continue

        content = render(raw, cfg) if entry.get("render", True) else raw
        digest = sha256(content)

        if dst.is_file():
            on_disk = dst.read_text(encoding="utf-8")
            if sha256(on_disk) == digest:
                stats["unchanged"] += 1
                recorded.append({"target": entry["target"], "mode": mode,
                                 "sha256": digest, "path": entry["path"]})
                continue
            was = prev.get(entry["target"], {}).get("sha256")
            if was and sha256(on_disk) != was and not force:
                print(f"  SKIP     {entry['target']} (edited after install; --force to overwrite)")
                stats["skipped"] += 1
                recorded.append(prev[entry["target"]])
                continue

        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(content, encoding="utf-8")
            if src.suffix == ".py":
                dst.chmod(0o755)
        stats["written"] += 1
        print(f"  {'would write' if dry_run else 'wrote'}    {entry['target']}")
        recorded.append({"target": entry["target"], "mode": mode,
                         "sha256": digest, "path": entry["path"]})

    state.setdefault("kits", {})[kit] = {
        "version": manifest.get("version", "0.0.0"),
        "files": recorded,
    }
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description="Install Claude OS Kits into a project.")
    ap.add_argument("--target", required=True, help="project root to install into")
    ap.add_argument("--kit", action="append", default=[],
                    help="core | kit1_reliability | kit2_growth | kit3_research | all")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE",
                    help="placeholder override, repeatable")
    ap.add_argument("--dry-run", action="store_true", help="report actions, change nothing")
    ap.add_argument("--force", action="store_true", help="overwrite locally edited files")
    ap.add_argument("--yes", action="store_true", help="accept defaults, never prompt")
    args = ap.parse_args()

    src_root = Path(__file__).resolve().parents[2]
    target = Path(args.target).expanduser().resolve()
    target.mkdir(parents=True, exist_ok=True)

    kits = args.kit or ["all"]
    if "all" in kits:
        kits = KITS
    for kit in kits:
        if kit not in KITS:
            sys.exit(f"ERROR: unknown kit '{kit}'. Known: {', '.join(KITS)}")
    if "core" not in kits:
        kits = ["core"] + kits          # Core-Lite is a hard dependency of every kit

    overrides = {}
    for pair in args.set:
        if "=" not in pair:
            sys.exit(f"ERROR: --set expects KEY=VALUE, got '{pair}'")
        key, value = pair.split("=", 1)
        overrides[key] = value

    cfg = resolve_config(target, overrides, args.yes)
    review = resolve_review(target, args.yes)
    state = read_json(target / STATE_FILE, default={"version": "1.0.0", "kits": {}})

    print(f"Installing into {target}\n")
    total = {"written": 0, "unchanged": 0, "skipped": 0, "missing": 0}
    for kit in kits:
        print(f"[{kit}]")
        stats = install_kit(kit, src_root, target, cfg, state, args.dry_run, args.force)
        for key in total:
            total[key] += stats[key]
        print(f"  -> {stats['written']} written, {stats['unchanged']} unchanged, "
              f"{stats['skipped']} skipped, {stats['missing']} missing\n")

    if not args.dry_run:
        # Merge, never replace: an earlier version wrote {"placeholders": ...} flat, which
        # would drop the review policy on every re-install — the answers would silently
        # revert to defaults and nothing would say so.
        existing = read_json(target / CONFIG_FILE, default={}) or {}
        existing["placeholders"] = cfg
        existing["review"] = review
        write_json(target / CONFIG_FILE, existing)
        write_json(target / STATE_FILE, state)

    print(f"TOTAL: {total['written']} written, {total['unchanged']} unchanged, "
          f"{total['skipped']} skipped, {total['missing']} missing")
    if total["missing"]:
        print("\nSome manifest entries had no file on disk. The kit is incomplete — "
              "report this rather than working around it.")
        return 1
    if total["written"] == 0 and not args.dry_run:
        print("Nothing changed. This is the expected result of a repeat install.")
    if not args.dry_run:
        report_retro_schedule(review)
        print(f"\nReview policy written to {CONFIG_FILE}. "
              "Rules and agents read it from there; edit it any time.")
        print("Next: run the install verifier in a FRESH session — "
              "`Read .claude/agents/install_verifier.md and verify this install`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
