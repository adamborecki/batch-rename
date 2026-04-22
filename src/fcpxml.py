"""Parse an FCPXML file and extract clip titles in timeline order.

Only spine-level clips (asset-clip, ref-clip, sync-clip, mc-clip, gap, title)
that appear directly on the primary storyline are returned. Nested clips,
B-roll, and connected clips are ignored.

Returns a list of ClipInfo dataclasses ordered by timeline offset.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


@dataclass
class ClipInfo:
    title: str
    offset: Fraction   # seconds from sequence start
    duration: Fraction # seconds


def _rational(value: str) -> Fraction:
    """Convert an FCPXML rational time string like '1001/30000s' to seconds."""
    s = value.rstrip("s")
    if "/" in s:
        num, den = s.split("/")
        return Fraction(int(num), int(den))
    return Fraction(int(s))


_CLIP_TAGS = {
    "asset-clip", "ref-clip", "sync-clip", "mc-clip", "clip", "title"
}


def _clip_title(el: ET.Element) -> str:
    return el.get("name") or el.get("ref") or el.tag


def _spine_clips(spine: ET.Element) -> list[ClipInfo]:
    clips: list[ClipInfo] = []
    for child in spine:
        if child.tag in _CLIP_TAGS:
            offset_str = child.get("offset", "0s")
            dur_str = child.get("duration", "0s")
            clips.append(ClipInfo(
                title=_clip_title(child),
                offset=_rational(offset_str),
                duration=_rational(dur_str),
            ))
    clips.sort(key=lambda c: c.offset)
    return clips


def parse(path: Path) -> list[ClipInfo]:
    """Return primary-storyline clips from *path* in timeline order."""
    tree = ET.parse(path)
    root = tree.getroot()

    # FCPXML wraps content in <library> > <event> > <project> > <sequence> > <spine>
    # but we search broadly so nested formats still work.
    spines = root.findall(".//sequence/spine")
    if not spines:
        raise ValueError(f"{path}: no <spine> found — is this a valid FCPXML file?")

    # Use the first (primary) spine
    return _spine_clips(spines[0])
