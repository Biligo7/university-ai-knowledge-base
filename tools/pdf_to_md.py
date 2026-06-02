"""Convert a single PDF to a Markdown file and extract embedded images.

Usage:
    python tools/pdf_to_md.py \
        --pdf path/to/file.pdf \
        --out-md subjects/<subject>/kb/slides/01-intro.md \
        --assets-dir subjects/<subject>/assets/01-intro \
        [--title "Lecture 01 - Intro"] \
        [--min-image-bytes 2048] \
        [--max-repeat 2]

What it does
------------
* Extracts text page by page and writes a Markdown file with one
  ``## Page N`` heading per page.
* Strips control characters that some PDFs embed in their text streams.
* Extracts embedded images per page into ``--assets-dir`` as
  ``p<NN>-i<NN>.<ext>``.
* Drops images smaller than ``--min-image-bytes`` (defaults to 2 KiB) — these
  are usually decorative slivers, bullets, watermarks.
* Drops images whose binary hash appears on more than ``--max-repeat`` pages
  (defaults to 2) — those are typically page templates / footers / logos.
* Appends Markdown image references at the end of the page section that the
  image came from.

The script is intentionally simple. Heavier curation (deciding whether an
image carries pedagogical value) is the job of the ``image-curator`` agent
that runs after this script.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import unicodedata
from collections import Counter
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError as exc:  # pragma: no cover
    sys.stderr.write(
        "pypdf is required. Install with: pip install -r requirements.txt\n"
    )
    raise SystemExit(1) from exc


def strip_control_chars(text: str) -> str:
    """Drop control characters that break some Markdown viewers/parsers."""
    out: list[str] = []
    for ch in text:
        if ch in ("\n", "\t"):
            out.append(ch)
            continue
        if ch == "\r":
            continue
        category = unicodedata.category(ch)
        if category.startswith("C"):
            continue
        out.append(ch)
    return "".join(out)


def safe_image_extension(name: str, data: bytes) -> str:
    suffix = Path(name).suffix.lower().lstrip(".")
    if suffix in {"png", "jpg", "jpeg", "gif", "bmp", "tif", "tiff", "webp"}:
        return "jpg" if suffix == "jpeg" else suffix
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"GIF8"):
        return "gif"
    return "bin"


def extract_pdf(
    pdf_path: Path,
    out_md: Path,
    assets_dir: Path,
    title: str,
    min_image_bytes: int,
    max_repeat: int,
) -> None:
    reader = PdfReader(str(pdf_path))
    pages = reader.pages

    # First pass: collect all images so we can detect repeats across pages.
    page_images: list[list[tuple[str, bytes]]] = []
    hash_pages: dict[str, set[int]] = {}

    for page_index, page in enumerate(pages, start=1):
        images_on_page: list[tuple[str, bytes]] = []
        try:
            embedded = list(page.images)
        except Exception:
            embedded = []
        for img in embedded:
            data = img.data
            if not data:
                continue
            digest = hashlib.sha1(data).hexdigest()
            hash_pages.setdefault(digest, set()).add(page_index)
            images_on_page.append((img.name or "", data))
        page_images.append(images_on_page)

    repeating_hashes = {
        digest for digest, pages_seen in hash_pages.items() if len(pages_seen) > max_repeat
    }

    assets_dir.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    parts: list[str] = [f"# {title}", ""]
    parts.append(f"_Source: `{pdf_path.name}`_")
    parts.append(f"_Pages: {len(pages)}_")
    parts.append("")
    parts.append("---")
    parts.append("")

    saved_per_page_counter: Counter[int] = Counter()

    for page_index, (page, images_on_page) in enumerate(
        zip(pages, page_images), start=1
    ):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # pragma: no cover
            text = f"[text extraction error: {exc}]"
        text = strip_control_chars(text).rstrip()

        parts.append(f"## Page {page_index}")
        parts.append("")
        if text:
            parts.append(text)
            parts.append("")

        image_refs: list[str] = []
        for name, data in images_on_page:
            if len(data) < min_image_bytes:
                continue
            digest = hashlib.sha1(data).hexdigest()
            if digest in repeating_hashes:
                continue
            saved_per_page_counter[page_index] += 1
            ext = safe_image_extension(name, data)
            fname = f"p{page_index:03d}-i{saved_per_page_counter[page_index]:02d}.{ext}"
            target = assets_dir / fname
            target.write_bytes(data)
            rel = _relative_asset_path(out_md.parent, target)
            image_refs.append(f"![Page {page_index} image]({rel})")

        if image_refs:
            parts.extend(image_refs)
            parts.append("")

    out_md.write_text("\n".join(parts), encoding="utf-8")


def _relative_asset_path(md_dir: Path, asset_path: Path) -> str:
    """Build a forward-slash relative path that works in Markdown on all OSes."""
    try:
        rel = asset_path.resolve().relative_to(md_dir.resolve())
    except ValueError:
        import os

        rel = Path(os.path.relpath(asset_path.resolve(), md_dir.resolve()))
    return rel.as_posix()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pdf", required=True, type=Path, help="Input PDF path")
    parser.add_argument("--out-md", required=True, type=Path, help="Output Markdown path")
    parser.add_argument(
        "--assets-dir",
        required=True,
        type=Path,
        help="Where to write extracted images for this PDF",
    )
    parser.add_argument("--title", default=None, help="H1 title (defaults to PDF stem)")
    parser.add_argument(
        "--min-image-bytes",
        type=int,
        default=2048,
        help="Drop images smaller than this size in bytes (default: 2048)",
    )
    parser.add_argument(
        "--max-repeat",
        type=int,
        default=2,
        help="Drop images whose hash appears on more than N pages (default: 2)",
    )
    args = parser.parse_args()

    title = args.title or args.pdf.stem
    extract_pdf(
        pdf_path=args.pdf,
        out_md=args.out_md,
        assets_dir=args.assets_dir,
        title=title,
        min_image_bytes=args.min_image_bytes,
        max_repeat=args.max_repeat,
    )
    print(f"Wrote {args.out_md} and images under {args.assets_dir}")


if __name__ == "__main__":
    main()
