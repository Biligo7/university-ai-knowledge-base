# templates/

Skeleton files that the pipeline copies (and templates) when a new subject is created.

| Path | Used by | Purpose |
|---|---|---|
| `subject/` | `tools/init_subject.py` | Folder layout copied verbatim under `subjects/<slug>/`. Markdown files inside are rendered with placeholder substitution (`{{SUBJECT_NAME}}`, `{{SUBJECT_SLUG}}`, `{{CATEGORIES_LIST}}`). |
| `tutor-agent.md` | `tutor-generator` agent | Skeleton for the per-subject tutor agent. The generator fills in `{{TOPIC_INDEX}}`, `{{EXAM_PATTERNS}}`, `{{IMAGE_POINTERS}}` and a few other placeholders. |

## Placeholder reference

| Placeholder | Meaning |
|---|---|
| `{{SUBJECT_NAME}}` | Human-readable subject name, e.g. *Algorithms*. |
| `{{SUBJECT_SLUG}}` | Folder name under `subjects/`, e.g. `algorithms`. |
| `{{CATEGORIES_LIST}}` | Bulleted list of the category subfolders (filled by `init_subject.py`). |
| `{{PRIMARY_LANGUAGE}}` | `Greek`, `English`, or `Mixed (Greek + English)`. |
| `{{KB_PATH}}` | `subjects/<slug>/kb/`. |
| `{{ASSETS_PATH}}` | `subjects/<slug>/assets/`. |
| `{{TOPIC_INDEX}}` | Markdown table: one row per kb file. Filled by `tutor-generator`. |
| `{{EXAM_PATTERNS}}` | Bullet list of recurring exam exercise types. Filled by `tutor-generator`. |
| `{{IMAGE_POINTERS}}` | Topic → canonical image path. Filled by `tutor-generator`. |

If you add categories or fields, update both this list and the agents that depend on them.
