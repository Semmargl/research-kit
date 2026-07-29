#!/usr/bin/env python3
"""Build local semantic embeddings over your notes. Opt-in module.

  python3 build_embeddings.py --notes ./00-capture ./10-reference ./30-reports

Embeds each note with a LOCAL model served by Ollama, L2-normalises the vectors so cosine
similarity is a plain dot product, and writes the index next to this script.

Nothing leaves the machine: the only network call is to localhost.

Output (in ./index/):
  vectors.json  list[list[float]], L2-normalised, aligned with records.json
  records.json  id -> {path, title, heading, text_preview}
  meta.json     model, endpoint, dim, count, generated_at

NumPy is used when available and is not required — with a few thousand notes the pure-Python
path is fast enough. See README.md for setup.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

try:
    import numpy as np
except ImportError:  # pure-Python fallback, no third-party requirement
    np = None

DEFAULT_MODEL = "bge-m3"
DEFAULT_ENDPOINT = "http://localhost:11434/api/embed"
BATCH = 32
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,3})\s+(.*)$", re.MULTILINE)


def strip_frontmatter(text: str) -> tuple[str, str]:
    match = FM_RE.match(text)
    if not match:
        return "", text
    title = ""
    found = re.search(r"^title:\s*(.+)$", match.group(1), re.MULTILINE)
    if found:
        title = found.group(1).strip().strip("'\"")
    return title, text[match.end():]


def chunk_note(path: Path, root: Path, max_chars: int) -> list[dict]:
    """One chunk per H1–H3 section, so a hit points at a section rather than a whole file."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    title, body = strip_frontmatter(raw)
    title = title or path.stem.replace("_", " ")
    rel = str(path.relative_to(root)) if root in path.parents or root == path.parent else str(path)

    positions = [(m.start(), m.group(2).strip()) for m in HEADING_RE.finditer(body)]
    chunks = []
    if not positions:
        text = body.strip()
        if text:
            chunks.append({"heading": "", "text": text[:max_chars]})
    else:
        if positions[0][0] > 0:
            head = body[: positions[0][0]].strip()
            if head:
                chunks.append({"heading": "", "text": head[:max_chars]})
        for i, (start, heading) in enumerate(positions):
            end = positions[i + 1][0] if i + 1 < len(positions) else len(body)
            text = body[start:end].strip()
            if text:
                chunks.append({"heading": heading, "text": text[:max_chars]})

    out = []
    for i, chunk in enumerate(chunks):
        out.append({
            "id": f"{rel}#{i}",
            "path": rel,
            "title": title,
            "heading": chunk["heading"],
            "text": chunk["text"],
        })
    return out


def embed_batch(texts: list[str], model: str, endpoint: str) -> list[list[float]]:
    payload = json.dumps({"model": model, "input": texts}).encode()
    req = urllib.request.Request(endpoint, data=payload,
                                 headers={"content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            return json.loads(resp.read())["embeddings"]
    except urllib.error.URLError as exc:
        sys.exit(
            f"ERROR: cannot reach the embedding server at {endpoint} ({exc.reason}).\n"
            f"Start it with:  ollama serve\n"
            f"Pull the model: ollama pull {model}"
        )


def normalise(vectors: list[list[float]]) -> list[list[float]]:
    if np is not None:
        arr = np.asarray(vectors, dtype="float32")
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return (arr / norms).tolist()
    out = []
    for vec in vectors:
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        out.append([x / norm for x in vec])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Build a local semantic index over markdown notes.")
    ap.add_argument("--notes", nargs="+", required=True, help="folders to index")
    ap.add_argument("--out", default=None, help="index folder (default: ./index next to this script)")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    ap.add_argument("--max-chars", type=int, default=2000, help="max characters per chunk")
    args = ap.parse_args()

    out_dir = Path(args.out) if args.out else Path(__file__).resolve().parent / "index"

    records: list[dict] = []
    missing_dirs: list[str] = []
    skipped_underscore = 0
    for folder in args.notes:
        root = Path(folder).expanduser().resolve()
        if not root.is_dir():
            print(f"  skipping {root} — not a directory")
            missing_dirs.append(folder)
            continue
        for path in sorted(root.rglob("*.md")):
            if path.name.startswith("_"):
                skipped_underscore += 1
                continue
            records.extend(chunk_note(path, root, args.max_chars))

    if not records:
        # Two very different causes, and the old message named only one of them. On a fresh
        # install the vault skeleton holds nothing but `_index.md` files, which are skipped by
        # design — so "check the --notes paths" sent people to look at paths that were correct.
        if missing_dirs:
            sys.exit("ERROR: no markdown notes found. These paths are not directories: "
                     + ", ".join(missing_dirs)
                     + "\n       Run this from your PROJECT ROOT — the note paths are relative "
                       "to it, the script is not.")
        if skipped_underscore:
            sys.exit(f"ERROR: no notes to index yet. Found {skipped_underscore} file(s) starting "
                     "with '_' (index/skeleton files, skipped by design) and no real notes.\n"
                     "       This is the expected state of a fresh install: capture some sources "
                     "first, then build the index.")
        sys.exit("ERROR: no markdown notes found in: " + ", ".join(args.notes))

    print(f"Chunks to embed: {len(records)}", flush=True)
    texts = [f'{r["title"]} — {r["heading"]}\n{r["text"]}' if r["heading"]
             else f'{r["title"]}\n{r["text"]}' for r in records]

    vectors: list[list[float]] = []
    started = time.time()
    for i in range(0, len(texts), BATCH):
        vectors.extend(embed_batch(texts[i:i + BATCH], args.model, args.endpoint))
        done = min(i + BATCH, len(texts))
        print(f"  {done}/{len(texts)}  ({time.time() - started:.0f}s)", flush=True)

    vectors = normalise(vectors)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "vectors.json").write_text(json.dumps(vectors), encoding="utf-8")
    trimmed = []
    for record in records:
        entry = {k: v for k, v in record.items() if k != "text"}
        entry["text_preview"] = record["text"][:280]
        trimmed.append(entry)
    (out_dir / "records.json").write_text(json.dumps(trimmed, ensure_ascii=False),
                                          encoding="utf-8")
    # `endpoint` is recorded because the query side reads it back: an index built against a
    # non-default server was unqueryable without hand-editing meta.json, since semantic_search.py
    # looked for a key nothing ever wrote and silently fell through to localhost:11434. A
    # supported flag on one side and a dead read on the other is the quietest kind of broken.
    (out_dir / "meta.json").write_text(json.dumps({
        "model": args.model,
        "endpoint": args.endpoint,
        "dim": len(vectors[0]) if vectors else 0,
        "count": len(vectors),
        "normalized": True,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }, indent=2), encoding="utf-8")

    print(f"DONE: {len(vectors)} vectors, dim {len(vectors[0])} -> {out_dir} "
          f"({time.time() - started:.0f}s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
