# Workflow — adding a new subject end-to-end

This is the user-facing recipe. It assumes you have already cloned the repo, created a virtual environment, installed `requirements.txt`, and wired the agents into your IDE (see [`ide-integration.md`](ide-integration.md)).

## Example scenario

You are studying **Algorithms** and you have the following PDFs in your `~/Downloads`:

- 12 lecture slide decks (`Alg26-01-Intro.pdf` … `Alg26-12-NP-II.pdf`)
- 11 tutorial sheets with hints (`Tutorial 1.pdf` … `Tutorial 11.pdf`)
- 2 past exams (`Final-2024.pdf`, `Midterm-2026.pdf`)
- 1 syllabus / final-exam material summary (`Final exam material.pdf`)

You want a tutor that helps you prepare for the final.

## Steps

### 1. Start a chat with the `kb-initializer` agent

Tell it what you have. A clean message looks like this:

```
Subject: Algorithms
Slug: algorithms
Categories: general slides exams
Primary language: Greek

PDFs:
  ~/Downloads/Final exam material.pdf         :: general
  ~/Downloads/Alg26-01-Intro.pdf              :: slides
  ~/Downloads/Alg26-02-Asymptotic.pdf         :: slides
  ...
  ~/Downloads/Tutorial 1.pdf                  :: exams
  ~/Downloads/Tutorial 2.pdf                  :: exams
  ...
  ~/Downloads/Final-2024.pdf                  :: exams
  ~/Downloads/Midterm-2026.pdf                :: exams
```

> Tutorials with worked answers are most useful when filed under `exams`, because the tutor will use them as practice material.

### 2. Let the initializer drive the pipeline

It will:

1. Confirm the plan and wait for your "yes".
2. Run `python tools/init_subject.py --name "Algorithms" --slug algorithms --categories general slides exams`.
3. Copy each PDF into `subjects/algorithms/raw/<category>/`.
4. Run `python tools/regenerate.py --subject algorithms`. This produces one `.md` per PDF under `subjects/algorithms/kb/<category>/` and one folder per PDF under `subjects/algorithms/assets/`.
5. Run `python tools/filter_images.py --assets-dir subjects/algorithms/assets --apply` to delete tiny/duplicate images and prune dead Markdown references.
6. Hand off to `image-curator`, which opens every remaining image and removes decorative ones (logos, portraits, banners, screenshots).
7. Hand off to `md-formatter`, which spots-checks the Markdown and applies any leftover formatting fixes.
8. Hand off to `tutor-generator`, which writes `subjects/algorithms/agents/algorithms-tutor.md`.

You should see one short progress line per step.

### 3. Talk to your tutor

Open `subjects/algorithms/agents/algorithms-tutor.md` in your IDE and load it as the system prompt (see [`ide-integration.md`](ide-integration.md)). Then ask anything in Greek or English:

- *"Δείξε μου ένα παράδειγμα Dynamic Programming από τα slides."*
- *"What's the recurrence for Mergesort and how do I solve it with the Master Theorem?"*
- *"Walk me through exercise 3 of Final-2024."*

The tutor will cite specific kb files and only open images when they add value.

## Updating an existing subject

Drop new PDFs into the appropriate `raw/<category>/` folder and run:

```bash
python tools/regenerate.py --subject algorithms
```

Then ask `image-curator` to curate any new images and `tutor-generator` to refresh the tutor (it will read the new kb files and rewrite the topic index).

To rebuild from scratch without touching curated images:

```bash
python tools/regenerate.py --subject algorithms --keep-assets
```

## Removing a subject

Delete `subjects/<slug>/`. The repository does not track any subject-specific state outside that folder.

## Tips

- **Naming PDFs.** The script slugifies filenames for `kb/` and `assets/`, but it preserves them in `raw/`. Spaces and Greek characters are fine in source filenames; the kb side will still be ASCII.
- **Scanned PDFs.** `pypdf` only reads embedded text. If a PDF was scanned without OCR, the resulting Markdown will be mostly empty. Run an OCR pass on the original PDF first (e.g. `ocrmypdf`) and then regenerate.
- **Languages.** The tutor agent picks language at chat time from the user's message. The kb itself stays in whatever language the PDFs were in.
- **Working offline.** All scripts are local. The agents only talk to your AI assistant's model.
