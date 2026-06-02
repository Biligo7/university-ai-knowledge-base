"""Lightweight Markdown formatter for files produced by ``pdf_to_md.py``.

Usage:
    python tools/format_md.py --md path/to/file.md
    python tools/format_md.py --dir subjects/<subject>/kb

What it does
------------
* Strips trailing whitespace on every line.
* Normalises common bullet-marker glyphs (•, ●, ●, ◦, ▪, ➢, –, —) to
  ``-`` Markdown list syntax.
* Collapses runs of blank lines to a single blank line.
* Joins obvious bullet continuations (a line that starts with a lowercase
  letter or an opening parenthesis is glued onto the previous bullet).
* Removes lone page-number lines that the extractor left behind on slides.
* Drops short, highly repeated lines that are clearly slide-deck footers
  (visible on at least 40% of pages, 4-32 chars long).

The formatter is intentionally conservative — it does not rewrite content,
add headings, or guess pseudocode. The ``md-formatter`` agent does a visual
review afterwards and can apply richer edits if it sees something the script
missed.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


BULLET_PREFIXES = ("•", "●", "◦", "▪", "▫", "■", "□", "➢", "►", "·", "–", "—")
SENTENCE_END = (".", "?", "!", ":", ";", "·")
PAGE_HEADING_RE = re.compile(r"^##\s+Page\s+\d+\s*$")
PAGE_NUMBER_LINE_RE = re.compile(r"^\s*\d{1,3}\s*$")


def normalise_bullets(line: str) -> str:
    stripped = line.lstrip()
    leading = line[: len(line) - len(stripped)]
    for marker in BULLET_PREFIXES:
        if stripped.startswith(marker + " "):
            return f"{leading}- {stripped[len(marker) + 1 :]}"
        if stripped.startswith(marker):
            return f"{leading}- {stripped[len(marker):].lstrip()}"
    return line


def join_bullet_continuations(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        cur = lines[i]
        if re.match(r"^\s*-\s+\S", cur):
            j = i + 1
            while j < len(lines):
                nxt = lines[j]
                stripped = nxt.strip()
                if not stripped:
                    break
                if stripped.startswith(("- ", "#", "![", ">", "**", "```", "|")):
                    break
                starts_lower_or_paren = bool(re.match(r"^[a-zα-ω(]", stripped))
                prev_open = (
                    not cur.rstrip().endswith(SENTENCE_END)
                    and stripped[0].isalpha()
                )
                if not (starts_lower_or_paren or prev_open):
                    break
                cur = cur.rstrip() + " " + stripped
                j += 1
            out.append(cur)
            i = j
            continue
        out.append(cur)
        i += 1
    return out


def detect_repeated_footers(pages: list[list[str]]) -> set[str]:
    counts: Counter[str] = Counter()
    for page in pages:
        seen = set()
        for raw in page:
            line = raw.strip()
            if 4 <= len(line) <= 32 and not line.startswith(("#", "-", "!", "|", ">", "```")):
                seen.add(line)
        counts.update(seen)
    threshold = max(2, int(0.4 * max(len(pages), 1)))
    return {line for line, count in counts.items() if count >= threshold}


def split_into_pages(lines: list[str]) -> list[tuple[str | None, list[str]]]:
    """Return [(page_heading_or_None, body_lines), ...]. First chunk is preamble."""
    sections: list[tuple[str | None, list[str]]] = []
    current_heading: str | None = None
    current_body: list[str] = []
    for line in lines:
        if PAGE_HEADING_RE.match(line):
            sections.append((current_heading, current_body))
            current_heading = line
            current_body = []
        else:
            current_body.append(line)
    sections.append((current_heading, current_body))
    return sections


def collapse_blank_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    blank = False
    for line in lines:
        if line.strip() == "":
            if not blank:
                out.append("")
            blank = True
        else:
            out.append(line)
            blank = False
    while out and out[-1] == "":
        out.pop()
    out.append("")
    return out


def format_text(text: str) -> str:
    raw_lines = [ln.rstrip() for ln in text.splitlines()]
    raw_lines = [normalise_bullets(ln) for ln in raw_lines]

    sections = split_into_pages(raw_lines)
    page_bodies = [body for heading, body in sections if heading is not None]
    footer_lines = detect_repeated_footers(page_bodies)

    cleaned_sections: list[list[str]] = []
    for heading, body in sections:
        filtered: list[str] = []
        for line in body:
            stripped = line.strip()
            if stripped in footer_lines:
                continue
            if heading is not None and PAGE_NUMBER_LINE_RE.match(line):
                continue
            filtered.append(line)
        filtered = join_bullet_continuations(filtered)
        if heading is not None:
            cleaned_sections.append([heading, ""] + filtered)
        else:
            cleaned_sections.append(filtered)

    merged: list[str] = []
    for chunk in cleaned_sections:
        merged.extend(chunk)
        merged.append("")

    merged = collapse_blank_lines(merged)
    return "\n".join(merged)


def format_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    new_text = format_text(text)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        print(f"Formatted {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--md", type=Path, help="Single Markdown file to format")
    group.add_argument(
        "--dir",
        type=Path,
        help="Directory to walk recursively; every .md file is formatted",
    )
    args = parser.parse_args()

    if args.md:
        format_file(args.md)
    else:
        for path in sorted(args.dir.rglob("*.md")):
            format_file(path)


if __name__ == "__main__":
    main()
