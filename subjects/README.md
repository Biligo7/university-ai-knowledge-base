# subjects/

One folder per subject. Each folder is fully self-contained: it has its own raw PDFs, Markdown kb, extracted images, and tutor agent. Subjects do not depend on each other and can be deleted independently.

## How a subject gets here

You do not create subject folders by hand. Ask the `kb-initializer` agent (in [`../agents/`](../agents)) — it runs `tools/init_subject.py` for you and then drives the rest of the pipeline. See [`../docs/workflow.md`](../docs/workflow.md) for the end-to-end recipe.

## Layout of a populated subject

```
subjects/<slug>/
├── README.md
├── agents/         # subject-scoped agents; the tutor lives here once tutor-generator has run
│   └── tutor.md
├── assets/         # one subfolder per source PDF, holding extracted images
├── kb/             # markdown copies of every source PDF
│   ├── general/
│   ├── slides/
│   └── exams/
└── raw/            # original PDFs, untouched, mirrors kb/'s category layout
    ├── general/
    ├── slides/
    └── exams/
```

## Current subjects

_None yet. Run the `kb-initializer` agent to create one._

When you add a subject, list it here as a one-line bullet pointing to the folder, for example:

```markdown
- [`algorithms/`](algorithms/) — Algorithms course (Spring 2026), slides + tutorials + past exams.
```
