"""Parse a plain-text setlist into an ordered list of piece titles.

Setlist format (one entry per line):
    01 Strauss - Don Juan, Op. 20
    02 Sibelius - Swan of Tuonela
    ; this is a comment and is ignored

The leading number/shortcode is stripped; only the title is returned.
"""

from __future__ import annotations

import re
from pathlib import Path


_COMMENT = re.compile(r"^\s*;")
_ENTRY = re.compile(r"^\s*\d+[a-zA-Z]?\s+(.+)$")


def parse(path: Path) -> list[str]:
    """Return ordered list of piece titles from *path*."""
    titles: list[str] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or _COMMENT.match(line):
            continue
        m = _ENTRY.match(line)
        if not m:
            raise ValueError(
                f"{path}:{lineno}: cannot parse setlist entry: {raw!r}\n"
                "Expected format: '01 Title of Piece'"
            )
        titles.append(m.group(1).strip())
    if not titles:
        raise ValueError(f"{path}: setlist is empty")
    return titles
