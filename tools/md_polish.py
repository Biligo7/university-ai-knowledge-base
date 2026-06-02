"""Visual polish pass run after ``format_md.py``.

This is the script half of the work that the ``md-formatter`` agent does
on Markdown files in ``subjects/<subject>/kb/``. Where ``format_md.py`` is
the heuristic formatter (bullets, blank lines, footers), this script
applies the small idempotent fixes that don't need human judgement:

* Bolds marker words at the start of a line:
  Υπόδειξη, Απάντηση, Σημείωση, Παρατήρηση, Hint, Answer, Note.
* Promotes obvious problem/exercise/example headers to ``###``:
  ``Πρόβλημα N.``, ``Άσκηση N.``, ``Παράδειγμα N`` (only when they are
  the entire line, optionally with a ``(N μονάδες)`` tag).
* Replaces a handful of PDF-extraction glyphs that hurt readability
  without context (``…`` → ``...``, fancy quotes → ``"``).

Everything else (heading promotion for slide titles, fencing pseudocode)
needs human judgement and stays out of this script.

Usage:
    python tools/md_polish.py --md path/to/file.md
    python tools/md_polish.py --dir subjects/<subject>/kb

Both flags accept multiple values; ``--dir`` recurses into subfolders.
The script reports each file it touched and the number of edits per
category. Running it twice on the same file is a no-op.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path


MARKER_WORDS = (
    "Υπόδειξη",
    "Απάντηση",
    "Σημείωση",
    "Παρατήρηση",
    "Hint",
    "Answer",
    "Note",
)


MARKER_RE = re.compile(
    r"^(?P<word>" + "|".join(MARKER_WORDS) + r")(?P<punct>[.:])(?P<tail>\s|$)",
    flags=re.MULTILINE,
)

PROBLIMA_RE = re.compile(
    r"^(?P<head>Πρόβλημα\s+\d+\.?(?:\s*\([^)\n]+\))?)\s*$",
    flags=re.MULTILINE,
)

# Same header glued to a body sentence on a single line, e.g.
# ``Πρόβλημα 2. (22 μονάδες) Θεωρήστε ...``. Split into heading + body.
PROBLIMA_GLUED_RE = re.compile(
    r"^(?P<head>Πρόβλημα\s+\d+\.?\s*\([^)\n]+\))\s+(?P<body>\S.+)$",
    flags=re.MULTILINE,
)

ASKISI_RE = re.compile(
    r"^(?P<head>Άσκηση\s+\d+\.?(?:\s*\([^)\n]+\))?)\s*$",
    flags=re.MULTILINE,
)

ASKISI_GLUED_RE = re.compile(
    r"^(?P<head>Άσκηση\s+\d+\.?\s*\([^)\n]+\))\s+(?P<body>\S.+)$",
    flags=re.MULTILINE,
)

PARADEIGMA_RE = re.compile(
    r"^(?P<head>Παράδειγμα\s+\d+)(?:[:.])?\s*$",
    flags=re.MULTILINE,
)

# Course-section headings, e.g. ``Ενότητα 02 (Asymptotic growth):`` or
# ``Ενότητες 07-08 (Greedy):`` — only when the line is just the heading.
ENOTITA_RE = re.compile(
    r"^(?P<head>Ενότητες?\s+\d+(?:-\d+)?\s*\([^)\n]+\):?)\s*$",
    flags=re.MULTILINE,
)

MOJIBAKE = (
    ("…", "..."),
    ("“", '"'),
    ("”", '"'),
)


@dataclass
class Stats:
    markers: int = 0
    problems: int = 0
    askiseis: int = 0
    paradeigmata: int = 0
    enotites: int = 0
    glyphs: int = 0
    spacing: int = 0

    def touched(self) -> bool:
        return any(
            (
                self.markers,
                self.problems,
                self.askiseis,
                self.paradeigmata,
                self.enotites,
                self.glyphs,
                self.spacing,
            )
        )

    def summary(self) -> str:
        parts: list[str] = []
        if self.markers:
            parts.append(f"{self.markers} marker(s) bolded")
        if self.problems:
            parts.append(f"{self.problems} Πρόβλημα heading(s)")
        if self.askiseis:
            parts.append(f"{self.askiseis} Άσκηση heading(s)")
        if self.paradeigmata:
            parts.append(f"{self.paradeigmata} Παράδειγμα heading(s)")
        if self.enotites:
            parts.append(f"{self.enotites} Ενότητα heading(s)")
        if self.glyphs:
            parts.append(f"{self.glyphs} glyph fix(es)")
        if self.spacing:
            parts.append(f"{self.spacing} heading spacing fix(es)")
        return ", ".join(parts) if parts else "no changes"


def bold_markers(text: str, stats: Stats) -> str:
    def repl(match: re.Match[str]) -> str:
        stats.markers += 1
        return f"**{match.group('word')}{match.group('punct')}**{match.group('tail')}"

    return MARKER_RE.sub(repl, text)


def promote_problems(text: str, stats: Stats) -> str:
    def repl(match: re.Match[str]) -> str:
        stats.problems += 1
        return f"### {match.group('head')}"

    text = PROBLIMA_RE.sub(repl, text)

    def split_repl(match: re.Match[str]) -> str:
        stats.problems += 1
        return f"### {match.group('head')}\n\n{match.group('body')}"

    return PROBLIMA_GLUED_RE.sub(split_repl, text)


def promote_askiseis(text: str, stats: Stats) -> str:
    def repl(match: re.Match[str]) -> str:
        stats.askiseis += 1
        return f"### {match.group('head')}"

    text = ASKISI_RE.sub(repl, text)

    def split_repl(match: re.Match[str]) -> str:
        stats.askiseis += 1
        return f"### {match.group('head')}\n\n{match.group('body')}"

    return ASKISI_GLUED_RE.sub(split_repl, text)


def promote_paradeigmata(text: str, stats: Stats) -> str:
    def repl(match: re.Match[str]) -> str:
        stats.paradeigmata += 1
        return f"### {match.group('head')}"

    return PARADEIGMA_RE.sub(repl, text)


def promote_enotites(text: str, stats: Stats) -> str:
    def repl(match: re.Match[str]) -> str:
        stats.enotites += 1
        return f"### {match.group('head')}"

    return ENOTITA_RE.sub(repl, text)


def fix_glyphs(text: str, stats: Stats) -> str:
    for src, dst in MOJIBAKE:
        count = text.count(src)
        if count:
            text = text.replace(src, dst)
            stats.glyphs += count
    return text


def ensure_heading_spacing(text: str, stats: Stats) -> str:
    """Make sure every ``### `` line has a blank line before and after.

    Idempotent: once the surrounding lines are blank, nothing changes.
    """
    lines = text.split("\n")
    out: list[str] = []
    for line in lines:
        if line.startswith("### ") and out and out[-1].strip() != "":
            out.append("")
            stats.spacing += 1
        out.append(line)

    result: list[str] = []
    for i, line in enumerate(out):
        result.append(line)
        if line.startswith("### "):
            if i + 1 < len(out) and out[i + 1].strip() != "":
                result.append("")
                stats.spacing += 1
    return "\n".join(result)


def polish(text: str) -> tuple[str, Stats]:
    stats = Stats()
    text = bold_markers(text, stats)
    text = promote_problems(text, stats)
    text = promote_askiseis(text, stats)
    text = promote_paradeigmata(text, stats)
    text = promote_enotites(text, stats)
    text = fix_glyphs(text, stats)
    text = ensure_heading_spacing(text, stats)
    return text, stats


def process_file(path: Path) -> Stats:
    original = path.read_text(encoding="utf-8")
    new_text, stats = polish(original)
    if stats.touched() and new_text != original:
        path.write_text(new_text, encoding="utf-8")
    return stats


def iter_md_files(targets: list[Path]) -> list[Path]:
    out: list[Path] = []
    for t in targets:
        if t.is_file():
            if t.suffix.lower() == ".md":
                out.append(t)
        elif t.is_dir():
            out.extend(sorted(t.rglob("*.md")))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--md", action="append", default=[], help="single .md file")
    parser.add_argument(
        "--dir",
        action="append",
        default=[],
        help="directory; .md files are processed recursively",
    )
    args = parser.parse_args()

    if not args.md and not args.dir:
        parser.error("provide at least one --md or --dir")

    targets = [Path(p) for p in (*args.md, *args.dir)]
    files = iter_md_files(targets)

    if not files:
        print("No Markdown files found.")
        return 1

    touched = 0
    for f in files:
        stats = process_file(f)
        if stats.touched():
            touched += 1
            print(f"{f}: {stats.summary()}")
        else:
            print(f"{f}: no changes")

    print(f"\n{touched}/{len(files)} files touched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
