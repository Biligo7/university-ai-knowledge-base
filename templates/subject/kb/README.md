# {{SUBJECT_NAME}} — kb (knowledge base)

Markdown copies of every source PDF, organised by category.

```
kb/
{{CATEGORIES_LIST}}
```

Each `.md` mirrors a PDF in the sibling `raw/` folder, with the same stem. Pages from the PDF appear under `## Page N` headings and the original images sit in `../assets/<pdf-stem>/`, referenced with `![...](...)` lines.

## Conventions

- One Markdown file per source PDF. Do not split a PDF across files; the page headings make navigation easy.
- Filenames are slugified (lowercase, hyphens) regardless of the original PDF name; the original name is kept in `raw/` so you can always trace back.
- Do not hand-edit these files unless the heuristic formatter or the `md-formatter` agent is leaving something obviously wrong. Prefer to fix the script and re-run `tools/regenerate.py`.

## Re-running the pipeline

If you add a PDF to `raw/`, regenerate from the repository root:

```bash
python tools/regenerate.py --subject {{SUBJECT_SLUG}}
```

This wipes `kb/` (preserving READMEs) and `assets/` (unless `--keep-assets` is passed) and rebuilds from `raw/`.
