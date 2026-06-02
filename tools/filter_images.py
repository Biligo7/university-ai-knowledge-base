"""Heuristic image filter for the per-PDF asset folders.

Usage:
    python tools/filter_images.py --assets-dir subjects/<subject>/assets
    python tools/filter_images.py --assets-dir subjects/<subject>/assets --apply

What it does
------------
* Walks every PDF asset subfolder.
* Lists images that look mechanically uninteresting:
    - smaller than ``--min-bytes`` (default 2048).
    - whose binary hash appears more than ``--max-repeats`` times across the
      same subject (default 3) — typically logos, watermarks, page templates.
* Without ``--apply`` the script only prints the candidates (dry run).
* With ``--apply`` the script:
    - deletes those image files,
    - walks every ``.md`` file under ``subjects/<subject>/kb`` and removes
      Markdown image references that no longer resolve.

This script handles only mechanical filtering. Pedagogical curation
(deciding whether a graph, table, or trace is worth keeping) is the job of
the ``image-curator`` agent that reads images with vision.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from collections import defaultdict
from pathlib import Path

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def list_images(assets_dir: Path) -> list[Path]:
    return sorted(
        p for p in assets_dir.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )


def find_candidates(
    assets_dir: Path, min_bytes: int, max_repeats: int
) -> tuple[list[Path], list[Path]]:
    images = list_images(assets_dir)
    tiny = [p for p in images if p.stat().st_size < min_bytes]
    hash_paths: dict[str, list[Path]] = defaultdict(list)
    for p in images:
        digest = hashlib.sha1(p.read_bytes()).hexdigest()
        hash_paths[digest].append(p)
    repeated: list[Path] = []
    for paths in hash_paths.values():
        if len(paths) > max_repeats:
            repeated.extend(paths)
    return tiny, repeated


def strip_dead_image_refs(kb_dir: Path) -> None:
    if not kb_dir.exists():
        return
    for md in kb_dir.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        kept_lines: list[str] = []
        changed = False
        for line in text.splitlines():
            match = MD_IMAGE_RE.search(line.strip())
            if match and line.strip().startswith("!["):
                target = (md.parent / match.group(1)).resolve()
                if not target.exists():
                    changed = True
                    continue
            kept_lines.append(line)
        if changed:
            md.write_text("\n".join(kept_lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--assets-dir",
        required=True,
        type=Path,
        help="Path to subjects/<subject>/assets",
    )
    parser.add_argument(
        "--kb-dir",
        type=Path,
        default=None,
        help="Path to subjects/<subject>/kb (defaults to ../kb relative to assets)",
    )
    parser.add_argument("--min-bytes", type=int, default=2048)
    parser.add_argument("--max-repeats", type=int, default=3)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually delete the candidate files and strip dead MD references",
    )
    args = parser.parse_args()

    kb_dir = args.kb_dir or (args.assets_dir.parent / "kb")

    tiny, repeated = find_candidates(args.assets_dir, args.min_bytes, args.max_repeats)
    candidates = sorted(set(tiny) | set(repeated))

    if not candidates:
        print("No candidates found.")
        return

    print(f"Found {len(candidates)} candidate image(s) to drop:")
    for p in candidates:
        reasons = []
        if p in tiny:
            reasons.append(f"<{args.min_bytes}B")
        if p in repeated:
            reasons.append(f"repeats >{args.max_repeats}")
        print(f"  {p}  [{', '.join(reasons)}]")

    if not args.apply:
        print("\nDry run only. Re-run with --apply to delete them.")
        return

    for p in candidates:
        try:
            p.unlink()
        except FileNotFoundError:
            pass
    strip_dead_image_refs(kb_dir)
    print(f"\nDeleted {len(candidates)} image(s) and cleaned MD references in {kb_dir}.")


if __name__ == "__main__":
    main()
