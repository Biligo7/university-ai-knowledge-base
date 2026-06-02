# {{SUBJECT_NAME}} — raw

Original, unmodified PDF sources for **{{SUBJECT_NAME}}**, organised by category. The layout mirrors `kb/` exactly:

```
raw/
{{CATEGORIES_LIST}}
```

## Conventions

- **Keep originals.** Do not edit PDFs in place. The pipeline rebuilds the kb from these files every time you run `tools/regenerate.py`.
- **Preserve filenames.** They are the source of truth; the pipeline slugifies stems when writing to `kb/` and `assets/`, but the originals in here keep their PDF names so you can always trace back to the source.
- **Categorise on intake.** Decide whether a new PDF is `general`, `slides`, `exams` (or any extra category your subject uses) and drop it in the matching subfolder. Re-run the pipeline.

## Adding a new PDF

```bash
# 1. Drop the file into the right category
cp ~/Downloads/Lecture-12.pdf subjects/{{SUBJECT_SLUG}}/raw/slides/

# 2. Regenerate from the repo root
python tools/regenerate.py --subject {{SUBJECT_SLUG}}

# 3. Curate the new images and refresh the tutor (ask the image-curator and tutor-generator agents)
```
