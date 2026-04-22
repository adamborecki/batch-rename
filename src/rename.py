"""Match exported files to setlist entries and rename them.

Matching strategy
-----------------
Each file's stem is checked for a leading shortcode that matches a setlist entry.
Shortcode matching is case-insensitive and strips leading zeros for comparison.

  07a.wav        matches setlist entry  "07a Title"
  08-1.mov       matches setlist entry  "08-1 Title"
  001.wav        matches setlist entry  "01 Title"
  clip 003.wav   matches setlist entry  "03 Title"

If shortcode matching fails (e.g. FCP generic names with no shortcodes),
files are sorted lexicographically and matched positionally.

Output filename: shortcode preserved from setlist + title + original extension
  07a L.V. Beethoven - String Quartet No. 14 - I. Adagio.wav
"""

from __future__ import annotations

import re
from pathlib import Path

try:
    from src.setlist import Entry
except ImportError:
    from setlist import Entry  # type: ignore


_SHORTCODE = re.compile(r"^(\d+[a-zA-Z]?(?:-\d+)?)")


def _extract_shortcode(stem: str) -> str | None:
    """Extract leading shortcode from a filename stem, stripping leading zeros."""
    m = _SHORTCODE.search(stem.strip())
    if not m:
        return None
    raw = m.group(1)
    # Normalize: strip leading zeros from the numeric part for comparison
    num_part = re.match(r"^(0*)(\d+)(.*)", raw)
    if num_part:
        return num_part.group(2) + num_part.group(3)
    return raw


def _normalize(shortcode: str) -> str:
    """Normalize a shortcode for comparison by stripping leading zeros."""
    m = re.match(r"^(0*)(\d+)(.*)", shortcode)
    if m:
        return m.group(2) + m.group(3)
    return shortcode


_CHANNEL_SUFFIX = re.compile(r"(\.[A-Za-z]{1,3}s?)(\.\w+)$")


def _split_channel_suffix(name: str) -> tuple[str, str]:
    """Split '01.L.wav' into stem '01' and full suffix '.L.wav'."""
    m = _CHANNEL_SUFFIX.search(name)
    if m:
        base = name[:m.start()]
        suffix = m.group(1) + m.group(2)
        return base, suffix
    p = Path(name)
    return p.stem, p.suffix


def _safe_filename(title: str) -> str:
    replacements = {
        "/": "∕", ":": "：", "\\": "＼", "*": "＊",
        "?": "？", '"': "＂", "<": "＜", ">": "＞", "|": "｜",
    }
    for bad, good in replacements.items():
        title = title.replace(bad, good)
    return title


def plan(files: list[Path], entries: list[Entry]) -> list[tuple[Path, Path]]:
    """Return (src, dst) pairs without touching the filesystem."""
    if not files:
        raise ValueError("No files provided to rename.")

    # Build a lookup: normalized shortcode → Entry
    entry_map = {_normalize(e.shortcode): e for e in entries}

    # Try shortcode matching first
    pairs: list[tuple[Path, Path]] = []
    unmatched: list[Path] = []

    for f in sorted(files):
        stem, suffix = _split_channel_suffix(f.name)
        code = _extract_shortcode(stem)
        entry = entry_map.get(code) if code else None
        if entry:
            safe_title = _safe_filename(entry.title)
            dst_name = f"{entry.shortcode} {safe_title}{suffix}"
            if len(dst_name) > 255:
                print(f"Warning: filename exceeds 255 chars:\n  {dst_name}")
            pairs.append((f, f.parent / dst_name))
        else:
            unmatched.append(f)

    # Fall back to positional matching for anything unmatched
    matched_codes = {_extract_shortcode(src.stem) for src, _ in pairs}
    remaining_entries = [e for e in entries if _normalize(e.shortcode) not in
                         {_normalize(c) for c in matched_codes if c}]

    if unmatched and remaining_entries:
        if len(unmatched) != len(remaining_entries):
            raise ValueError(
                f"{len(unmatched)} unmatched file(s) but {len(remaining_entries)} "
                "remaining setlist entries — counts don't match."
            )
        for f, entry in zip(sorted(unmatched), remaining_entries):
            safe_title = _safe_filename(entry.title)
            dst_name = f"{entry.shortcode} {safe_title}{f.suffix}"
            pairs.append((f, f.parent / dst_name))
    elif unmatched:
        names = ", ".join(f.name for f in unmatched)
        raise ValueError(f"Could not match files to setlist entries: {names}")

    pairs.sort(key=lambda p: p[0].name)
    return pairs


def apply(pairs: list[tuple[Path, Path]], dry_run: bool = False) -> None:
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
