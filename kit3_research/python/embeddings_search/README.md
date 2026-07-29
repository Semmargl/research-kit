# Semantic search over your notes — opt-in module

**Off by default.** The Research Kit works fully without it. Turn it on when keyword search stops
finding things you know you wrote — typically past a few hundred notes, or when your notes mix
languages and grep only matches one of them.

## What it is

A local semantic index. Each note is split into sections, each section is embedded by a model
running on your own machine, and search ranks by meaning rather than by shared words.

By default the only network call is to `localhost`, so your notes are never uploaded.
`--endpoint` can point either script at a remote server; if you set it, that claim no longer
holds and your note text goes wherever you pointed it.

## Requirements

| Requirement | Why | Install |
|---|---|---|
| [Ollama](https://ollama.com) running locally | Serves the embedding model | `ollama serve` |
| An embedding model, default `bge-m3` | 1024-dim, multilingual — matches RU queries to EN notes | `ollama pull bge-m3` |
| NumPy — **optional** | Faster ranking on large indexes | `pip install numpy` |

Without NumPy both scripts fall back to pure Python. We have not benchmarked the crossover — if
ranking feels slow on your index, install NumPy and compare. Treat any threshold here as a
starting point, not a measurement.

## Use

```bash
# Run these from your PROJECT ROOT, not from this folder — the note paths are
# relative to the project, the script is not.

# 1 · build the index (re-run after adding notes)
python3 scripts/embeddings_search/build_embeddings.py --notes ./00-capture ./10-reference ./30-reports

# 2 · search
python3 semantic_search.py "how do we decide when to escalate the model"
python3 semantic_search.py "cost control" --path 30-reports --k 5
python3 semantic_search.py "источники, которым мы не доверяем"
```

Output is score, note title, path and section, plus a preview.

## Options

| Flag | Default | Meaning |
|---|---|---|
| `--k` | 8 | How many results |
| `--path` | — | Only results whose path contains this string |
| `--min-score` | 0.0 | Drop weak matches. Unmeasured starting point for `bge-m3`: try 0.5, then tune on your own notes |
| `--json` | off | Machine-readable output |
| `--model` (build) | `bge-m3` | Any Ollama embedding model |
| `--max-chars` (build) | 2000 | Chunk size cap |

## Keeping it honest

- **The index goes stale.** It reflects your notes as of the last build. Rebuild after a batch of
  writing, or the search will confidently miss last week's work.
- **Semantic search ranks, it does not verify.** A high score means "similar", never "correct".
  Read the note before citing it.
- **Change the model, rebuild the index.** Vectors from different models are not comparable.
  `semantic_search.py` checks the dimension and refuses a mismatch rather than returning nonsense.
- **`index/` is derived data.** Add it to `.gitignore`; rebuild rather than commit.

## Removing it

Delete the `embeddings_search/` folder. Nothing else in the kit depends on it.
