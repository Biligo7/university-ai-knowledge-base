"""Create the folder skeleton for a new subject.

Usage:
    python tools/init_subject.py --name "Algorithms"
    python tools/init_subject.py --name "Linear Algebra" --slug linear-algebra
    python tools/init_subject.py --name "Algorithms" --categories slides exams general labs

What it does
------------
* Slugifies the subject name (lowercase, hyphens) unless ``--slug`` is given.
* Creates ``subjects/<slug>/`` with the standard layout:

      subjects/<slug>/
      ├── README.md
      ├── agents/
      │   └── README.md
      ├── assets/
      │   └── README.md
      ├── kb/
      │   ├── README.md
      │   └── <category>/  (one per --categories entry)
      └── raw/
          ├── README.md
          └── <category>/  (one per --categories entry)

* Copies and templates the README files from ``templates/subject/``.
* Refuses to overwrite an existing subject unless ``--force`` is passed.
"""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

DEFAULT_CATEGORIES = ["general", "slides", "exams"]
REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = REPO_ROOT / "templates" / "subject"


def slugify(name: str) -> str:
    value = name.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "subject"


def render(template_text: str, *, subject_name: str, slug: str, categories: list[str]) -> str:
    categories_list = "\n".join(f"- `{c}/`" for c in categories)
    return (
        template_text.replace("{{SUBJECT_NAME}}", subject_name)
        .replace("{{SUBJECT_SLUG}}", slug)
        .replace("{{CATEGORIES_LIST}}", categories_list)
    )


def copy_template_file(
    src: Path, dst: Path, *, subject_name: str, slug: str, categories: list[str]
) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix.lower() == ".md":
        text = src.read_text(encoding="utf-8")
        dst.write_text(
            render(text, subject_name=subject_name, slug=slug, categories=categories),
            encoding="utf-8",
        )
    else:
        shutil.copy2(src, dst)


def create_subject(name: str, slug: str, categories: list[str], force: bool) -> Path:
    subject_dir = REPO_ROOT / "subjects" / slug
    if subject_dir.exists() and not force:
        raise SystemExit(
            f"Subject already exists at {subject_dir}. Pass --force to overwrite README files."
        )

    if not TEMPLATE_DIR.exists():
        raise SystemExit(
            f"Missing template directory: {TEMPLATE_DIR}. "
            "Run this script from a fresh clone of the template repo."
        )

    for sub in ("agents", "assets", "kb", "raw"):
        (subject_dir / sub).mkdir(parents=True, exist_ok=True)

    for category in categories:
        (subject_dir / "kb" / category).mkdir(parents=True, exist_ok=True)
        (subject_dir / "raw" / category).mkdir(parents=True, exist_ok=True)
        keep_kb = subject_dir / "kb" / category / ".gitkeep"
        keep_raw = subject_dir / "raw" / category / ".gitkeep"
        if not keep_kb.exists():
            keep_kb.touch()
        if not keep_raw.exists():
            keep_raw.touch()

    for tmpl in TEMPLATE_DIR.rglob("*"):
        if tmpl.is_dir():
            continue
        rel = tmpl.relative_to(TEMPLATE_DIR)
        if rel.name == ".gitkeep":
            continue
        copy_template_file(
            tmpl,
            subject_dir / rel,
            subject_name=name,
            slug=slug,
            categories=categories,
        )

    return subject_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--name", required=True, help="Human-readable subject name")
    parser.add_argument("--slug", default=None, help="Folder name (defaults to slugified name)")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=DEFAULT_CATEGORIES,
        help=f"Category subfolders to create (default: {' '.join(DEFAULT_CATEGORIES)})",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing README files")
    args = parser.parse_args()

    slug = args.slug or slugify(args.name)
    subject_dir = create_subject(args.name, slug, args.categories, args.force)
    print(f"Created subject scaffold at {subject_dir}")
    print("Next steps:")
    print(f"  1. Drop your PDFs into raw/<category>/ inside {subject_dir}")
    print("  2. Run tools/regenerate.py --subject", slug)
    print("  3. Ask the image-curator and tutor-generator agents to finish the job")


if __name__ == "__main__":
    main()
