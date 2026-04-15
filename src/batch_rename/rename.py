"""Match exported files to setlist titles and rename them.

Matching strategy
-----------------
Exported files are assumed to be named with a leading number that corresponds
to their position in the setlist (1-indexed). Examples that all match entry 3:

    003.mov
    3.mov
    clip 003.mov
    Sequence - 003.mov

If no numeric prefix can be found the files are sorted lexicographically and
matched positionally — this handles whatever sequential names FCP assigns.

The output filename is built as:  {index:02d} {title}{suffix}
e.g.  03 Dvořák - Violin Concerto in A minor.mov
"""

from __future__ import annotations

import re
from pathlib import Path


_LEADING_NUM = re.compile(r"(\d+)")


def _clip_index(name: str) -> int | None:
    m = _LEADING_NUM.search(name)
    return int(m.group(1)) if m else None


def _safe_filename(title: str) -> str:
    """Replace characters that are illegal on macOS/Windows."""
    replacements = {
        "/": "∕",
        ":": "：",
        "\\": "＼",
        "*": "＊",
        "?": "？",
        '"': "＂",
        "<": "＜",
        ">": "＞",
        "|": "｜",
    }
    for bad, good in replacements.items():
        title = title.replace(bad, good)
    return title


def plan(files: list[Path], titles: list[str]) -> list[tuple[Path, Path]]:
    """Return (src, dst) pairs without touching the filesystem.

    *files*  — exported clip files (any order)
    *titles* — ordered setlist titles (index 1 = titles[0])
    """
    if not files:
        raise ValueError("No files provided to rename.")

    # Try to sort by embedded number; fall back to lexicographic order.
    def sort_key(p: Path) -> tuple[int, str]:
        idx = _clip_index(p.stem)
        return (idx if idx is not None else 999999, p.name)

    sorted_files = sorted(files, key=sort_key)

    if len(sorted_files) != len(titles):
        raise ValueError(
            f"File count ({len(sorted_files)}) does not match "
            f"setlist entry count ({len(titles)}). "
            "Make sure every piece has exactly one exported clip."
        )

    pairs: list[tuple[Path, Path]] = []
    for i, (src, title) in enumerate(zip(sorted_files, titles), 1):
        safe_title = _safe_filename(title)
        dst_name = f"{i:02d} {safe_title}{src.suffix}"
        if len(dst_name) > 255:
            print(f"Warning: filename exceeds 255 characters and may fail on some "
                  f"filesystems:\n  {dst_name}")
        dst = src.parent / dst_name
        pairs.append((src, dst))
    return pairs


def apply(pairs: list[tuple[Path, Path]], dry_run: bool = False) -> None:
    """Execute the renames. Prints each operation."""
    for src, dst in pairs:
        if dry_run:
            print(f"  {src.name}  →  {dst.name}")
        else:
            if dst.exists() and dst != src:
                raise FileExistsError(
                    f"Destination already exists: {dst}\n"
                    "Rename or remove it before running again."
                )
            src.rename(dst)
            print(f"  {src.name}  →  {dst.name}")
