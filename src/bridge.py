"""Python API exposed to the WebView JS frontend."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import webview

try:
    from src import rename, setlist
except ImportError:
    import rename, setlist  # type: ignore


VIDEO_EXTENSIONS = {
    ".mov", ".mp4", ".m4v", ".mxf", ".avi", ".mkv",
    ".wav", ".aif", ".aiff", ".mp3", ".m4a", ".flac",
}


class API:
    def __init__(self) -> None:
        self._pending_pairs: list[tuple[Path, Path]] = []
        self._window: webview.Window | None = None

    def set_window(self, window: webview.Window) -> None:
        self._window = window

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

    def build_plan(self, setlist_path: str, clips_dir: str) -> dict[str, Any]:
        try:
            entries = setlist.parse(Path(setlist_path))
        except ValueError as e:
            return {"error": str(e)}

        clips_folder = Path(clips_dir)
        files = [
            p for p in sorted(clips_folder.iterdir())
            if p.is_file() and p.suffix.lower() in VIDEO_EXTENSIONS
        ]
        if not files:
            return {"error": f"No video/audio files found in {clips_folder.name}."}

        try:
            pairs = rename.plan(files, entries)
        except ValueError as e:
            return {"error": str(e)}

        self._pending_pairs = pairs
        return {"pairs": [(src.name, dst.name) for src, dst in pairs]}

    def confirm_rename(self) -> dict[str, Any]:
        if not self._pending_pairs:
            return {"error": "No pending rename plan."}
        try:
            rename.apply(self._pending_pairs, dry_run=False)
            count = len(self._pending_pairs)
            self._pending_pairs = []
            return {"count": count}
        except (FileExistsError, Exception) as e:
            return {"error": str(e)}
