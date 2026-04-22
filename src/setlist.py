"""Parse a plain-text setlist into an ordered list of (shortcode, title) pairs.

Supported shortcode formats:
    01      simple number
    07a     number + letter suffix
    08-1    number + dash + number (multiple camera angles)

Lines starting with ; are comments. folderPrefix lines are ignored (future use).
"""

from __future__ import annotations

import re
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Entry:
    shortcode: str  # e.g. "07a", "08-1", "01"
    title: str


_COMMENT = re.compile(r"^\s*;")
_FOLDER_PREFIX = re.compile(r"^\s*folderPrefix\s*=", re.IGNORECASE)
_ENTRY = re.compile(r"^\s*(\d+[a-zA-Z0-9](?:-\d+)?|\d+[a-zA-Z]?)\s+(.+)$")


def parse(path: Path) -> list[Entry]:
    """Return ordered list of entries from *path*."""
    entries: list[Entry] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or _COMMENT.match(line) or _FOLDER_PREFIX.match(line):
            continue
        m = _ENTRY.match(line)
        if not m:
            raise ValueError(
                f"{path}:{lineno}: cannot parse setlist entry: {raw!r}\n"
                "Expected format: '01 Title' or '07a Title' or '08-1 Title'"
            )
        entries.append(Entry(shortcode=m.group(1).strip(), title=m.group(2).strip()))
    if not entries:
        raise ValueError(f"{path}: setlist is empty")
    return entries


def titles(path: Path) -> list[str]:
    """Convenience wrapper returning just the title strings in order."""
    return [e.title for e in parse(path)]
