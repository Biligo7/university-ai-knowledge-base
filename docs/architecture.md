# Architecture

This template separates the work into two layers:

1. **Mechanical layer** — Python scripts under `tools/`. They do deterministic things that do not need an LLM: copying files, extracting text and images from PDFs, normalising bullets, deleting tiny duplicate images, wiring up a folder tree from a template.
2. **Intelligent layer** — Markdown agent files under `agents/` and `templates/tutor-agent.md`. They do things that genuinely need a model: deciding whether an image is pedagogical, recognising that a paragraph is actually a heading, writing a tutor with a coherent topic index.

Keeping these two layers separate means the same template works in any IDE: the scripts run on plain Python, and any modern AI assistant can interpret the agent prompts.

## Data flow

```
┌─────────────────────────┐
│ user input              │
│ (subject name + PDFs +  │
│  categories + language) │
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│ kb-initializer (agent)  │
└──────────┬──────────────┘
           │ runs
           ▼
┌─────────────────────────┐
│ tools/init_subject.py   │  →  subjects/<slug>/{agents,assets,kb,raw}/
└──────────┬──────────────┘
           │ user/agent copies PDFs into raw/<category>/
           ▼
┌─────────────────────────┐
│ tools/regenerate.py     │
│   → pdf_to_md.py × N    │  →  kb/<category>/*.md  +  assets/<pdf>/*.{png,jpg}
│   → format_md.py        │
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│ tools/filter_images.py  │  →  deletes tiny / repeated images
│   --apply               │      and strips dead MD references
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│ image-curator (agent)   │  →  vision pass: deletes decorative images
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│ md-formatter (agent)    │  →  visual pass: promotes headings, fences pseudocode
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│ tutor-generator (agent) │  →  subjects/<slug>/agents/<slug>-tutor.md
└──────────┬──────────────┘
           ▼
┌─────────────────────────┐
│ ready-to-use tutor      │
└─────────────────────────┘
```

## Per-subject folder

Every subject created by the pipeline looks like this:

```
subjects/<slug>/
├── README.md          # summary, layout, how to talk to the tutor
├── agents/
│   ├── README.md
│   └── <slug>-tutor.md  # written by tutor-generator (e.g. algorithms-tutor.md)
├── assets/
│   └── <pdf-slug>/    # one folder per source PDF
│       └── p###-i##.{png,jpg}
├── kb/
│   ├── README.md
│   ├── general/       # one .md per PDF in raw/general/
│   ├── slides/        # one .md per PDF in raw/slides/
│   └── exams/         # one .md per PDF in raw/exams/
└── raw/
    ├── README.md
    ├── general/       # original PDFs
    ├── slides/
    └── exams/
```

Categories are configurable. The defaults (`general`, `slides`, `exams`) cover most courses; you can pass `--categories general slides exams labs tutorials` to `init_subject.py` to add more.

## Why this split

| Concern | Where it lives | Why |
|---|---|---|
| PDF text extraction | `tools/pdf_to_md.py` | Deterministic, deps-only, runs offline. |
| Image extraction | `tools/pdf_to_md.py` | Same — `pypdf` does the heavy lifting. |
| Mechanical image filtering (tiny, duplicate) | `tools/filter_images.py` | Pure heuristics; LLMs do not need to look at 200 logos. |
| Pedagogical image curation | `image-curator` agent | Needs vision and judgement. |
| Markdown normalisation (bullets, blanks, footers) | `tools/format_md.py` | Pure pattern matching; runs in a fraction of a second. |
| Heading promotion, code-fencing | `md-formatter` agent | Needs context awareness. |
| Tutor authoring | `tutor-generator` agent | Needs to read the kb and synthesise a coherent index. |
| Day-to-day Q&A | per-subject `<slug>-tutor.md` | The end product. |

## Adding capabilities

The cleanest way to extend the template is to add a new agent under `agents/` and a small script under `tools/` if it needs deterministic work. Update the relevant READMEs and `docs/workflow.md` so users can find it.

Common extensions:

- A **flashcard generator** agent that reads the tutor and produces Anki-format cards into `subjects/<slug>/flashcards.csv`.
- A **practice quizzer** agent that runs an oral-exam loop using past exam questions.
- An **OCR fallback script** that handles scanned PDFs (`pypdf` only reads embedded text). A wrapper around `pytesseract` would slot into `tools/` and be called from `pdf_to_md.py` when `extract_text()` returns nothing.
