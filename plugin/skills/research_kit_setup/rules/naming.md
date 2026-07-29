# Naming Conventions

## Files

- Lowercase `snake_case`. No spaces, no hyphens.
- Exception: system files (`_index.md`, `_shared/`) keep the underscore prefix so they sort first.
- Extension always `.md` for prose, `.py` for scripts.
- Prefer ≤ 50 characters.

## Folders

- Singular for domains (`research/`, not `researches/`).
- Plural for collections (`agents/`, `rules/`, `skills/`, `templates/`).
- Underscore prefix (`_shared/`) for the cross-cutting layer, so it sorts above domains.

## Agents

- Filename matches the `name` field in the agent's frontmatter.
- Suffix `_agent` is conventional but optional. Routers use `_router`; orchestrators use `_commander`.

## Rules and skills

- Noun-oriented filenames for rules: `frontmatter.md`, `source_grading.md`.
- Action-oriented folder names for skills: `capture_url/`, `verify_deliverable/`.
- A skill is a folder containing `SKILL.md`, never a bare file.

## Migration

If an existing tree uses `kebab-case`, do not mass-rename. Rename a file the next time you edit it
for another reason. A rename-only commit costs review attention and buys nothing.
