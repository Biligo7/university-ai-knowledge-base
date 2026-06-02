"""Wipe and rebuild the Markdown + assets for one subject from its raw/ PDFs.

Usage:
    python tools/regenerate.py --subject algorithms
    python tools/regenerate.py --subject algorithms --keep-assets

What it does
------------
* Locates ``subjects/<subject>/raw/`` and iterates every PDF inside each
  category subfolder (``slides/``, ``exams/``, ``general/``, ...).
* Clears ``subjects/<subject>/kb/`` (preserving READMEs and ``.gitkeep``).
* Optionally clears ``subjects/<subject>/assets/`` (default behaviour;
  pass ``--keep-assets`` to keep curated images intact).
* Runs ``pdf_to_md.py`` for every PDF, producing one ``.md`` under the
  matching category in ``kb/`` and an assets subfolder named after the PDF.
* Runs ``format_md.py`` on the whole ``kb/`` afterwards.

This is the safe way to re-run the pipeline after you have added or
removed PDFs in ``raw/``.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
PRESERVED_NAMES = {"README.md", ".gitkeep"}


def slugify_filename(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in name)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def wipe_dir(root: Path) -> None:
    if not root.exists():
        return
    for entry in root.iterdir():
        if entry.name in PRESERVED_NAMES:
            continue
        if entry.is_dir():
            for nested in entry.rglob("*"):
                if nested.is_file() and nested.name in PRESERVED_NAMES:
                    continue
            shutil.rmtree(entry, ignore_errors=True)
        else:
            entry.unlink()


def run(cmd: list[str]) -> None:
    print("$", " ".join(cmd))
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        sys.exit(result.returncode)


def regenerate(subject_slug: str, keep_assets: bool) -> None:
    subject_dir = REPO_ROOT / "subjects" / subject_slug
    raw_dir = subject_dir / "raw"
    kb_dir = subject_dir / "kb"
    assets_dir = subject_dir / "assets"

    if not raw_dir.exists():
        raise SystemExit(f"Missing raw/ directory at {raw_dir}")

    for category_dir in sorted(p for p in raw_dir.iterdir() if p.is_dir()):
        kb_target = kb_dir / category_dir.name
        wipe_dir(kb_target)
        kb_target.mkdir(parents=True, exist_ok=True)

    if not keep_assets:
        wipe_dir(assets_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(raw_dir.rglob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found under {raw_dir}.")
        return

    for pdf in pdfs:
        category = pdf.parent.name
        stem = slugify_filename(pdf.stem)
        out_md = kb_dir / category / f"{stem}.md"
        per_pdf_assets = assets_dir / stem
        run(
            [
                sys.executable,
                str(TOOLS_DIR / "pdf_to_md.py"),
                "--pdf",
                str(pdf),
                "--out-md",
                str(out_md),
                "--assets-dir",
                str(per_pdf_assets),
                "--title",
                pdf.stem,
            ]
        )

    run([sys.executable, str(TOOLS_DIR / "format_md.py"), "--dir", str(kb_dir)])
    print(f"\nDone. Subject regenerated at {subject_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--subject", required=True, help="Subject slug (folder name under subjects/)")
    parser.add_argument(
        "--keep-assets",
        action="store_true",
        help="Do not wipe the assets/ folder before re-extracting",
    )
    args = parser.parse_args()
    regenerate(args.subject, args.keep_assets)


if __name__ == "__main__":
    main()
