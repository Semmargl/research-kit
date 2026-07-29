#!/usr/bin/env python3
"""Semantic search over the local note index. Opt-in module.

  python3 semantic_search.py "how do we decide when to escalate the model"
  python3 semantic_search.py "источники, которым мы не доверяем" --k 5
  python3 semantic_search.py "cost control" --path 30-reports --json

Embeds the query with the same local model used to build the index, then ranks chunks by cosine
similarity. Only the query leaves this process, and only to localhost.

Build the index first with build_embeddings.py.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.error
import urllib.request
from pathlib import Path

try:
    import numpy as np
except ImportError:
    np = None


def load_index(index_dir: Path):
    missing = [f for f in ("vectors.json", "records.json", "meta.json")
               if not (index_dir / f).is_file()]
    if missing:
        sys.exit(
            f"ERROR: index incomplete at {index_dir} (missing: {', '.join(missing)}).\n"
            f"Build it first:  python3 scripts/embeddings_search/build_embeddings.py --notes <folders>"
        )
    vectors = json.loads((index_dir / "vectors.json").read_text(encoding="utf-8"))
    records = json.loads((index_dir / "records.json").read_text(encoding="utf-8"))
    meta = json.loads((index_dir / "meta.json").read_text(encoding="utf-8"))
    if len(vectors) != len(records):
        sys.exit(f"ERROR: index corrupt — {len(vectors)} vectors vs {len(records)} records. Rebuild it.")
    return vectors, records, meta


def embed_query(text: str, model: str, endpoint: str) -> list[float]:
    payload = json.dumps({"model": model, "input": [text]}).encode()
    req = urllib.request.Request(endpoint, data=payload,
                                 headers={"content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            vec = json.loads(resp.read())["embeddings"][0]
    except urllib.error.URLError as exc:
        sys.exit(
            f"ERROR: cannot reach the embedding server at {endpoint} ({exc.reason}).\n"
            f"Start it with:  ollama serve"
        )
    norm = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / norm for x in vec]


def rank(vectors, query):
    if np is not None:
        sims = np.asarray(vectors, dtype="float32") @ np.asarray(query, dtype="float32")
        return sims.tolist()
    return [sum(a * b for a, b in zip(vec, query)) for vec in vectors]


def main() -> int:
    ap = argparse.ArgumentParser(description="Semantic search over local notes.")
    ap.add_argument("query")
    ap.add_argument("--k", type=int, default=8)
    ap.add_argument("--path", default=None, help="only results whose path contains this string")
    ap.add_argument("--min-score", type=float, default=0.0)
    ap.add_argument("--index", default=None)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--endpoint", default=None,
                    help="override the embedding server recorded in the index's meta.json")
    args = ap.parse_args()

    index_dir = Path(args.index) if args.index else Path(__file__).resolve().parent / "index"
    vectors, records, meta = load_index(index_dir)

    # The query must be embedded by the same server that built the index, so meta.json wins by
    # default and --endpoint is an explicit override for a server that has since moved.
    query = embed_query(args.query, meta.get("model", "bge-m3"),
                        args.endpoint or meta.get("endpoint",
                                                  "http://localhost:11434/api/embed"))
    if len(query) != meta.get("dim", len(query)):
        sys.exit(f"ERROR: query dim {len(query)} != index dim {meta.get('dim')}. "
                 f"The index was built with a different model — rebuild it.")

    scores = rank(vectors, query)
    order = sorted(range(len(scores)), key=lambda i: -scores[i])

    results = []
    for idx in order:
        record = records[idx]
        if args.path and args.path not in record["path"]:
            continue
        if scores[idx] < args.min_score:
            continue
        results.append(dict(record, score=round(float(scores[idx]), 4)))
        if len(results) >= args.k:
            break

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=1))
        return 0

    if not results:
        print("No matches. Try a broader query, or lower --min-score.")
        return 0

    for record in results:
        location = f'{record["path"]}'
        if record.get("heading"):
            location += f' § {record["heading"]}'
        preview = " ".join(record.get("text_preview", "").split())[:110]
        print(f'{record["score"]:.3f}  {record["title"]}')
        print(f'        {location}')
        print(f'        {preview}…\n')
    return 0


if __name__ == "__main__":
    sys.exit(main())
