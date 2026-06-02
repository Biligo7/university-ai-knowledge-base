# tools/

Cross-platform Python scripts that do the mechanical work of the pipeline. The agents under [`../agents/`](../agents) call these scripts.

| Script | Purpose |
|---|---|
| [`init_subject.py`](init_subject.py) | Create the folder skeleton for a new subject from the templates. |
| [`pdf_to_md.py`](pdf_to_md.py) | Convert a single PDF to Markdown and extract its embedded images. |
| [`format_md.py`](format_md.py) | Normalise Markdown produced by the converter (bullets, blank lines, footers). |
| [`filter_images.py`](filter_images.py) | Drop tiny or repeated images (logos, watermarks) and prune dead MD references. |
| [`regenerate.py`](regenerate.py) | Wipe a subject's `kb/` and `assets/` and rebuild from `raw/`. |

All scripts work on Windows, macOS and Linux as long as the Python deps in [`../requirements.txt`](../requirements.txt) are installed:

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Each script has its own `--help`. The pipeline used by the initializer agent is:

```text
init_subject.py            -->   creates subjects/<slug>/
(copy PDFs into raw/)
regenerate.py              -->   pdf_to_md.py per PDF, then format_md.py
filter_images.py --apply   -->   mechanical image cleanup
(image-curator agent)      -->   intelligent image curation with vision
(md-formatter agent)       -->   visual MD review pass
(tutor-generator agent)    -->   writes subjects/<slug>/agents/tutor.md
```
