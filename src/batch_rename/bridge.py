"""Python API exposed to the WebView JS frontend."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import webview

from . import rename, setlist


VIDEO_EXTENSIONS = {
    ".mov", ".mp4", ".m4v", ".mxf", ".avi", ".mkv",
    ".wav", ".aif", ".aiff", ".mp3", ".m4a", ".flac",
}


class API:
    """Methods here are callable from JS via window.pywebview.api.*"""

    def __init__(self) -> None:
        self._pending_pairs: list[tuple[Path, Path]] = []
        self._window: webview.Window | None = None

    def set_window(self, window: webview.Window) -> None:
        self._window = window

    # ------------------------------------------------------------------
    # File / folder pickers
    # ------------------------------------------------------------------

    def pick_file(self, filters: list[dict]) -> str | None:
        file_types = tuple(
            f"{f['name']} (*.{ext})"
            for f in filters
            for ext in f.get("extensions", [])
        )
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types,
        )
        return result[0] if result else None

    def pick_folder(self) -> str | None:
        result = self._window.create_file_dialog(webview.FOLDER_DIALOG)
        return result[0] if result else None

    # ------------------------------------------------------------------
    # Rename logic
    # ------------------------------------------------------------------

    def build_plan(
        self,
        program_path: str | None,
        fcpxml_path: str | None,
        clips_dir: str | None,
    ) -> dict[str, Any]:
        """Parse inputs and return a preview of (src_name, dst_name) pairs."""
        if not fcpxml_path or not clips_dir:
            return {"error": "FCPXML and clips folder are required."}

        # Collect clip files
        clips_folder = Path(clips_dir)
        files = [
            p for p in sorted(clips_folder.iterdir())
            if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
        ]
        if not files:
            return {"error": f"No video/audio files found in {clips_folder.name}."}

        # Get titles — from FCPXML clip names for now (program parsing comes later)
        try:
            from . import fcpxml as fcp
            clips = fcp.parse(Path(fcpxml_path))
            titles = [c.title for c in clips]
        except Exception as e:
            return {"error": f"Could not parse FCPXML: {e}"}

        try:
            pairs = rename.plan(files, titles)
        except ValueError as e:
            return {"error": str(e)}

        self._pending_pairs = pairs
        return {
            "pairs": [(src.name, dst.name) for src, dst in pairs]
        }

    def confirm_rename(self) -> dict[str, Any]:
        """Execute the pending rename plan."""
        if not self._pending_pairs:
            return {"error": "No pending rename plan."}
        try:
            rename.apply(self._pending_pairs, dry_run=False)
            count = len(self._pending_pairs)
            self._pending_pairs = []
            return {"count": count}
        except FileExistsError as e:
            return {"error": str(e)}
        except Exception as e:
            return {"error": str(e)}
